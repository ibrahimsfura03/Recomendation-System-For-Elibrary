#!/usr/bin/env python3
"""
Dataset Refactoring Script
Combines t*.json files and creates three organized dataset splits (set1, set2, set3)
with proper referential integrity between books, users, and ratings.
"""

import json
import csv
import os
import random
from pathlib import Path
from datetime import datetime, timedelta

# Configuration
DATASET_PATH = Path("dataset")
BOOKS_FILE = DATASET_PATH / "t2.json"
USERS_FILE = DATASET_PATH / "t3.json"
RATINGS_FILE = DATASET_PATH / "interactions.csv"
OUTPUT_BASE = DATASET_PATH

# Set random seed for reproducibility
random.seed(42)


def load_books_from_file(file_path):
    """Load books from t2.json."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data.get('books', [])


def load_users_from_file(file_path):
    """Load users from t3.json."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data.get('users', [])


def load_ratings_from_csv(file_path):
    """Load ratings from interactions.csv."""
    ratings = []
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ratings.append({
                'user_id': row['user_id'],
                'book_id': row['book_id'],
                'rating': int(row['rating'])
            })
    return ratings


def generate_synthetic_users(num_users=20):
    """Generate synthetic users if needed."""
    categories = ["Computer Science", "Literature", "History", "Philosophy", "Mathematics"]
    given_names = ["Alice", "Bob", "Charlie", "Diana", "Evan", "Fiona", "George", "Hannah", 
                   "Ivan", "Jane", "Kevin", "Laura", "Mark", "Nancy", "Oscar", "Paula",
                   "Quinn", "Rachel", "Steve", "Tina"]
    last_names = ["Smith", "Jones", "Brown", "Prince", "Wright", "Lee", "Garcia", "Miller",
                  "Davis", "Wilson", "Anderson", "Taylor", "Thomas", "Moore", "Jackson", "Martin"]
    
    users = []
    base_date = datetime(2023, 1, 1)
    
    for i in range(1, num_users + 1):
        user_id = f"U{i:03d}"
        first_name = random.choice(given_names)
        last_name = random.choice(last_names)
        name = f"{first_name} {last_name}"
        email = f"{first_name.lower()}.{last_name.lower()}@example.com"
        preferred_categories = random.sample(categories, k=random.randint(1, 3))
        joined_date = (base_date + timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
        
        users.append({
            "user_id": user_id,
            "name": name,
            "email": email,
            "preferred_categories": preferred_categories,
            "joined_date": joined_date
        })
    
    return users


def create_dataset_split(split_name, books, users, ratings, shuffle_factor=0.0):
    """
    Create a single dataset split.
    
    Args:
        split_name: Name of the split (e.g., "set1")
        books: List of book dictionaries
        users: List of user dictionaries
        ratings: List of rating dictionaries
        shuffle_factor: Fraction of ratings to shuffle/resample (0.0 = no shuffle, 1.0 = full reshuffle)
    """
    split_path = OUTPUT_BASE / split_name
    split_path.mkdir(parents=True, exist_ok=True)
    
    # Prepare books.json
    books_json_path = split_path / "books.json"
    books_data = {
        "count": len(books),
        "books": books
    }
    with open(books_json_path, 'w') as f:
        json.dump(books_data, f, indent=2)
    
    # Prepare users.json
    users_json_path = split_path / "users.json"
    users_data = {
        "count": len(users),
        "users": users
    }
    with open(users_json_path, 'w') as f:
        json.dump(users_data, f, indent=2)
    
    # Prepare ratings.csv with potential shuffling/modification
    if shuffle_factor > 0:
        # Resample some ratings with different ratings
        shuffled_ratings = []
        shuffle_count = int(len(ratings) * shuffle_factor)
        indices_to_shuffle = set(random.sample(range(len(ratings)), shuffle_count))
        
        for idx, rating in enumerate(ratings):
            if idx in indices_to_shuffle:
                # Resample rating
                new_rating = random.randint(1, 5)
                shuffled_ratings.append({
                    'user_id': rating['user_id'],
                    'book_id': rating['book_id'],
                    'rating': new_rating
                })
            else:
                shuffled_ratings.append(rating)
        
        final_ratings = shuffled_ratings
    else:
        final_ratings = ratings
    
    # Write ratings.csv
    ratings_csv_path = split_path / "ratings.csv"
    with open(ratings_csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['user_id', 'book_id', 'rating'])
        writer.writeheader()
        for rating in final_ratings:
            writer.writerow(rating)
    
    # Verify referential integrity
    book_ids = {b['book_id'] for b in books}
    user_ids = {u['user_id'] for u in users}
    
    missing_books = set()
    missing_users = set()
    
    for rating in final_ratings:
        if rating['book_id'] not in book_ids:
            missing_books.add(rating['book_id'])
        if rating['user_id'] not in user_ids:
            missing_users.add(rating['user_id'])
    
    return {
        'split': split_name,
        'books_count': len(books),
        'users_count': len(users),
        'ratings_count': len(final_ratings),
        'missing_books': list(missing_books),
        'missing_users': list(missing_users),
        'valid': len(missing_books) == 0 and len(missing_users) == 0
    }


def main():
    """Main refactoring function."""
    print("=" * 70)
    print("Dataset Refactoring for Recommendation System")
    print("=" * 70)
    
    # Load source data
    print("\n[1/5] Loading source data...")
    try:
        books = load_books_from_file(BOOKS_FILE)
        print(f"  ✓ Loaded {len(books)} books from {BOOKS_FILE.name}")
    except Exception as e:
        print(f"  ✗ Error loading books: {e}")
        return
    
    try:
        users = load_users_from_file(USERS_FILE)
        print(f"  ✓ Loaded {len(users)} users from {USERS_FILE.name}")
    except Exception as e:
        print(f"  ✗ Error loading users: {e}")
        print("  → Generating synthetic users...")
        users = generate_synthetic_users(num_users=20)
        print(f"  ✓ Generated {len(users)} synthetic users")
    
    try:
        ratings = load_ratings_from_csv(RATINGS_FILE)
        print(f"  ✓ Loaded {len(ratings)} ratings from {RATINGS_FILE.name}")
    except Exception as e:
        print(f"  ✗ Error loading ratings: {e}")
        return
    
    # Ensure all book_ids and user_ids in ratings exist in our datasets
    print("\n[2/5] Validating referential integrity...")
    book_ids = {b['book_id'] for b in books}
    user_ids = {u['user_id'] for u in users}
    
    original_rating_count = len(ratings)
    ratings = [r for r in ratings if r['book_id'] in book_ids and r['user_id'] in user_ids]
    
    if len(ratings) < original_rating_count:
        print(f"  ⚠ Filtered ratings: {original_rating_count} → {len(ratings)} "
              f"(removed {original_rating_count - len(ratings)} invalid entries)")
    else:
        print(f"  ✓ All {len(ratings)} ratings are valid")
    
    # Shuffle users pool for set2 and set3 to create variation
    all_users = users
    shuffled_users = users.copy()
    random.shuffle(shuffled_users)
    
    # Create set1 (original, no modification)
    print("\n[3/5] Creating dataset splits...")
    
    result1 = create_dataset_split(
        "set1",
        books=books,
        users=users,
        ratings=ratings,
        shuffle_factor=0.0
    )
    print(f"  ✓ {result1['split']}: {result1['books_count']} books, "
          f"{result1['users_count']} users, {result1['ratings_count']} ratings")
    if not result1['valid']:
        print(f"    ⚠ Integrity issues: missing_books={result1['missing_books']}, "
              f"missing_users={result1['missing_users']}")
    
    # Create set2 (20% rating shuffle, different user order)
    result2 = create_dataset_split(
        "set2",
        books=books,
        users=shuffled_users,  # Different user order for variation
        ratings=ratings,
        shuffle_factor=0.2
    )
    print(f"  ✓ {result2['split']}: {result2['books_count']} books, "
          f"{result2['users_count']} users, {result2['ratings_count']} ratings (20% rating shuffle)")
    
    # Create set3 (40% rating shuffle, different user order)
    shuffled_users_2 = users.copy()
    random.shuffle(shuffled_users_2)
    result3 = create_dataset_split(
        "set3",
        books=books,
        users=shuffled_users_2,  # Another different user order
        ratings=ratings,
        shuffle_factor=0.4
    )
    print(f"  ✓ {result3['split']}: {result3['books_count']} books, "
          f"{result3['users_count']} users, {result3['ratings_count']} ratings (40% rating shuffle)")
    
    # Verify JSON validity
    print("\n[4/5] Validating JSON format...")
    for split in ["set1", "set2", "set3"]:
        split_path = OUTPUT_BASE / split
        for json_file in ["books.json", "users.json"]:
            file_path = split_path / json_file
            try:
                with open(file_path, 'r') as f:
                    json.load(f)
                print(f"  ✓ {split}/{json_file} is valid JSON")
            except Exception as e:
                print(f"  ✗ {split}/{json_file} is invalid: {e}")
    
    # Summary
    print("\n[5/5] Refactoring Complete!")
    print("=" * 70)
    print("\nDataset Structure Created:")
    print("  dataset/")
    print("    set1/  (Original data)")
    print("      ├── books.json")
    print("      ├── users.json")
    print("      └── ratings.csv")
    print("    set2/  (20% rating variation)")
    print("      ├── books.json")
    print("      ├── users.json")
    print("      └── ratings.csv")
    print("    set3/  (40% rating variation)")
    print("      ├── books.json")
    print("      ├── users.json")
    print("      └── ratings.csv")
    
    print("\n✓ All files created successfully with referential integrity maintained!")
    print("=" * 70)


if __name__ == "__main__":
    main()
