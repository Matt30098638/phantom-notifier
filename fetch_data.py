import requests
import logging
from config import get_jellyfin_config, get_tmdb_config

logging.basicConfig(level=logging.INFO)

class JellyfinFetcher:
    def __init__(self):
        jellyfin = get_jellyfin_config()
        self.api_key = jellyfin.get('api_key')
        self.server_url = jellyfin.get('url').rstrip('/')
        self.headers = {
            'X-Emby-Token': self.api_key,
            'Accept': 'application/json'
        }
        # Store fetched media folders
        self.media_folders = []

    def fetch_media_folders(self):
        """Fetch all media items directly from /Library/MediaFolders."""
        endpoint = f"{self.server_url}/Library/MediaFolders"
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            folders = response.json().get('Items', [])
            
            # Log and store folder details for movies and TV shows
            for folder in folders:
                name = folder.get('Name', '').lower()
                logging.info(f"Folder '{name}' with ID '{folder.get('Id')}' found in Jellyfin.")
                
                # Store each folder in media_folders
                self.media_folders.append({
                    'id': folder.get('Id'),
                    'name': folder.get('Name'),
                    'type': folder.get('CollectionType')  # CollectionType could be "movies" or "tvshows"
                })
        
        except requests.RequestException as e:
            logging.error(f"Error fetching media folders: {e}")
            if e.response:
                logging.debug(f"Response details: {e.response.text}")

    def fetch_all_media(self):
        """Fetch media items for each folder."""
        all_media = []
        
        # Ensure media folders are fetched
        if not self.media_folders:
            self.fetch_media_folders()
        
        for folder in self.media_folders:
            folder_id = folder.get('id')
            media_type = folder.get('type', 'unknown')
            logging.info(f"Fetching items from folder '{folder['name']}' (ID: {folder_id}, Type: {media_type}).")
            
            # Here we use the MediaItems endpoint within each folder context
            endpoint = f"{self.server_url}/Items"
            params = {
                'ParentId': folder_id,
                'Recursive': 'true',
                'Fields': 'Name,Id,CommunityRating,Type'
            }
            
            try:
                response = requests.get(endpoint, headers=self.headers, params=params)
                response.raise_for_status()
                items = response.json().get('Items', [])
                
                # Append fetched items to the overall media list with type for each folder
                all_media.extend([{
                    'title': item['Name'],
                    'jellyfin_id': item['Id'],
                    'type': 'movie' if media_type == 'movies' else 'tv'  # Map Jellyfin types to TMDB types
                } for item in items])
                
                logging.info(f"Fetched {len(items)} items from folder '{folder['name']}'.")
                
            except requests.RequestException as e:
                logging.error(f"Error fetching items from folder '{folder['name']}': {e}")
                if e.response:
                    logging.debug(f"Response details: {e.response.text}")
        
        logging.info(f"Total fetched media items: {len(all_media)}")
        return all_media

class TMDBHelper:
    def __init__(self):
        tmdb = get_tmdb_config()
        self.api_key = tmdb.get('api_key')
        self.base_url = 'https://api.themoviedb.org/3'
        if not self.api_key:
            logging.error("TMDB API key missing in configuration.")
            raise ValueError("TMDB configuration error")

    def get_recommendations(self, title, media_type='movie'):
        """Fetch recommendations from TMDB."""
        try:
            # Ensure the media_type is either 'movie' or 'tv' for TMDB endpoints
            media_type = 'movie' if media_type == 'movie' else 'tv'
            
            # Set the endpoint dynamically based on media_type (movie or tv)
            endpoint = f"{self.base_url}/search/{media_type}"
            params = {'query': title, 'api_key': self.api_key}
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            results = response.json().get('results', [])
            if not results:
                logging.warning(f"No TMDB results for '{title}'")
                return []

            # Use the first result's ID to fetch recommendations
            tmdb_id = results[0].get('id')
            return self._fetch_tmdb_recommendations(tmdb_id, media_type)
        except requests.RequestException as e:
            logging.error(f"TMDB API request error for '{title}': {e}")
            return []

    def _fetch_tmdb_recommendations(self, tmdb_id, media_type):
        """Fetch recommendations by TMDB ID."""
        try:
            endpoint = f"{self.base_url}/{media_type}/{tmdb_id}/recommendations"
            params = {'api_key': self.api_key}
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            recommendations = response.json().get('results', [])
            logging.info(f"Retrieved {len(recommendations)} recommendations for TMDB ID {tmdb_id}")
            
            # Safely access 'title' key and fallback to empty if missing
            return [rec.get('title', 'Unknown Title') for rec in recommendations]
        except requests.RequestException as e:
            logging.error(f"Error fetching TMDB recommendations for ID {tmdb_id}: {e}")
            return []

# Example usage
if __name__ == "__main__":
    fetcher = JellyfinFetcher()
    all_media = fetcher.fetch_all_media()
    logging.info(f"Fetched media items: {all_media}")

    # Fetch recommendations for an example title
    tmdb_helper = TMDBHelper()
    for media in all_media:
        recommendations = tmdb_helper.get_recommendations(media['title'], media['type'])
        logging.info(f"Recommendations for '{media['title']}': {recommendations}")
