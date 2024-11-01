import requests
import logging
from config import config
from time import sleep

logging.basicConfig(level=logging.INFO)

class TMDBHelper:
    def __init__(self):
        tmdb_config = config.get('tmdb', {})
        self.api_key = tmdb_config.get('api_key')
        
        if not self.api_key:
            logging.error("TMDB API key is missing from configuration.")
            raise ValueError("API key is required.")
        
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
            # Restrict media_type to 'movie' or 'tv' for TMDB API compatibility
            if media_type not in ['movie', 'tv']:
                logging.warning(f"Invalid media_type '{media_type}', defaulting to 'movie'.")
                media_type = 'movie'
            
            endpoint = f"{self.base_url}/search/{media_type}"
            params = {'query': title}  # Removed 'api_key' from params
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
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            recommendations = response.json().get('results', [])
            logging.info(f"Retrieved {len(recommendations)} recommendations for TMDB ID {tmdb_id}")
            
            # Handle title vs. name based on media type
            title_key = 'title' if media_type == 'movie' else 'name'
            return [rec[title_key] for rec in recommendations if title_key in rec]

        except requests.RequestException as e:
            logging.error(f"Error fetching TMDB recommendations for ID {tmdb_id}: {e}")
            return []

def get_tmdb_recommendations(titles, media_type='tv'):
    """
    Get recommendations from TMDB for a list of titles.
    Args:
        titles (list): List of movie or show titles to fetch recommendations for.
        media_type (str): 'movie' or 'tv', default is 'tv'.
    Returns:
        dict: A dictionary mapping each title to its list of recommended titles.
    """
    tmdb_helper = TMDBHelper()  # Create an instance of TMDBHelper
    recommendations = {}
    for title in titles:
        try:
            recommendations[title] = tmdb_helper.get_recommendations(title, media_type)
            logging.info(f"Fetched recommendations for '{title}': {recommendations[title]}")
        except Exception as e:
            logging.error(f"Failed to get recommendations for '{title}': {e}")
    
    return recommendations
