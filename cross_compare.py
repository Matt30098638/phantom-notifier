import requests
import logging
from config import config
from time import sleep

logging.basicConfig(level=logging.INFO)

class TMDBHelper:
    def __init__(self):
        tmdb_config = config.get('tmdb', {})
        self.api_key = tmdb_config.get('api_key')
        self.base_url = 'https://api.themoviedb.org/3'
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        self.cache = {}

    def get_recommendations(self, title, media_type='movie'):
        """Fetch TMDB recommendations for a given title."""
        if title in self.cache:
            logging.info(f"Using cached recommendations for {title}")
            return self.cache[title]

        try:
            endpoint = f"{self.base_url}/search/{media_type}"
            params = {'query': title, 'api_key': self.api_key}
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            results = response.json().get('results', [])

            if not results:
                logging.warning(f"No TMDB results found for '{title}'")
                return []

            # Assume the first result is correct, then get recommendations
            tmdb_id = results[0].get('id')
            recommendations = self._fetch_tmdb_recommendations(tmdb_id, media_type)
            self.cache[title] = recommendations  # Cache the result
            return recommendations

        except requests.RequestException as e:
            logging.error(f"TMDB API request error for '{title}': {e}")
            return []

    def _fetch_tmdb_recommendations(self, tmdb_id, media_type):
        """Fetch recommendations by TMDB ID."""
        try:
            endpoint = f"{self.base_url}/{media_type}/{tmdb_id}/recommendations"
            params = {'api_key': self.api_key}
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            recommendations = response.json().get('results', [])
            logging.info(f"Retrieved {len(recommendations)} recommendations for TMDB ID {tmdb_id}")
            return [rec['title'] for rec in recommendations]

        except requests.RequestException as e:
            logging.error(f"Error fetching TMDB recommendations for ID {tmdb_id}: {e}")
            return []
