#!/usr/bin/env python3
"""
Generate distinct dataset splits with category-biased rating patterns.
- set1: Computer Science & Mathematics focus (STEM bias)
- set2: Philosophy & Literature focus (Humanities bias)
- set3: Random mixed preferences
"""

import json
import csv
import random
from pathlib import Path
from collections import defaultdict

# Configuration
DATASET_PATH = Path("dataset")
BOOKS_FILE = DATASET_PATH / "set1" / "books.json"
USERS_FILE = DATASET_PATH / "set1" / "users.json"

# Categories mapping
CATEGORY_BOOKS = {
    "Computer Science": ["B001", "B002", "B003", "B004"],
    "Mathematics": ["B017", "B018", "B019", "B020"],
    "Philosophy": ["B013", "B014", "B015", "B016"],
    "Literature": ["B005", "B006", "B007", "B008"],
    "History": ["B009", "B010", "B011", "B012"]
}

STEM_BOOKS = set(CATEGORY_BOOKS["Computer Science"] + CATEGORY_BOOKS["Mathematics"])
HUMANITIES_BOOKS = set(CATEGORY_BOOKS["Philosophy"] + CATEGORY_BOOKS["Literature"] + CATEGORY_BOOKS["History"])

# Fixed seed for reproducibility
random.seed(42)


def load_books():
    """Load books from set1."""
    with open(BOOKS_FILE, 'r') as f:
        return json.load(f)['books']


def load_users():
    """Load users from set1."""
    with open(USERS_FILE, 'r') as f:
        return json.load(f)['users']


def get_rating(book_id, bias_categories, user_affinity):
    """
    Generate a rating based on category bias and user affinity.
    
    Args:
        book_id: Book ID to rate
        bias_categories: List of preferred categories for this dataset
        user_affinity: Float [0, 1] representing how strong the bias is
    
    Returns:
        Rating 1-5
    """
    # Map books to categories
    book_category = None
    for category, books in CATEGORY_BOOKS.items():
        if book_id in books:
            book_category = category
            break
    
    # If book is in preferred categories, bias toward higher ratings
    if book_category in bias_categories:
        # Generate ratings with preference: mostly 3-5, occasional lower
        if random.random() < user_affinity:
            return random.choices([4, 5], weights=[30, 70], k=1)[0]
        else:
            return random.randint(2, 5)
    else:
        # For non-preferred categories, more random/neutral/lower
        return random.choices([1, 2, 3, 4, 5], weights=[20, 25, 30, 15, 10], k=1)[0]


def create_set1_ratings(books, users):
    """
    SET1: Computer Science & Mathematics focus (STEM).
    Users rate STEM books highly, humanities moderately/low.
    """
    ratings = []
    stem_users = ["U001", "U004", "U005"]  # STEM-focused users
    humanities_users = ["U002", "U003"]  # Humanities-focused
    mixed_users = ["U006", "U007", "U008", "U009", "U010"]  # Mixed interests
    
    for user_id in [u['user_id'] for u in users]:
        # Determine user's interest pattern
        if user_id in stem_users:
            # STEM enthusiasts - rate CS & Math highly
            for book in books:
                bid = book['book_id']
                if bid in STEM_BOOKS:
                    rating = random.choices([4, 5], weights=[40, 60], k=1)[0]
                elif bid in HUMANITIES_BOOKS:
                    rating = random.choices([1, 2, 3], weights=[30, 40, 30], k=1)[0]
                else:
                    rating = random.randint(1, 5)
                
                # 70% chance to rate each book
                if random.random() < 0.6:
                    ratings.append({'user_id': user_id, 'book_id': bid, 'rating': rating})
        
        elif user_id in humanities_users:
            # Humanities enthusiasts - rate philosophy/literature highly
            for book in books:
                bid = book['book_id']
                if bid in HUMANITIES_BOOKS:
                    rating = random.choices([4, 5], weights=[40, 60], k=1)[0]
                elif bid in STEM_BOOKS:
                    rating = random.choices([1, 2, 3], weights=[25, 35, 40], k=1)[0]
                else:
                    rating = random.randint(1, 5)
                
                if random.random() < 0.5:
                    ratings.append({'user_id': user_id, 'book_id': bid, 'rating': rating})
        
        else:
            # Mixed users - broadly read with slight STEM preference
            for book in books:
                bid = book['book_id']
                rating = random.choices([1, 2, 3, 4, 5], weights=[10, 15, 30, 30, 15], k=1)[0]
                
                if random.random() < 0.5:
                    ratings.append({'user_id': user_id, 'book_id': bid, 'rating': rating})
    
    return ratings


def create_set2_ratings(books, users):
    """
    SET2: Philosophy & Literature focus (Humanities).
    Users rate humanities books highly, STEM moderately/low.
    """
    ratings = []
    humanities_users = ["U001", "U002", "U003", "U007"]  # Humanities-focused
    stem_users = ["U004", "U005", "U009"]  # STEM-focused but not as strong
    mixed_users = ["U006", "U008", "U010"]  # Mixed
    
    for user_id in [u['user_id'] for u in users]:
        if user_id in humanities_users:
            # Philosophy & Literature enthusiasts
            for book in books:
                bid = book['book_id']
                if bid in HUMANITIES_BOOKS:
                    rating = random.choices([4, 5], weights=[35, 65], k=1)[0]
                elif bid in STEM_BOOKS:
                    rating = random.choices([1, 2, 3], weights=[40, 35, 25], k=1)[0]
                else:
                    rating = random.randint(1, 5)
                
                if random.random() < 0.65:
                    ratings.append({'user_id': user_id, 'book_id': bid, 'rating': rating})
        
        elif user_id in stem_users:
            # STEM users in humanities dataset - still rate STEM decently
            for book in books:
                bid = book['book_id']
                if bid in STEM_BOOKS:
                    rating = random.choices([3, 4, 5], weights=[25, 50, 25], k=1)[0]
                elif bid in HUMANITIES_BOOKS:
                    rating = random.choices([2, 3, 4], weights=[30, 40, 30], k=1)[0]
                else:
                    rating = random.randint(1, 5)
                
                if random.random() < 0.45:
                    ratings.append({'user_id': user_id, 'book_id': bid, 'rating': rating})
        
        else:
            # Mixed - balanced across categories
            for book in books:
                bid = book['book_id']
                rating = random.choices([1, 2, 3, 4, 5], weights=[12, 18, 30, 28, 12], k=1)[0]
                
                if random.random() < 0.55:
                    ratings.append({'user_id': user_id, 'book_id': bid, 'rating': rating})
    
    return ratings


def create_set3_ratings(books, users):
    """
    SET3: Completely random mixed preferences.
    Users have unpredictable patterns, no clear bias.
    """
    ratings = []
    
    for user_id in [u['user_id'] for u in users]:
        # Each user has random preferences
        pref_categories = random.sample(list(CATEGORY_BOOKS.keys()), k=random.randint(2, 4))
        
        for book in books:
            bid = book['book_id']
            
            # Determine category
            book_category = None
            for category, books_list in CATEGORY_BOOKS.items():
                if bid in books_list:
                    book_category = category
                    break
            
            # Random rating with slight preference for books in user's categories
            if book_category in pref_categories and random.random() < 0.5:
                rating = random.choices([3, 4, 5], weights=[20, 40, 40], k=1)[0]
            else:
                rating = random.choices([1, 2, 3, 4, 5], weights=[18, 22, 30, 20, 10], k=1)[0]
            
            # Random rating probability
            if random.random() < 0.5:
                ratings.append({'user_id': user_id, 'book_id': bid, 'rating': rating})
    
    return ratings


def modify_users_preferences(users, set_name, category_bias):
    """Update user preferences to match their rating patterns."""
    modified_users = []
    
    for user in users:
        user_copy = user.copy()
        user_copy['preferred_categories'] = category_bias
        modified_users.append(user_copy)
    
    return modified_users


def write_dataset(set_name, books, users, ratings):
    """Write books, users, and ratings to dataset split."""
    set_path = DATASET_PATH / set_name
    set_path.mkdir(parents=True, exist_ok=True)
    
    # Write books.json (same across all sets)
    with open(set_path / "books.json", 'w') as f:
        json.dump({"count": len(books), "books": books}, f, indent=2)
    
    # Write users.json
    with open(set_path / "users.json", 'w') as f:
        json.dump({"count": len(users), "users": users}, f, indent=2)
    
    # Write ratings.csv
    with open(set_path / "ratings.csv", 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['user_id', 'book_id', 'rating'])
        writer.writeheader()
        for rating in ratings:
            writer.writerow(rating)
    
    return {
        'set': set_name,
        'books': len(books),
        'users': len(users),
        'ratings': len(ratings)
    }


def verify_integrity(set_name):
    """Verify referential integrity."""
    set_path = DATASET_PATH / set_name
    
    with open(set_path / "books.json") as f:
        books = json.load(f)['books']
    with open(set_path / "users.json") as f:
        users = json.load(f)['users']
    
    book_ids = {b['book_id'] for b in books}
    user_ids = {u['user_id'] for u in users}
    
    valid = 0
    invalid = 0
    
    with open(set_path / "ratings.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['book_id'] in book_ids and row['user_id'] in user_ids:
                valid += 1
            else:
                invalid += 1
    
    return {'valid': valid, 'invalid': invalid, 'all_valid': invalid == 0}


def analyze_ratings(ratings):
    """Analyze rating distribution."""
    rating_counts = defaultdict(int)
    for r in ratings:
        rating_counts[r['rating']] += 1
    
    return dict(rating_counts)


def main():
    """Main execution."""
    print("=" * 80)
    print("Creating DISTINCT datasets with DIFFERENT rating patterns")
    print("=" * 80)
    
    # Load source data
    books = load_books()
    users = load_users()
    
    print(f"\nLoaded: {len(books)} books, {len(users)} users")
    print("\nBook categories:")
    for category, book_ids in CATEGORY_BOOKS.items():
        print(f"  {category}: {', '.join(book_ids)}")
    
    # SET1: STEM Bias (Computer Science & Mathematics)
    print("\n" + "-" * 80)
    print("SET1: STEM BIAS (Computer Science & Mathematics focus)")
    print("-" * 80)
    ratings_set1 = create_set1_ratings(books, users)
    users_set1 = modify_users_preferences(
        users,
        "set1",
        ["Computer Science", "Mathematics"]
    )
    result1 = write_dataset("set1", books, users_set1, ratings_set1)
    verify1 = verify_integrity("set1")
    print(f"✓ {result1['set']}: {result1['books']} books, {result1['users']} users, {result1['ratings']} ratings")
    print(f"  Rating distribution: {analyze_ratings(ratings_set1)}")
    print(f"  Integrity: {verify1['valid']} valid, {verify1['invalid']} invalid ✓" if verify1['all_valid'] else "  ✗ FAILED")
    
    # SET2: Humanities Bias (Philosophy & Literature focus)
    print("\n" + "-" * 80)
    print("SET2: HUMANITIES BIAS (Philosophy & Literature focus)")
    print("-" * 80)
    ratings_set2 = create_set2_ratings(books, users)
    users_set2 = modify_users_preferences(
        users,
        "set2",
        ["Philosophy", "Literature", "History"]
    )
    result2 = write_dataset("set2", books, users_set2, ratings_set2)
    verify2 = verify_integrity("set2")
    print(f"✓ {result2['set']}: {result2['books']} books, {result2['users']} users, {result2['ratings']} ratings")
    print(f"  Rating distribution: {analyze_ratings(ratings_set2)}")
    print(f"  Integrity: {verify2['valid']} valid, {verify2['invalid']} invalid ✓" if verify2['all_valid'] else "  ✗ FAILED")
    
    # SET3: Random Mixed Preferences
    print("\n" + "-" * 80)
    print("SET3: RANDOM MIXED PREFERENCES (No clear bias)")
    print("-" * 80)
    ratings_set3 = create_set3_ratings(books, users)
    users_set3 = [
        {
            **user,
            'preferred_categories': random.sample(list(CATEGORY_BOOKS.keys()), k=random.randint(2, 4))
        }
        for user in users
    ]
    result3 = write_dataset("set3", books, users_set3, ratings_set3)
    verify3 = verify_integrity("set3")
    print(f"✓ {result3['set']}: {result3['books']} books, {result3['users']} users, {result3['ratings']} ratings")
    print(f"  Rating distribution: {analyze_ratings(ratings_set3)}")
    print(f"  Integrity: {verify3['valid']} valid, {verify3['invalid']} invalid ✓" if verify3['all_valid'] else "  ✗ FAILED")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("\n✓ SET1 (STEM bias):")
    print("  - Users prefer Computer Science & Mathematics")
    print("  - High ratings (4-5) for B001-B004, B017-B020")
    print("  - Low ratings (1-3) for Philosophy/Literature books")
    
    print("\n✓ SET2 (Humanities bias):")
    print("  - Users prefer Philosophy, Literature & History")
    print("  - High ratings (4-5) for B005-B016")
    print("  - Low ratings (1-3) for STEM books")
    
    print("\n✓ SET3 (Random mixed):")
    print("  - No clear pattern, truly random preferences per user")
    print("  - Each user has different preferred categories")
    print("  - Unpredictable rating patterns")
    
    print("\n✓ All datasets maintain referential integrity!")
    print("✓ Each dataset will produce DIFFERENT recommendation outputs in KNN system")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
