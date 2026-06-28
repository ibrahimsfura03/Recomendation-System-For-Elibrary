from flask import Flask, render_template, request, session, redirect, url_for, jsonify, send_file
from database.db import get_db, get_books_by_dataset, get_all_categories, search_books, search_user_books, get_saved_books, get_reading_history, get_notifications, get_user_by_email, get_user_by_username, get_author_by_email
from model.hybrid import hybrid_recommend
import bcrypt
from datetime import datetime
import os
from functools import wraps
from werkzeug.utils import secure_filename
import mimetypes

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super_secret_e_library_key_prod")

# Upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'jpg', 'jpeg', 'png', 'gif'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

from database.db import initialize_db
if not initialize_db():
    print("Warning: MongoDB initialization")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """Save uploaded file with secure filename and return path"""
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        return None
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    if file_length > MAX_FILE_SIZE:
        return None
    file.seek(0)
    
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
    filename = timestamp + filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return filename

def hash_password(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def verify_pwd(pwd, hashed):
    try:
        return bcrypt.checkpw(pwd.encode(), hashed.encode())
    except:
        return False

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("user_role") != "user":
            return redirect(url_for("user_login"))
        return f(*args, **kwargs)
    return decorated

def author_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("user_role") != "author":
            return redirect(url_for("author_login"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("user_role") != "admin":
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def homepage():
    db = get_db()
    
    # Only show approved user-uploaded books (exclude datasets)
    books = list(db.books.find({
        "status": "approved",
        "uploaded_by": {"$exists": True}
    }).limit(20))
    
    # Get categories from approved books only
    categories = db.books.distinct("category", {
        "status": "approved",
        "uploaded_by": {"$exists": True}
    })
    
    context = {
        "books": books,
        "categories": categories,
        "user": session.get("username", None) if session.get("user_role") == "user" else None
    }
    
    return render_template("homepage.html", **context)

@app.route("/signup", methods=["GET", "POST"])
def user_signup():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        category = request.form.get("category", "")
        
        db = get_db()
        
        errors = []
        if not full_name:
            errors.append("Full name required")
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters")
        if not email or "@" not in email:
            errors.append("Valid email required")
        if password != confirm:
            errors.append("Passwords don't match")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters")
        
        if db.users.find_one({"email": email}):
            errors.append("Email already registered")
        if db.users.find_one({"username": username}):
            errors.append("Username already taken")
        
        if errors:
            return render_template("signup.html", errors=errors, categories=get_all_categories())
        
        user_doc = {
            "user_id": f"U{db.users.count_documents({}) + 1001}",
            "full_name": full_name,
            "username": username,
            "email": email,
            "password": hash_password(password),
            "role": "user",
            "joined_date": datetime.now(),
            "preferred_categories": [category] if category else [],
            "saved_books": [],
            "reading_history": [],
            "created_at": datetime.now()
        }
        
        db.users.insert_one(user_doc)
        return redirect(url_for("user_login"))
    
    return render_template("signup.html", categories=get_all_categories())

@app.route("/login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")
        
        db = get_db()
        user = None
        
        if "@" in identifier:
            user = db.users.find_one({"email": identifier})
        else:
            user = db.users.find_one({"username": identifier})
        
        if user and verify_pwd(password, user.get("password", "")):
            session["user_id"] = user["user_id"]
            session["user_role"] = "user"
            session["username"] = user.get("username", "")
            session["email"] = user.get("email", "")
            return redirect(url_for("user_dashboard"))
        else:
            return render_template("login.html", error="Invalid username/email or password")
    
    return render_template("login.html")

@app.route("/user/dashboard")
@login_required
def user_dashboard():
    db = get_db()
    user_id = session.get("user_id")
    user = db.users.find_one({"user_id": user_id})
    
    if not user:
        return redirect(url_for("user_login"))
    
    saved_books_ids = user.get("saved_books", [])
    saved_books = list(db.books.find({"book_id": {"$in": saved_books_ids}})) if saved_books_ids else []
    
    reading_hist = user.get("reading_history", [])
    
    try:
        recommendations = hybrid_recommend(user_id, "set2")[:6]
    except:
        recommendations = []
    
    recent_books = list(db.books.find({}).sort("imported_date", -1).limit(5))
    
    context = {
        "user": user,
        "recommendations": recommendations,
        "saved_books": saved_books,
        "reading_history": reading_hist,
        "recent_books": recent_books,
        "notifications": get_notifications(user_id)
    }
    
    return render_template("user_dashboard.html", **context)

@app.route("/books")
def books_list():
    db = get_db()
    category = request.args.get("category", "")
    
    # Filter: approved books only, no datasets
    filter_query = {"status": "approved", "uploaded_by": {"$exists": True}}
    
    if category:
        filter_query["category"] = category
        books = list(db.books.find(filter_query))
    else:
        books = list(db.books.find(filter_query).limit(50))
    
    categories = db.books.distinct("category", {
        "status": "approved",
        "uploaded_by": {"$exists": True}
    })
    
    return render_template("books_list.html", books=books, categories=categories, selected_category=category)

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    results = []
    
    if query:
        results = search_user_books(query)
    
    return render_template("search_results.html", results=results, query=query)

@app.route("/book/<book_id>")
def view_book(book_id):
    db = get_db()
    book = db.books.find_one({"book_id": book_id})
    
    if not book:
        return "Book not found", 404
    
    if session.get("user_role") == "user":
        user_id = session.get("user_id")
        db.book_views.insert_one({
            "user_id": user_id,
            "book_id": book_id,
            "viewed_at": datetime.now()
        })
        
        user = db.users.find_one({"user_id": user_id})
        if book_id not in user.get("reading_history", []):
            db.users.update_one(
                {"user_id": user_id},
                {"$push": {"reading_history": book_id}}
            )
    
    is_saved = False
    if session.get("user_role") == "user":
        is_saved = db.saved_books.find_one({
            "user_id": session.get("user_id"),
            "book_id": book_id
        }) is not None
    
    ratings = list(db.ratings.find({"book_id": book_id}))
    avg_rating = sum([r["rating"] for r in ratings]) / len(ratings) if ratings else 0
    
    try:
        recommendations = hybrid_recommend(session.get("user_id", "U001"), "set2")[:5]
    except:
        recommendations = []
    
    context = {
        "book": book,
        "is_saved": is_saved,
        "avg_rating": avg_rating,
        "total_ratings": len(ratings),
        "recommendations": recommendations
    }
    
    return render_template("book_detail.html", **context)

@app.route("/api/save-book/<book_id>", methods=["POST"])
@login_required
def save_book(book_id):
    db = get_db()
    user_id = session.get("user_id")
    
    result = db.saved_books.update_one(
        {"user_id": user_id, "book_id": book_id},
        {"$set": {"user_id": user_id, "book_id": book_id, "saved_at": datetime.now()}},
        upsert=True
    )
    
    db.users.update_one(
        {"user_id": user_id},
        {"$addToSet": {"saved_books": book_id}}
    )
    
    return jsonify({"success": True})

@app.route("/api/unsave-book/<book_id>", methods=["POST"])
@login_required
def unsave_book(book_id):
    db = get_db()
    user_id = session.get("user_id")
    
    db.saved_books.delete_one({"user_id": user_id, "book_id": book_id})
    db.users.update_one(
        {"user_id": user_id},
        {"$pull": {"saved_books": book_id}}
    )
    
    return jsonify({"success": True})

@app.route("/api/rate-book/<book_id>", methods=["POST"])
@login_required
def rate_book(book_id):
    db = get_db()
    user_id = session.get("user_id")
    rating = request.json.get("rating", 0)
    
    if rating < 1 or rating > 5:
        return jsonify({"success": False}), 400
    
    rating_doc = {
        "user_id": user_id,
        "book_id": book_id,
        "rating": int(rating),
        "rated_at": datetime.now(),
        "dataset": "set2"
    }
    
    db.ratings.update_one(
        {"user_id": user_id, "book_id": book_id},
        {"$set": rating_doc},
        upsert=True
    )
    
    return jsonify({"success": True})

@app.route("/author/signup", methods=["GET", "POST"])
def author_signup():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        bio = request.form.get("biography", "").strip()
        institution = request.form.get("institution", "").strip()
        expertise = request.form.get("expertise", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        
        db = get_db()
        
        errors = []
        if not full_name or not username or not email or not phone or not password:
            errors.append("All required fields must be filled")
        if password != confirm:
            errors.append("Passwords don't match")
        if db.authors.find_one({"email": email}):
            errors.append("Email already registered")
        if db.authors.find_one({"username": username}):
            errors.append("Username already taken")
        
        if errors:
            return render_template("author_signup.html", errors=errors)
        
        author_doc = {
            "author_id": f"A{db.authors.count_documents({}) + 1001}",
            "full_name": full_name,
            "username": username,
            "email": email,
            "phone": phone,
            "password": hash_password(password),
            "biography": bio,
            "institution": institution,
            "expertise": expertise,
            "uploaded_books": [],
            "status": "pending",
            "role": "author",
            "created_at": datetime.now()
        }
        
        db.authors.insert_one(author_doc)
        return redirect(url_for("author_login"))
    
    return render_template("author_signup.html")

@app.route("/author/login", methods=["GET", "POST"])
def author_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        
        author = get_author_by_email(email)
        
        if author and verify_pwd(password, author.get("password", "")):
            if author.get("status") != "approved":
                return render_template("author_login.html", error="Account pending approval")
            
            session["author_id"] = author["author_id"]
            session["user_role"] = "author"
            session["username"] = author.get("username", "")
            return redirect(url_for("author_dashboard"))
        else:
            return render_template("author_login.html", error="Invalid email or password")
    
    return render_template("author_login.html")

@app.route("/author/dashboard")
@author_required
def author_dashboard():
    db = get_db()
    author_id = session.get("author_id")
    author = db.authors.find_one({"author_id": author_id})
    
    if not author:
        return redirect(url_for("author_login"))
    
    books = list(db.books.find({"uploaded_by": author_id}))
    
    context = {
        "author": author,
        "books": books,
        "stats": {
            "total_books": len(books),
            "approved": len([b for b in books if b.get("status") == "approved"]),
            "pending": len([b for b in books if b.get("status") == "pending"]),
            "rejected": len([b for b in books if b.get("status") == "rejected"])
        }
    }
    
    return render_template("author_dashboard.html", **context)

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        db = get_db()
        admin = db.admins.find_one({"username": username})
        
        if admin and verify_pwd(password, admin.get("password", "")):
            session["admin_id"] = admin["admin_id"]
            session["user_role"] = "admin"
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("admin_login.html", error="Invalid username or password")
    
    return render_template("admin_login.html")

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    db = get_db()
    
    # Count user-uploaded books only (exclude datasets)
    user_books_filter = {"uploaded_by": {"$exists": True}}
    
    stats = {
        "total_users": db.users.count_documents({}),
        "total_authors": db.authors.count_documents({}),
        "total_books": db.books.count_documents(user_books_filter),
        "total_ratings": db.ratings.count_documents({}),
        "pending_authors": db.authors.count_documents({"status": "pending"}),
        "pending_books": db.books.count_documents({"status": "pending", **user_books_filter})
    }
    
    pending_authors = list(db.authors.find({"status": "pending"}))
    
    context = {
        "stats": stats,
        "pending_authors": pending_authors
    }
    
    return render_template("admin_dashboard.html", **context)

@app.route("/api/approve-author/<author_id>", methods=["POST"])
@admin_required
def approve_author(author_id):
    db = get_db()
    db.authors.update_one(
        {"author_id": author_id},
        {"$set": {"status": "approved", "approved_at": datetime.now()}}
    )
    return jsonify({"success": True})

@app.route("/api/reject-author/<author_id>", methods=["POST"])
@admin_required
def reject_author(author_id):
    reason = request.json.get("reason", "")
    db = get_db()
    db.authors.update_one(
        {"author_id": author_id},
        {"$set": {"status": "rejected", "reason": reason, "rejected_at": datetime.now()}}
    )
    return jsonify({"success": True})

# ====== ADMIN MANAGEMENT PAGES ======

@app.route("/admin/manage-users")
@admin_required
def manage_users():
    db = get_db()
    users = list(db.users.find({}))
    return render_template("admin_manage_users.html", users=users)

@app.route("/admin/manage-authors")
@admin_required
def manage_authors():
    db = get_db()
    authors = list(db.authors.find({}))
    return render_template("admin_manage_authors.html", authors=authors)

@app.route("/admin/manage-books")
@admin_required
def manage_books():
    db = get_db()
    # Only show user-uploaded books (exclude datasets)
    books = list(db.books.find({"uploaded_by": {"$exists": True}}))
    return render_template("admin_manage_books.html", books=books)

# ====== ADMIN USER MANAGEMENT APIS ======

@app.route("/api/admin/suspend-user/<user_id>", methods=["POST"])
@admin_required
def suspend_user(user_id):
    db = get_db()
    db.users.update_one(
        {"user_id": user_id},
        {"$set": {"status": "suspended", "suspended_at": datetime.now()}}
    )
    return jsonify({"success": True})

@app.route("/api/admin/delete-user/<user_id>", methods=["POST"])
@admin_required
def delete_user(user_id):
    db = get_db()
    db.users.delete_one({"user_id": user_id})
    db.saved_books.delete_many({"user_id": user_id})
    db.ratings.delete_many({"user_id": user_id})
    return jsonify({"success": True})

# ====== ADMIN AUTHOR MANAGEMENT APIS ======

@app.route("/api/admin/suspend-author/<author_id>", methods=["POST"])
@admin_required
def suspend_author(author_id):
    db = get_db()
    db.authors.update_one(
        {"author_id": author_id},
        {"$set": {"status": "suspended", "suspended_at": datetime.now()}}
    )
    return jsonify({"success": True})

@app.route("/api/admin/delete-author/<author_id>", methods=["POST"])
@admin_required
def delete_author(author_id):
    db = get_db()
    db.authors.delete_one({"author_id": author_id})
    db.books.delete_many({"uploaded_by": author_id})
    return jsonify({"success": True})

# ====== ADMIN BOOK MANAGEMENT APIS ======

@app.route("/api/admin/approve-book/<book_id>", methods=["POST"])
@admin_required
def approve_book(book_id):
    db = get_db()
    db.books.update_one(
        {"book_id": book_id},
        {"$set": {"status": "approved", "approved_at": datetime.now()}}
    )
    return jsonify({"success": True})

@app.route("/api/admin/reject-book/<book_id>", methods=["POST"])
@admin_required
def reject_book(book_id):
    reason = request.json.get("reason", "")
    db = get_db()
    db.books.update_one(
        {"book_id": book_id},
        {"$set": {"status": "rejected", "reason": reason, "rejected_at": datetime.now()}}
    )
    return jsonify({"success": True})

@app.route("/api/admin/delete-book/<book_id>", methods=["POST"])
@admin_required
def delete_book(book_id):
    db = get_db()
    db.books.delete_one({"book_id": book_id})
    db.ratings.delete_many({"book_id": book_id})
    db.saved_books.delete_many({"book_id": book_id})
    return jsonify({"success": True})

# ====== AUTHOR UPLOAD BOOK ======

@app.route("/author/upload-book", methods=["GET", "POST"])
@author_required
def upload_book():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author_name = request.form.get("author", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        isbn = request.form.get("isbn", "").strip()
        published_year = request.form.get("published_year", "").strip()
        
        # Handle file uploads
        cover_file = request.files.get('cover_image')
        book_file = request.files.get('book_file')
        
        db = get_db()
        author_id = session.get("author_id")
        author = db.authors.find_one({"author_id": author_id})
        
        errors = []
        if not title:
            errors.append("Title required")
        if not author_name:
            errors.append("Author name required")
        if not category:
            errors.append("Category required")
        if not book_file:
            errors.append("Book file (PDF/DOCX) is required")
        
        # Save files
        cover_filename = None
        book_filename = None
        
        if not errors and book_file:
            book_filename = save_uploaded_file(book_file)
            if not book_filename:
                errors.append("Invalid book file (must be PDF or DOCX, max 10MB)")
        
        if not errors and cover_file and cover_file.filename != '':
            cover_filename = save_uploaded_file(cover_file)
            if not cover_filename:
                errors.append("Invalid cover image (JPG/PNG, max 10MB)")
        
        if errors:
            return render_template("author_upload_book.html", errors=errors, categories=get_all_categories())
        
        book_doc = {
            "book_id": f"B{db.books.count_documents({}) + 5001}",
            "title": title,
            "author": author_name,
            "category": category,
            "description": description,
            "isbn": isbn,
            "published_year": published_year,
            "uploaded_by": author_id,
            "status": "pending",
            "cover_image": f"/uploads/{cover_filename}" if cover_filename else None,
            "book_file": f"/uploads/{book_filename}" if book_filename else None,
            "rating": 0,
            "reviews_count": 0,
            "uploaded_date": datetime.now(),
            "imported_date": datetime.now()
        }
        
        db.books.insert_one(book_doc)
        return redirect(url_for("author_dashboard"))
    
    return render_template("author_upload_book.html", categories=get_all_categories())

@app.route("/uploads/<filename>")
def download_file(filename):
    """Serve uploaded files"""
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return "File not found", 404
    except Exception as e:
        return "Error downloading file", 400

# ====== AUTHOR MY BOOKS ======

@app.route("/author/my-books")
@author_required
def author_my_books():
    db = get_db()
    author_id = session.get("author_id")
    
    all_books = list(db.books.find({"uploaded_by": author_id}))
    approved = [b for b in all_books if b.get("status") == "approved"]
    pending = [b for b in all_books if b.get("status") == "pending"]
    rejected = [b for b in all_books if b.get("status") == "rejected"]
    
    context = {
        "all_books": all_books,
        "approved": approved,
        "pending": pending,
        "rejected": rejected
    }
    
    return render_template("author_my_books.html", **context)

@app.route("/api/author/delete-book/<book_id>", methods=["POST"])
@author_required
def author_delete_book(book_id):
    db = get_db()
    author_id = session.get("author_id")
    
    db.books.delete_one({"book_id": book_id, "uploaded_by": author_id})
    db.ratings.delete_many({"book_id": book_id})
    db.saved_books.delete_many({"book_id": book_id})
    
    return jsonify({"success": True})

@app.route("/author/edit-book/<book_id>", methods=["GET", "POST"])
@author_required
def edit_book(book_id):
    db = get_db()
    author_id = session.get("author_id")
    book = db.books.find_one({"book_id": book_id, "uploaded_by": author_id})
    
    if not book:
        return "Book not found", 404
    
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        
        update_data = {
            "title": title,
            "description": description,
            "category": category,
            "updated_at": datetime.now()
        }
        
        # Handle cover image replacement
        cover_file = request.files.get('cover_image')
        if cover_file and cover_file.filename != '':
            cover_filename = save_uploaded_file(cover_file)
            if cover_filename:
                update_data["cover_image"] = f"/uploads/{cover_filename}"
        
        # Handle book file replacement
        book_file = request.files.get('book_file')
        if book_file and book_file.filename != '':
            book_filename = save_uploaded_file(book_file)
            if book_filename:
                update_data["book_file"] = f"/uploads/{book_filename}"
        
        db.books.update_one(
            {"book_id": book_id},
            {"$set": update_data}
        )
        return redirect(url_for("author_my_books"))
    
    return render_template("author_edit_book.html", book=book, categories=get_all_categories())

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("homepage"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
