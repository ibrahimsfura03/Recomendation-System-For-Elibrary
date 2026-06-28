#!/usr/bin/env python3

from database.db import get_db
from datetime import datetime
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

db = get_db()

test_users = [
    {
        "user_id": "U_TEST_001",
        "full_name": "John Doe",
        "username": "johndoe",
        "email": "john@example.com",
        "password": hash_password("password123"),
        "role": "user",
        "joined_date": str(datetime.now().date()),
        "preferred_categories": ["Computer Science"],
        "saved_books": [],
        "reading_history": [],
        "created_at": datetime.now()
    },
    {
        "user_id": "U_TEST_002",
        "full_name": "Jane Smith",
        "username": "janesmith",
        "email": "jane@example.com",
        "password": hash_password("password123"),
        "role": "user",
        "joined_date": str(datetime.now().date()),
        "preferred_categories": ["Literature"],
        "saved_books": [],
        "reading_history": [],
        "created_at": datetime.now()
    }
]

test_authors = [
    {
        "author_id": "A_TEST_001",
        "full_name": "Bob Author",
        "username": "bobauthor",
        "email": "bob@author.com",
        "phone": "+1234567890",
        "password": hash_password("password123"),
        "biography": "Experienced author in technology",
        "institution": "Tech University",
        "expertise": "Technology, Science Fiction",
        "uploaded_books": [],
        "status": "approved",
        "role": "author",
        "created_at": datetime.now()
    }
]

print("Creating test users...")
for user in test_users:
    db.users.update_one(
        {"username": user["username"]},
        {"$set": user},
        upsert=True
    )
    print(f"  ✓ Created user: {user['email']}")

print("\nCreating test authors...")
for author in test_authors:
    db.authors.update_one(
        {"username": author["username"]},
        {"$set": author},
        upsert=True
    )
    print(f"  ✓ Created author: {author['email']}")

print("\nTest Credentials:")
print("Users:")
for user in test_users:
    print(f"  Email: {user['email']}, Password: password123")
print("\nAuthors:")
for author in test_authors:
    print(f"  Email: {author['email']}, Password: password123")
