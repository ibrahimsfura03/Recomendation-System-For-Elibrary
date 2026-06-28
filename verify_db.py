#!/usr/bin/env python3

from database.db import get_db, connect_db

def verify_setup():
    print("Verifying MongoDB Setup...\n")
    
    if not connect_db():
        print("✗ MongoDB connection failed")
        return False
    
    db = get_db()
    
    collections = db.list_collection_names()
    print(f"Collections ({len(collections)}):")
    for col in collections:
        count = db[col].count_documents({})
        print(f"  • {col}: {count} documents")
    
    print("\n--- Document Counts by Collection ---")
    
    for col in collections:
        print(f"\n{col}:")
        if col == "users":
            stem_count = db.users.count_documents({"dataset": "set1"})
            hum_count = db.users.count_documents({"dataset": "set2"})
            rand_count = db.users.count_documents({"dataset": "set3"})
            print(f"  set1: {stem_count} users")
            print(f"  set2: {hum_count} users")
            print(f"  set3: {rand_count} users")
        
        elif col == "books":
            set1_count = db.books.count_documents({"dataset": "set1"})
            set2_count = db.books.count_documents({"dataset": "set2"})
            set3_count = db.books.count_documents({"dataset": "set3"})
            print(f"  set1: {set1_count} books")
            print(f"  set2: {set2_count} books")
            print(f"  set3: {set3_count} books")
        
        elif col == "ratings":
            set1_count = db.ratings.count_documents({"dataset": "set1"})
            set2_count = db.ratings.count_documents({"dataset": "set2"})
            set3_count = db.ratings.count_documents({"dataset": "set3"})
            print(f"  set1: {set1_count} ratings")
            print(f"  set2: {set2_count} ratings")
            print(f"  set3: {set3_count} ratings")
    
    print("\n✓ Verification complete!")
    return True

if __name__ == "__main__":
    verify_setup()
