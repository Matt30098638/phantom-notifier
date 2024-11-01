# main.py
from fetch_data import fetch_jellyfin_library, get_new_releases_from_tmdb
from cross_compare import cross_compare_library
from utils import classify_by_age
from email_notifications import compose_email_content, send_email
from database import initialize_db, store_notified_release
from config import RECIPIENT_GROUPS
import time
import schedule


def main():
    # Initialize database
    initialize_db()

    library = fetch_jellyfin_library()
    new_releases = get_new_releases_from_tmdb()
    
    relevant_releases = cross_compare_library(new_releases, library)
    
    categorized_releases = classify_by_age(relevant_releases)
    
    for age_group, releases in categorized_releases.items():
        if releases:
            email_content = compose_email_content(releases, age_group)
            send_email(email_content, RECIPIENT_GROUPS[age_group])

            # Store notified releases
            for release in releases:
                store_notified_release(release['title'], release['release_date'], release.get('age_rating'))

# Set up the schedule
schedule.every().hour.do(main)  # Run main every hour

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)