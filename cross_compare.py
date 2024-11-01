# cross_compare.py
from database import was_notified

def cross_compare_library(new_releases, library):
    matches = []
    library_titles = {item['Title'] for item in library}

    for release in new_releases:
        # Only notify if it hasn't been notified before
        if release['title'] in library_titles and not was_notified(release['title'], release['release_date']):
            matches.append(release)
    
    return matches
