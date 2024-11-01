# utils.py

def classify_by_age(releases):
    all_ages = []
    teen = []
    adult = []
    
    for release in releases:
        rating = release.get('age_rating')
        if rating in ['G', 'PG']:
            all_ages.append(release)
        elif rating in ['PG-13']:
            teen.append(release)
        elif rating in ['R', 'NC-17']:
            adult.append(release)
    
    return {'all_ages': all_ages, 'teen': teen, 'adult': adult}
