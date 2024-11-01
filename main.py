import time
import logging
from database import add_media_item, add_recommendation, cache_recommendation_exists
from fetch_data import get_jellyfin_data, get_tmdb_recommendations
from email_notifications import send_summary_notification
from utils import log_error, retry

logging.basicConfig(level=logging.INFO)


def fetch_jellyfin_media():
    """Fetch media items from Jellyfin and store them in the database."""
    try:
        media_items = get_jellyfin_data()
        for item in media_items:
            if not item_in_database(item['title'], item['jellyfin_id']):
                add_media_item(title=item['title'], media_type=item['type'], jellyfin_id=item['jellyfin_id'])
        logging.info("Jellyfin media fetch complete.")
    except Exception as e:
        log_error(f"Error fetching Jellyfin media: {e}")


def fetch_tmdb_recommendations():
    """Fetch recommendations from TMDB for Jellyfin media items."""
    try:
        media_items = get_all_media_items()
        for media in media_items:
            if not cache_recommendation_exists(media.id):
                recommendations = get_tmdb_recommendations(media.title, media.media_type)
                for recommendation in recommendations:
                    add_recommendation(
                        media_item_id=media.id,
                        recommended_title=recommendation['title'],
                        recommended_type=recommendation['type'],
                        tmdb_id=recommendation['tmdb_id']
                    )
        logging.info("TMDB recommendation fetch complete.")
    except Exception as e:
        log_error(f"Error fetching TMDB recommendations: {e}")


def update_database():
    """Update the database with new media and recommendations."""
    fetch_jellyfin_media()
    fetch_tmdb_recommendations()
    logging.info("Database update complete.")


def send_notifications():
    """Send notification email with a summary of new recommendations."""
    try:
        recommendations = get_new_recommendations()
        if recommendations:
            send_summary_notification(recommendations)
    except Exception as e:
        log_error(f"Error sending notifications: {e}")


def schedule_tasks():
    """Scheduler to periodically fetch data, update the database, and send notifications."""
    while True:
        update_database()
        send_notifications()
        logging.info("Scheduled tasks completed. Sleeping for 24 hours.")
        time.sleep(86400)  # Schedule to run once every 24 hours


if __name__ == "__main__":
    logging.info("Starting PhantomFetch.")
    schedule_tasks()
