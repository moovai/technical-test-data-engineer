import pandas as pd
import random
import shutil
import sys
import unittest

from datetime import datetime, timedelta
from fastapi_pagination import create_page, Params
from pathlib import Path
from sqlalchemy import inspect, create_engine
from sqlalchemy.sql.sqltypes import INTEGER, VARCHAR, DATETIME
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.moovitamix_fastapi.classes_out import TracksOut, UsersOut, ListenHistoryOut
from src.moovitamix_fastapi.data_flux import create_db, extract_data, format_data, load_local, save_local, write_to, \
    load_last_run, save_last_run, handle_process_interval

# Créer un faux response de l'API. Comme ça, on pourrait rouler nos tests sans avoir besoin que le API soit en-ligne.
data_range_observations = 1000

generated_data = {
    'tracks': [
            TracksOut.generate_fake() for _ in range(data_range_observations)
        ],
    'users': [UsersOut.generate_fake() for _ in range(data_range_observations)],
    'listen_history': [
            ListenHistoryOut.generate_fake()
            for _ in range(data_range_observations)
        ]
}

for index, item in enumerate(generated_data['listen_history']):
    random_tracks = random.sample(
        [track.id for track in generated_data['tracks']], 5
    )  # pick 5 random track IDs per user
    generated_data['listen_history'][index] = ListenHistoryOut(
        user_id=generated_data['users'][index].id,
        items=random_tracks,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )

# Encore des variables qui changeront pas dans tous les tests
BASE_URL = 'http://127.0.0.1:8000'
ENDPOINTS = ['tracks', 'users', 'listen_history']

DB_URL = f"sqlite:///{Path(__file__).resolve().parent}/test_data/db.sqlite"
LOCAL_PATH = Path(__file__).resolve().parent / 'test_data'


# Va aider à générer le mock request
def mimic_response(data):
    mock_pages = []
    for page in range(1, 11):
        params = Params(size=100, page=page)
        page_data = create_page(data, total=data_range_observations, params=params)

        mock_pages.append(unittest.mock.Mock())
        mock_pages[page-1].status_code = 200
        mock_pages[page-1].json.return_value = {
            'pages': page_data.pages,
            'size': page_data.size,
            'total': page_data.total,
            'items': [dict(x) for x in page_data.items[100 * (page-1): (100 * page)]]
        }

    return mock_pages


def test_create_db():
    shutil.rmtree(LOCAL_PATH, ignore_errors=True)
    LOCAL_PATH.mkdir(parents=True, exist_ok=True)
    create_db(DB_URL)
    engine = create_engine(DB_URL, connect_args={"check_same_thread": False})

    # Vérifie si le db a bel et bien été créé
    assert (LOCAL_PATH / 'db.sqlite').exists()

    inspector = inspect(engine)
    all_tables = inspector.get_table_names()

    expected_columns = {
        'tracks': {
            'id': INTEGER,
            'name': VARCHAR,
            'artist': VARCHAR,
            'songwriters': VARCHAR,
            'duration': VARCHAR,
            'genres': VARCHAR,
            'album': VARCHAR,
            'created_at': DATETIME,
            'updated_at': DATETIME

        },
        'users': {
            'id': INTEGER,
            'first_name': VARCHAR,
            'last_name': VARCHAR,
            'email': VARCHAR,
            'gender': VARCHAR,
            'favorite_genres': VARCHAR,
            'created_at': DATETIME,
            'updated_at': DATETIME

        },
        'listen_history': {
            'user_id': INTEGER,
            'items': VARCHAR,
            'created_at': DATETIME,
            'updated_at': DATETIME
        }
    }

    for table in ENDPOINTS:
        assert table in all_tables

        columns = inspector.get_columns(table)
        actual_columns = {col['name']: col['type'] for col in columns}

        for key, value in expected_columns[table].items():

            # Vérifie que tous les colonnes ont bel et bien été mis dans les tables du db.
            assert key in list(actual_columns.keys())

            # Vérifie que les types des colonnes a bien été enregistrés
            assert expected_columns[table][key] == type(actual_columns[key])

            # Vérifie la longueur des colonnes String
            if expected_columns[table][key] == VARCHAR:
                if key == 'duration':
                    assert actual_columns[key].length == 10
                elif key == 'gender':
                    assert actual_columns[key].length == 50
                else:
                    assert actual_columns[key].length == 255


class TestExtractData(unittest.TestCase):
    @patch('requests.get')
    def test_extract_data(self, mock_get):

        for endpoint in ENDPOINTS:

            mock_pages = mimic_response(generated_data[endpoint])
            mock_get.side_effect = mock_pages

            expected_fields = dict(generated_data[endpoint][0]).keys()
            expected_number_of_pages = 10
            expected_total_entries = data_range_observations
            expected_entries_per_page = 100

            extracted_data = extract_data(endpoint)

            mock_get.assert_any_call(f'http://127.0.0.1:8000/{endpoint}')

            for i in range(2, 11):
                # Vérifie qu'on touche tous les endpoints qu'on anticipe
                mock_get.assert_any_call(f'http://127.0.0.1:8000/{endpoint}', params={'page': i})

            actual_number_of_pages = len(extracted_data)
            actual_total_items = 0

            # Vérifie qu'on n'a pas manqué de pages
            assert actual_number_of_pages == expected_number_of_pages

            all_ids = []
            for extracted_item in extracted_data:
                actual_total_items += len(extracted_item)

                if endpoint != 'listen_history':
                    all_ids += [x['id'] for x in extracted_item]
                else:
                    all_ids += [x['user_id'] for x in extracted_item]

                # Vérifie que les pages sont la bonne longueur
                assert len(extracted_item) == expected_entries_per_page

                for entry in extracted_item:
                    # Vérifie qu'on n'a rien manqué par rapport aux colonnes
                    assert entry.keys() == expected_fields

            # Vérifie qu'on n'a rien perdu dans le data
            assert actual_total_items == expected_total_entries

            # Vérifie que la pagination n'a pas résulté en des valeurs dupliqués
            assert len(list(dict.fromkeys(all_ids))) == 1000


class TestFormatData(unittest.TestCase):
    @patch('requests.get')
    def test_format_data(self, mock_get):
        for endpoint in ENDPOINTS:

            mock_pages = mimic_response(generated_data[endpoint])
            mock_get.side_effect = mock_pages

            extracted_data = extract_data(endpoint)
            formatted_data = format_data(extracted_data)

            # Vérifie qu'on n'a pas perdu de données
            assert formatted_data.shape[0] == 1000
            # Vérifie que tout le data a été transfert et qu'on n'a pas des NaN ou valeurs vides
            assert formatted_data.isnull().sum().sum() == 0

            # Vérifie qu'on n'a rien dupliqué durant la concatenation
            if endpoint != 'listen_history':
                assert formatted_data.drop_duplicates('id').shape[0] == formatted_data.shape[0]
            else:
                assert formatted_data.drop_duplicates('user_id').shape[0] == formatted_data.shape[0]


def test_load_and_save_local():
    shutil.rmtree(LOCAL_PATH, ignore_errors=True)
    LOCAL_PATH.mkdir(parents=True, exist_ok=True)
    for endpoint in ENDPOINTS:
        file = load_local(endpoint, LOCAL_PATH)

        # Vérifie que load_local a bel et bien confirmé que le fichier n'existe pas
        assert file is None
        dummy_df = pd.DataFrame.from_dict(
            [
                {
                    'id': 1,
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                 },
                {
                    'id': 2,
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
            ]
        )

        save_local(dummy_df, endpoint, LOCAL_PATH)

        # Vérifie que le fichier a été créé
        assert (LOCAL_PATH / f'{endpoint}.csv').exists()

        file = load_local(endpoint, LOCAL_PATH)

        # Et que load_local l'a trouvé et l'a bien lu
        assert file.equals(dummy_df)


class TestWriteToDB(unittest.TestCase):
    @patch('requests.get')
    def test_write_to_db(self, mock_get):
        shutil.rmtree(LOCAL_PATH, ignore_errors=True)
        LOCAL_PATH.mkdir(parents=True, exist_ok=True)

        create_db(DB_URL)
        engine = create_engine(DB_URL, connect_args={"check_same_thread": False})

        for endpoint in ENDPOINTS:

            # Qu'il y a rien dans le db pour l'instant
            assert pd.read_sql(f'SELECT * FROM {endpoint}', engine).shape[0] == 0

            mock_pages = mimic_response(generated_data[endpoint])
            mock_get.side_effect = mock_pages

            extracted_data = extract_data(endpoint)
            formatted_data = format_data(extracted_data)

            # Sauvegarder au DB
            write_to(formatted_data, endpoint, db_engine=engine)

            written_data = pd.read_sql(f'SELECT * FROM {endpoint}', engine)
            written_data['created_at'] = pd.to_datetime(written_data['created_at'])
            written_data['updated_at'] = pd.to_datetime(written_data['updated_at'])

            # Que ce qui est sorti du db est égal a ce qui a été mis dans le db (avec un peu de sorting)
            if endpoint != 'listen_history':
                assert written_data.equals(formatted_data.sort_values(['id']).reset_index(drop=True))
            else:
                assert written_data.equals(formatted_data.sort_values(['user_id']).reset_index(drop=True))

            # Prouver que faire un update des données va pas causer de problèmes
            write_to(formatted_data, endpoint, db_engine=engine)
            written_data = pd.read_sql(f'SELECT * FROM {endpoint}', engine)
            written_data['created_at'] = pd.to_datetime(written_data['created_at'])
            written_data['updated_at'] = pd.to_datetime(written_data['updated_at'])
            if endpoint != 'listen_history':
                assert written_data.equals(formatted_data.sort_values(['id']).reset_index(drop=True))
            else:
                assert written_data.equals(formatted_data.sort_values(['user_id']).reset_index(drop=True))


class TestWriteToLocal(unittest.TestCase):
    @patch('requests.get')
    def test_write_to_local(self, mock_get):
        shutil.rmtree(LOCAL_PATH, ignore_errors=True)
        LOCAL_PATH.mkdir(parents=True, exist_ok=True)

        for endpoint in ENDPOINTS:

            # Que le fichier n'existe pas encore
            assert not (LOCAL_PATH / f'{endpoint}.csv').exists()

            mock_pages = mimic_response(generated_data[endpoint])
            mock_get.side_effect = mock_pages

            extracted_data = extract_data(endpoint)
            formatted_data = format_data(extracted_data)

            # Sauvegarder localement
            write_to(formatted_data, endpoint, True, LOCAL_PATH)

            # Que le fichier existe maintenant
            assert (LOCAL_PATH / f'{endpoint}.csv').exists()

            written_data = pd.read_csv(LOCAL_PATH / f'{endpoint}.csv')
            written_data['created_at'] = pd.to_datetime(written_data['created_at'])
            written_data['updated_at'] = pd.to_datetime(written_data['updated_at'])

            # Que ce qui est sorti du fichier est égal a ce qui a été mis dans le fichier

            if endpoint != 'listen_history':
                assert written_data.equals(formatted_data.sort_values(['id']).reset_index(drop=True))
            else:
                assert written_data.equals(formatted_data.sort_values(['user_id']).reset_index(drop=True))

            # Prouver que faire un update des données va pas causer de problèmes.
            # Un peu superflu dans ce cas, mais bon :)

            write_to(formatted_data, endpoint, True, LOCAL_PATH)
            written_data = pd.read_csv(LOCAL_PATH / f'{endpoint}.csv')
            written_data['created_at'] = pd.to_datetime(written_data['created_at'])
            written_data['updated_at'] = pd.to_datetime(written_data['updated_at'])

            if endpoint != 'listen_history':
                assert written_data.equals(formatted_data.sort_values(['id']).reset_index(drop=True))
            else:
                assert written_data.equals(formatted_data.sort_values(['user_id']).reset_index(drop=True))


def test_load_and_save_last_run():
    shutil.rmtree(LOCAL_PATH, ignore_errors=True)
    LOCAL_PATH.mkdir(parents=True, exist_ok=True)

    result = load_last_run(LOCAL_PATH)

    # Vérifie que load_last_run a bel et bien confirmé que le fichier n'existe pas
    assert result is None

    run_time = datetime.utcnow()
    save_last_run(run_time, LOCAL_PATH)

    # Que save_last_run a créé le fichier
    assert (LOCAL_PATH / 'last_run.json').exists()

    result = load_last_run(LOCAL_PATH)

    # Que le fichier a les bonnes valeurs
    assert 'last_run' in result.keys()
    assert datetime.strptime(result.get('last_run'), '%Y-%m-%dT%H:%M:%S') == run_time.replace(microsecond=0)


def test_handle_process_interval():
    shutil.rmtree(LOCAL_PATH, ignore_errors=True)
    LOCAL_PATH.mkdir(parents=True, exist_ok=True)

    start_time = datetime.utcnow()
    handle_process_interval(timedelta(seconds=5), LOCAL_PATH)
    end_time = datetime.utcnow()

    # Que handle_process_interval n'arrête pas le processus vu que last_run existe pas
    assert round((end_time - start_time).total_seconds()) == 0

    start_time = datetime.utcnow()
    save_last_run(start_time, LOCAL_PATH)
    handle_process_interval(timedelta(seconds=5), LOCAL_PATH)
    end_time = datetime.utcnow()

    # Que last run arrête le processus pour presque les 5 secondes de test (considérant les maigres pertes de temps en
    # processing).
    assert 4 <= round((end_time - start_time).total_seconds()) <= 5
