import time
import logging
from fetch_data import JellyfinFetcher, TMDBHelper
from database import add_media_item, add_recommendation, get_all_media_items, get_new_recommendations
from email_notifications import send_summary_notification
from utils import log_message, retry  # Importing custom logging and retry utilities

logging.basicConfig(level=logging.INFO)

@retry(retries=3, delay=5, backoff=2)
def fetch_and_store_media():
    """Fetch media data from Jellyfin and store it in the database."""
    try:
        fetcher = JellyfinFetcher()
        all_media = fetcher.fetch_all_media()
        
        for item in all_media:
            if isinstance(item, dict):  # Ensuring item is a dictionary
                log_message(f"Processing item: {item}")  # Improved logging for debugging
                add_media_item(title=item.get('title'), media_type=item.get('type'), jellyfin_id=item.get('jellyfin_id'))
                
        log_message("Media data fetched and stored successfully.")
    except Exception as e:
        log_message(f"Error fetching and storing media: {e}", level="error")

@retry(retries=3, delay=5, backoff=2)
def fetch_and_store_recommendations():
    """Fetch recommendations from TMDB and store them in the database."""
    try:
        tmdb_helper = TMDBHelper()
        media_items = get_all_media_items()

        for item in media_items:
            recommendations = tmdb_helper.get_recommendations(item['title'], item['type'])
            for rec_title in recommendations:
                add_recommendation(media_item_id=item['id'], recommended_title=rec_title)

        log_message("Recommendations fetched and stored successfully.")
    except Exception as e:
        log_message(f"Error fetching and storing recommendations: {e}", level="error")

def main():
    """Main function to execute media fetch and recommendation update."""
    # Fetch and store media items with enhanced logging and retry
    fetch_and_store_media()
    
    # Fetch and store recommendations with enhanced logging and retry
    fetch_and_store_recommendations()
    
    # Send notification if there are new recommendations
    try:
        new_recommendations = get_new_recommendations()
        if new_recommendations:
            send_summary_notification(new_recommendations)
        else:
            log_message("No new recommendations to notify.")
    except Exception as e:
        log_message(f"Error sending notifications: {e}", level="error")

if __name__ == "__main__":
    while True:
        main()
        log_message("Task completed. Sleeping for 24 hours.")
        time.sleep(86400)
