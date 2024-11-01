import requests
import logging
import json
from config import config  # Assuming Jellyfin configuration is retrieved here

# Setting up logging for detailed information
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class JellyfinFetcher:
    def __init__(self):
        # Fetching Jellyfin configuration from config
        jellyfin_config = config.get('jellyfin', {})
        self.api_key = jellyfin_config.get('api_key')
        self.server_url = jellyfin_config.get('server_url')
        
        if not self.api_key or not self.server_url:
            logging.error("Jellyfin API configuration is missing. Check 'api_key' and 'server_url'.")
            raise ValueError("Jellyfin configuration error")

        # Setting headers for Jellyfin API
        self.headers = {
            'X-Emby-Token': self.api_key,
            'Accept': 'application/json'
        }

    def fetch_media(self, media_type='Movie'):
        """Fetch movies or TV shows from Jellyfin based on media_type."""
        try:
            endpoint = f"{self.server_url}/Users/{self.get_user_id()}/Items"
            params = {
                'IncludeItemTypes': media_type,
                'Recursive': 'true',
                'Fields': 'Name, Id'
            }
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            media_items = response.json().get('Items', [])

            logging.info(f"Fetched {len(media_items)} {media_type.lower()}s from Jellyfin.")
            return media_items
        except requests.RequestException as e:
            logging.error(f"Failed to fetch {media_type.lower()}s: {e}")
            return []

    def get_user_id(self):
        """Retrieve the Jellyfin user ID based on the provided API key."""
        try:
            endpoint = f"{self.server_url}/Users"
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            users = response.json()
            # Assuming the first user in the list is the target user for simplicity
            user_id = users[0]['Id']
            logging.info(f"Retrieved Jellyfin user ID: {user_id}")
            return user_id
        except requests.RequestException as e:
            logging.error(f"Failed to retrieve Jellyfin user ID: {e}")
            raise

    def fetch_movies(self):
        """Fetch movies from Jellyfin."""
        return self.fetch_media(media_type='Movie')

    def fetch_tv_shows(self):
        """Fetch TV shows from Jellyfin."""
        return self.fetch_media(media_type='Series')

# Sample usage
if __name__ == "__main__":
    fetcher = JellyfinFetcher()
    movies = fetcher.fetch_movies()
    tv_shows = fetcher.fetch_tv_shows()
    
    logging.info(f"Movies: {json.dumps(movies, indent=2)}")
    logging.info(f"TV Shows: {json.dumps(tv_shows, indent=2)}")
