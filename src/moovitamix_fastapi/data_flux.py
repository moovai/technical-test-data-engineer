import json
import pandas as pd
import requests
import sys
import time

from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy import create_engine, Engine
from typing import Union

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.moovitamix_fastapi.models import Base


# Vu que rien de ces variables va changer et qu'ils vont tous être utilisés à plusieurs endroits, je les laisse comme
# des variables global
BASE_URL = 'http://127.0.0.1:8000'
ENDPOINTS = ['tracks', 'users', 'listen_history']
LOCAL_PATH = Path(__file__).resolve().parent.parent / 'data'
LOCAL_PATH.mkdir(parents=True, exist_ok=True)
DB_URL = f"sqlite:///{Path(__file__).resolve().parent.parent}/data/db.sqlite"


def create_db(db_url: str = DB_URL) -> Engine:
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

    return engine


def extract_data(endpoint: str) -> list[list[dict[str, any]]]:
    failed_requests = 0
    while failed_requests < 5:
        response = requests.get(f'{BASE_URL}/{endpoint}')
        if response.status_code == 200:
            break
        else:
            failed_requests += 1
            print(f'API request failed {failed_requests} time(s)... Trying again in 5 seconds.')
            time.sleep(0)

    if failed_requests == 5:
        raise requests.exceptions.RequestException('No response from API after 5 attempts!')

    data = response.json()
    number_of_pages = data['pages']
    all_data = [data['items']]

    for page in range(2, number_of_pages + 1):
        response = requests.get(f'{BASE_URL}/{endpoint}', params={'page': page})
        data = response.json()

        all_data.append(data['items'])

    return all_data


def format_data(data: list[list[dict[str, any]]]) -> pd.DataFrame:
    formatted_data = None

    for item in data:
        if formatted_data is None:
            formatted_data = pd.DataFrame.from_dict(item)
        else:
            formatted_data = pd.concat([formatted_data, pd.DataFrame.from_dict(item)])

    formatted_data = format_datetimes(formatted_data)

    return formatted_data.reset_index(drop=True)


def format_datetimes(data: pd.DataFrame) -> pd.DataFrame:
    data['created_at'] = pd.to_datetime(data['created_at'])
    data['updated_at'] = pd.to_datetime(data['updated_at'])

    return data


def load_local(endpoint: str, local_path: Path = LOCAL_PATH) -> Union[pd.DataFrame, None]:
    dataframe_path = local_path / f'{endpoint}.csv'
    if dataframe_path.exists():
        saved_data = pd.read_csv(dataframe_path)
        return format_datetimes(saved_data)
    else:
        return None


def save_local(data: pd.DataFrame, endpoint: str, local_path: Path = LOCAL_PATH) -> None:
    dataframe_path = local_path / f'{endpoint}.csv'
    data.to_csv(dataframe_path, index=False)


def write_to(data: pd.DataFrame, endpoint: str, local: bool = False, local_path: Path = LOCAL_PATH,
             db_engine: Union[Engine, None] = None) -> None:
    if endpoint == 'listen_history':
        id_str = 'user_id'
        data['items'] = data['items'].astype(str)
    else:
        id_str = 'id'

    if local:
        old_data = load_local(endpoint, local_path)
        if old_data is None:
            old_data = pd.DataFrame(columns=data.columns)
    else:
        old_data = pd.read_sql(f'SELECT * from {endpoint}', db_engine)

    old_data = format_datetimes(old_data)
    all_data = pd.concat([old_data, data])
    entries_before_duplicate_drop = all_data.shape[0]
    all_data = all_data.sort_values([id_str, 'updated_at'], ascending=[True, False])
    all_data = all_data.drop_duplicates(id_str, keep='first')
    updated_entries = entries_before_duplicate_drop - all_data.shape[0]
    new_entries = all_data.shape[0] - old_data.shape[0]

    if local:
        save_local(all_data, endpoint, local_path)
        log_string = 'LOCAL: '
    else:
        all_data.to_sql(endpoint, db_engine, if_exists='replace', index=False)
        log_string = 'DB: '

    print(f'{log_string}Writing done for {endpoint}. {updated_entries} updated entries, {new_entries} new entries.')


def load_last_run(local_path: Path = LOCAL_PATH) -> Union[dict[str, any], None]:
    tracking_path = local_path / f'last_run.json'
    if tracking_path.exists():
        with open(tracking_path) as f:
            return json.load(f)
    else:
        return None


def save_last_run(last_run: datetime, local_path: Path = LOCAL_PATH) -> None:
    tracking_path = local_path / f'last_run.json'
    tracking_path.parents[0].mkdir(parents=True, exist_ok=True)

    last_run = {'last_run': last_run.strftime('%Y-%m-%dT%H:%M:%S')}
    with open(tracking_path, 'w') as f:
        json.dump(last_run, f)


def process_data(endpoint: str, engine: Engine):

    # Data handling

    extracted_data = extract_data(endpoint)
    formatted_data = format_data(extracted_data)

    # Saving to DB
    write_to(formatted_data, endpoint, db_engine=engine)

    # Saving locally
    write_to(formatted_data, endpoint, local=True)


def handle_process_interval(interval: timedelta = timedelta(days=1)):
    start_time = datetime.utcnow()

    # On va utiliser ce fichier pour que le flux de données retient un certain mémoire; au cas ou le flux de données est
    # arrêté pour n'importe quelle raison, le code saurait quand elle extraire des données quand elle est remis en
    # marche
    last_run_json = load_last_run()

    # Si le json existe, on va référer à lui pour savoir quand 24h ont passé. Sinon, on commence le processus
    # immédiatement
    if last_run_json is not None:
        last_run = pd.to_datetime(last_run_json['last_run'])
        next_run = last_run + interval
        if start_time < next_run:
            time_to_sleep = (next_run - start_time).total_seconds()
            if time_to_sleep >= 3600:
                pretty_time = f'{time_to_sleep / 3600} hours'
            elif time_to_sleep >= 60:
                pretty_time = f'{time_to_sleep / 60} minutes'
            else:
                pretty_time = f'{time_to_sleep} seconds'

            print(f'Sleeping for {pretty_time} until next cycle...')
            time.sleep((next_run - start_time).total_seconds())

        start_time = datetime.utcnow()

    # On va ensuite marquer quand ce run a commencé pour le prochain cycle.
    print(f'Starting data extraction at {start_time}')
    save_last_run(start_time)


def main():

    # Pour être complètement minutieux, j'ai décidé de faire un petit database pour cette exercise en plus de
    # sauvegarder le data dans des fichiers.
    engine = create_db()
    while True:

        # J'ai mis ça pour imiter l'opération quotidien du flux de données. En pratique, ça serait certainement
        # coordonné par un système d'orchestration
        handle_process_interval(timedelta(days=1))

        for endpoint in ENDPOINTS:
            try:
                process_data(endpoint, engine)

            # Dans un plus grand système, on pourrait plus simplement incorporer un système d'events pour rerouler
            # quand le API est en-ligne
            except requests.exceptions.ConnectionError:
                print(f'Could not connect to endpoint {BASE_URL}/{endpoint}! Trying again during next cycle.')
            except requests.exceptions.RequestException:
                print(f'Unsuccessful response from endpoint {BASE_URL}/{endpoint}! Trying again during next cycle.')


if __name__ == '__main__':
    main()
