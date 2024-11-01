# fetch_data.py
import requests
from config import JELLYFIN_API_KEY, TMDB_API_KEY, JELLYFIN_URL, TMDB_URL, USER_ID

def fetch_jellyfin_library():
    headers = {'X-Emby-Token': JELLYFIN_API_KEY}
    response = requests.get(f"{JELLYFIN_URL}/Users/{USER_ID}/Items", headers=headers)
    return response.json().get('Items', [])


def get_new_releases_from_tmdb():
    url = f"{TMDB_URL}/movie/now_playing?api_key={TMDB_API_KEY}"
    response = requests.get(url)
    return response.json().get('results', [])
