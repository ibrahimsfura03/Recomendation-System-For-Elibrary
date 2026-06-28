#!/usr/bin/env python3

import sys
from database.db import initialize_db, get_db
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_admin(username, password, full_name):
    db = get_db()
    
    admin_doc = {
        "admin_id": f"ADMIN_{username}",
        "username": username,
        "password": hash_password(password),
        "full_name": full_name
    }
    
    result = db.admins.update_one(
        {"username": username},
        {"$set": admin_doc},
        upsert=True
    )
    
    return result

def create_author(author_id, name, email, password, biography=""):
    db = get_db()
    
    author_doc = {
        "author_id": author_id,
        "full_name": name,
        "email": email,
        "password": hash_password(password),
        "biography": biography,
        "uploaded_books": [],
        "status": "active",
        "role": "author"
    }
    
    result = db.authors.update_one(
        {"author_id": author_id},
        {"$set": author_doc},
        upsert=True
    )
    
    return result

def main():
    print("Setting up MongoDB for E-Library System...")
    
    if not initialize_db():
        print("Failed to initialize database")
        sys.exit(1)
    
    print("\nCreating default admin account...")
    create_admin("admin", "admin123", "System Administrator")
    print("✓ Admin created: username='admin', password='admin123'")
    
    print("\nDatabase setup complete!")
    print("\nNext steps:")
    print("1. Start the application: python app.py")
    print("2. Admin login: http://localhost:5000/admin/login")
    print("3. User login: http://localhost:5000/login")
    print("4. Author login: http://localhost:5000/author/login")

if __name__ == "__main__":
    main()
