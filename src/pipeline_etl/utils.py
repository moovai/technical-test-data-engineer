import requests
from typing import Dict, Any, List
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_all_pages(url:str, params:Dict[str, Any]) -> List[Dict[str, Any]]:
    if params is None:
        params = {}
    data = []
    max_pages = None
    page = params.get('page',1)
    while True:
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            json_data = response.json()
            items = json_data.get('items', [])
            if not items:
                break
            data.extend(items)
            if json_data.get('total_pages'):
                max_pages = json_data.get('total_pages')
            if page == max_pages:
                break
            page += 1
            params['page'] = page
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url} with params {params}: {e}")
            break
        except Exception as e:
            logger.error(f"Error fetching {url} with params {params}: {e}")
            break
    return data

def transform_base(df:pd.DataFrame) -> pd.DataFrame:
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    return df

def transform_tracks(df:pd.DataFrame) -> pd.DataFrame:
    df = transform_base(df)
    # Exemple pour Tracks : renommer l'id en track_id
    df.rename(columns={'id':'track_id'}, inplace=True)
    # Exemple pour Tracks : duration en secondes
    df['duration'] = df['duration'].apply(lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1]))
    return df

def transform_users(df:pd.DataFrame) -> pd.DataFrame:
    df = transform_base(df)
    # Exemple pour Users : renommer l'id en user_id
    df.rename(columns={'id':'user_id'}, inplace=True)
    # Exemple pour Users : anonymiser les données
    df = df.drop(columns=['first_name', 'last_name','email'])
    return df

def transform_listen_history(df:pd.DataFrame) -> pd.DataFrame:
    # Exemple pour Listen History : join avec | et renomer en tracks_id
    df['items'] = df['items'].apply(lambda x: '|'.join(map(str, x)))
    df = transform_base(df)
    df.rename(columns={'items':'tracks_id'}, inplace=True)
    return df