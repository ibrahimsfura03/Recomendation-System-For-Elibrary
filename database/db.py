from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os
from datetime import datetime
import json
import pandas as pd
from pathlib import Path

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "elibrary"

client = None
db = None

def connect_db():
    global client, db
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client[DB_NAME]
        print("✓ MongoDB connected successfully")
        return True
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"✗ MongoDB connection failed: {e}")
        return False

def get_db():
    global db
    if db is None:
        connect_db()
    return db

def create_collections():
    database = get_db()
    if database is None:
        return False
    
    collections_to_create = [
        "users",
        "authors",
        "admins",
        "books",
        "ratings",
        "recommendation_history",
        "saved_books",
        "book_views",
        "reading_history",
        "author_requests",
        "notifications"
    ]
    
    existing_collections = database.list_collection_names()
    
    for collection in collections_to_create:
        if collection not in existing_collections:
            database.create_collection(collection)
            print(f"✓ Created collection: {collection}")
    
    create_indexes()
    return True

def create_indexes():
    database = get_db()
    
    try:
        database.users.create_index("user_id")
        database.users.create_index("email", unique=True)
        database.users.create_index("username", unique=True)
        
        database.books.create_index("book_id")
        database.books.create_index("category")
        database.books.create_index("title")
        database.books.create_index("author")
        
        database.ratings.create_index([("user_id", 1), ("book_id", 1), ("dataset", 1)], unique=True)
        database.ratings.create_index("user_id")
        
        database.authors.create_index("author_id", unique=True)
        database.authors.create_index("email", unique=True)
        database.authors.create_index("username", unique=True)
        
        database.admins.create_index("username", unique=True)
        
        database.saved_books.create_index([("user_id", 1), ("book_id", 1)], unique=True)
        database.saved_books.create_index("user_id")
        
        database.book_views.create_index("user_id")
        database.book_views.create_index("book_id")
        
        database.reading_history.create_index("user_id")
        database.reading_history.create_index("book_id")
        
        database.author_requests.create_index("author_id")
        database.author_requests.create_index("status")
        
        database.notifications.create_index("user_id")
        database.notifications.create_index("created_at")
        
        print("✓ Indexes created")
    except Exception as e:
        print(f"Indexes update: {e}")

def import_datasets():
    database = get_db()
    
    dataset_path = Path("dataset")
    datasets = ["set1", "set2", "set3"]
    
    for dataset_name in datasets:
        print(f"\nImporting {dataset_name}...")
        
        books_file = dataset_path / dataset_name / "books.json"
        users_file = dataset_path / dataset_name / "users.json"
        ratings_file = dataset_path / dataset_name / "ratings.csv"
        
        if books_file.exists():
            with open(books_file, "r") as f:
                books_data = json.load(f)
                books_list = books_data.get("books", [])
                
                for book in books_list:
                    book_id = book["book_id"]
                    book["dataset"] = dataset_name
                    book["imported_date"] = datetime.now()
                    database.books.insert_one(book)
                print(f"  ✓ Imported {len(books_list)} books from {dataset_name}")
        
        if users_file.exists():
            with open(users_file, "r") as f:
                users_data = json.load(f)
                users_list = users_data.get("users", [])
                
                for user in users_list:
                    user["role"] = "user"
                    user["dataset"] = dataset_name
                    user["joined_date"] = user.get("joined_date", str(datetime.now().date()))
                    user["saved_books"] = []
                    user["reading_history"] = []
                    user["imported_date"] = datetime.now()
                    
                    database.users.insert_one(user)
                print(f"  ✓ Imported {len(users_list)} users from {dataset_name}")
        
        if ratings_file.exists():
            df = pd.read_csv(ratings_file)
            
            for idx, row in df.iterrows():
                rating_doc = {
                    "user_id": row["user_id"],
                    "book_id": row["book_id"],
                    "rating": int(row["rating"]),
                    "rated_at": datetime.now(),
                    "dataset": dataset_name
                }
                try:
                    database.ratings.insert_one(rating_doc)
                except:
                    pass
            print(f"  ✓ Imported {len(df)} ratings from {dataset_name}")

def get_books_by_dataset(dataset="set2"):
    database = get_db()
    books = list(database.books.find({"dataset": dataset}))
    return {book["book_id"]: book for book in books}

def get_users_by_dataset(dataset="set2"):
    database = get_db()
    users = list(database.users.find({"dataset": dataset}))
    return users

def get_ratings_by_dataset(dataset="set2"):
    database = get_db()
    ratings = list(database.ratings.find({"dataset": dataset}))
    df = pd.DataFrame([{
        "user_id": r["user_id"],
        "book_id": r["book_id"],
        "rating": r["rating"]
    } for r in ratings])
    return df

def save_recommendation_history(user_id, recommended_books, engine_type, dataset="set2"):
    database = get_db()
    
    history_doc = {
        "user_id": user_id,
        "recommended_books": recommended_books,
        "recommendation_engine": engine_type,
        "dataset": dataset,
        "timestamp": datetime.now()
    }
    
    result = database.recommendation_history.insert_one(history_doc)
    return str(result.inserted_id)

def initialize_db():
    if not connect_db():
        return False
    
    if not create_collections():
        return False
    
    import_datasets()
    return True

def get_user_by_email(email):
    database = get_db()
    return database.users.find_one({"email": email})

def get_user_by_username(username):
    database = get_db()
    return database.users.find_one({"username": username})

def get_author_by_email(email):
    database = get_db()
    return database.authors.find_one({"email": email})

def get_book_by_id(book_id):
    database = get_db()
    return database.books.find_one({"book_id": book_id})

def save_book_to_user(user_id, book_id):
    database = get_db()
    saved_doc = {
        "user_id": user_id,
        "book_id": book_id,
        "saved_at": datetime.now()
    }
    try:
        database.saved_books.insert_one(saved_doc)
        return True
    except:
        return False

def unsave_book_from_user(user_id, book_id):
    database = get_db()
    database.saved_books.delete_one({"user_id": user_id, "book_id": book_id})
    return True

def is_book_saved(user_id, book_id):
    database = get_db()
    return database.saved_books.find_one({"user_id": user_id, "book_id": book_id}) is not None

def get_saved_books(user_id):
    database = get_db()
    saved = list(database.saved_books.find({"user_id": user_id}))
    book_ids = [s["book_id"] for s in saved]
    books = list(database.books.find({"book_id": {"$in": book_ids}}))
    return books

def log_book_view(user_id, book_id):
    database = get_db()
    view_doc = {
        "user_id": user_id,
        "book_id": book_id,
        "viewed_at": datetime.now()
    }
    database.book_views.insert_one(view_doc)

def get_reading_history(user_id):
    database = get_db()
    history = list(database.reading_history.find({"user_id": user_id}).sort("read_at", -1))
    return history

def add_to_reading_history(user_id, book_id):
    database = get_db()
    history_doc = {
        "user_id": user_id,
        "book_id": book_id,
        "read_at": datetime.now()
    }
    database.reading_history.insert_one(history_doc)

def create_notification(user_id, message, notification_type="info"):
    database = get_db()
    notif_doc = {
        "user_id": user_id,
        "message": message,
        "type": notification_type,
        "read": False,
        "created_at": datetime.now()
    }
    result = database.notifications.insert_one(notif_doc)
    return str(result.inserted_id)

def get_notifications(user_id):
    database = get_db()
    return list(database.notifications.find({"user_id": user_id}).sort("created_at", -1))

def get_pending_authors():
    database = get_db()
    return list(database.author_requests.find({"status": "pending"}))

def approve_author(author_id):
    database = get_db()
    database.author_requests.update_one(
        {"author_id": author_id},
        {"$set": {"status": "approved", "approved_at": datetime.now()}}
    )

def reject_author(author_id, reason=""):
    database = get_db()
    database.author_requests.update_one(
        {"author_id": author_id},
        {"$set": {"status": "rejected", "reason": reason, "rejected_at": datetime.now()}}
    )

def search_books(query, dataset="set2"):
    database = get_db()
    books = list(database.books.find({
        "dataset": dataset,
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"author": {"$regex": query, "$options": "i"}},
            {"category": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}}
        ]
    }))
    return books

def search_user_books(query):
    """Search user-uploaded books (approved only, no datasets)"""
    database = get_db()
    books = list(database.books.find({
        "status": "approved",
        "uploaded_by": {"$exists": True},
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"author": {"$regex": query, "$options": "i"}},
            {"category": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}}
        ]
    }))
    return books

def get_books_by_category(category, dataset="set2"):
    database = get_db()
    books = list(database.books.find({"category": category, "dataset": dataset}))
    return books

def get_all_categories(dataset="set2"):
    database = get_db()
    # Get categories from existing books
    categories = database.books.distinct("category")
    
    # Default categories to offer to authors
    default_categories = [
        "Fiction",
        "Non-Fiction",
        "Science",
        "History",
        "Biography",
        "Romance",
        "Mystery",
        "Thriller",
        "Fantasy",
        "Science Fiction",
        "Self-Help",
        "Business",
        "Technology",
        "Education",
        "Children",
        "Poetry",
        "Drama",
        "Art & Design"
    ]
    
    # Combine existing categories with defaults, remove duplicates
    all_cats = list(set(categories + default_categories))
    return sorted(all_cats)

