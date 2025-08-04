import pandas as pd
import numpy as np
from extract import get_tracks_data,get_users_data,get_history_data

def clean_text_series(series: pd.Series) -> pd.Series:
    """Nettoyage et normalisation des données textuelles :
     - conversion en chaîne de caractères
     - mise en minuscules
     - suppression des espaces superflus
     - suppression des caractères spéciaux indésirables"""
    return (series.fillna("")
                  .astype(str)
                  .str.lower()
                  .str.strip()
                  .str.replace(r'[^\w\s-]', '', regex=True)
                  .replace('', np.nan))

def parse_datetime_series(series: pd.Series) -> pd.Series:
    """
    Analyse les dates et heures d'une série et les formate sous forme de chaînes de caractères
    au format « AAAA-MM-JJ HH:MM:SS » (compatible SQLite).
    """
    parsed = pd.to_datetime(series, errors='coerce')
    return parsed.dt.floor('s').dt.strftime('%Y-%m-%d %H:%M:%S')

def duration_to_seconds_series(series: pd.Series) -> pd.Series:
    """ Conversion de la durée au format mm:ss en secondes (ingénierie des fonctionnalités)"""
    def duration_to_seconds(duration):
        try:
            mins, secs = duration.split(":")
            return int(mins) * 60 + int(secs)
        except Exception:
            return np.nan
    return series.apply(duration_to_seconds)

def transform_tracks_df(df: pd.DataFrame) -> pd.DataFrame:
    # Suppression des doublons basés sur la colonne 'id'
    df = df.drop_duplicates(subset='id')

    # Nettoyage et normalisation des colonnes textuelles
    text_cols = ['name', 'artist', 'songwriters', 'genres', 'album']
    for col in text_cols:
        df[col] = clean_text_series(df[col])

    # Conversion de la durée en secondes
    df['duration_seconds'] = duration_to_seconds_series(df['duration'])
    df = df.drop('duration', axis=1)
    # Conversion des colonnes date en format datetime
    df['created_at'] = parse_datetime_series(df['created_at'])
    df['updated_at'] = parse_datetime_series(df['updated_at'])

    return df

def transform_users_df(df: pd.DataFrame) -> pd.DataFrame:
    # Suppression des doublons basés sur la colonne 'id'
    df = df.drop_duplicates(subset='id')

    # Nettoyage et normalisation des colonnes textuelles
    text_cols = ['first_name', 'last_name', 'email', 'gender', 'favorite_genres']
    for col in text_cols:
        df[col] = clean_text_series(df[col])

    # Supprimer les doublons d'e-mails (après normalisation)
    df = df.drop_duplicates(subset='email', keep='first')

    # Conversion des colonnes date en format datetime
    df['created_at'] = parse_datetime_series(df['created_at'])
    df['updated_at'] = parse_datetime_series(df['updated_at'])
    return df

def flatten_listen_history(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforme le DataFrame de l'historique d'écoute 
    afin que chaque élément de « items » devienne sa propre ligne.
    """
    records = []
    for _, row in df.iterrows():
        user_id = row['user_id']
        created_at = row['created_at']
        updated_at = row['updated_at']
        #rint(row.to_dict())
        for item in row['items']:
            records.append({
                'user_id': user_id,
                'item': item,
                'created_at': created_at,
                'updated_at': updated_at
            })
    return pd.DataFrame(records)

def transform_history_df(df: pd.DataFrame) -> pd.DataFrame:
    # Suppression des doublons basés sur la combinaison ('user_id', 'created_at')
    df = df.drop_duplicates(subset=['user_id', 'created_at'])
    # Conversion des colonnes date en format datetime
    df['created_at'] = parse_datetime_series(df['created_at'])
    df['updated_at'] = parse_datetime_series(df['updated_at'])

    # Nettoyage de la colonne 'items' : suppression des valeurs non entières ou négatives
    def clean_items(items):
        if not isinstance(items, list):
            return []
        return [i for i in items if isinstance(i, int) and i > 0]

    df['items'] = df['items'].apply(clean_items)
    #Tranformer les items (morceaux) aux lignes
    df = flatten_listen_history(df)
    return df

# Transform and clean tracks 
def tracks_db():
    tracks_df = get_tracks_data()
    print(tracks_df['created_at'])
    clean_tracks_df = transform_tracks_df(tracks_df)
    return clean_tracks_df 

# Transform and clean users
def users_db():
    users_df = get_users_data()
    clean_users_df = transform_users_df(users_df)
    return clean_users_df 

# Transform and clean history
def history_db():
    history_df = get_history_data()
    clean_history_df = transform_history_df(history_df)
    return clean_history_df 