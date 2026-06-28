# Quick Start Guide - E-Library System

## Prerequisites

- Python 3.11+
- MongoDB running on localhost:27017
- pip (Python package manager)

## Setup Steps

### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Initialize Database
```bash
python setup_mongodb.py
```

This creates:
- All MongoDB collections
- Default admin account: `admin` / `admin123`
- Imports datasets (set1, set2, set3)

### 4. Run Application
```bash
python app.py
```

App will start at: **http://localhost:5000**

## Login Credentials

### Admin Access
- URL: `http://localhost:5000/admin/login`
- Username: `admin`
- Password: `admin123`

### User Access
- URL: `http://localhost:5000/login`
- Sign up first at: `http://localhost:5000/signup`
- Login with username or email

### Author Access
- URL: `http://localhost:5000/author/login`
- Sign up first at: `http://localhost:5000/author/signup`
- Must be approved by admin before can login

## Main Features

### For Users
- ✅ Browse and search books
- ✅ Save books
- ✅ Rate books
- ✅ View recommendations
- ✅ Track reading history

### For Authors
- ✅ Upload books (pending approval)
- ✅ View my books (Approved/Pending/Rejected)
- ✅ Edit book details
- ✅ Delete books

### For Admins
- ✅ Approve/Reject authors
- ✅ Approve/Reject/Delete books
- ✅ Manage users (Suspend/Delete)
- ✅ Manage authors (Approve/Reject/Suspend/Delete)
- ✅ Manage books (Approve/Reject/Delete)

## Test Workflow

### 1. Admin Approves Authors
1. Login as admin
2. Go to `/admin/manage-authors`
3. Click approve for pending authors

### 2. Author Uploads Books
1. Login as author (after approval)
2. Go to `/author/upload-book`
3. Fill form and submit
4. Books appear in "Pending" section

### 3. Admin Approves Books
1. Login as admin
2. Go to `/admin/manage-books`
3. Approve pending books

### 4. User Views Approved Books
1. Login as user
2. Go to `/` or `/books`
3. Browse approved books

## Important Files

```
app.py                          - Main Flask application
setup_mongodb.py               - MongoDB initialization
database/db.py                 - Database functions
model/hybrid.py               - Recommendation engine
templates/                     - All HTML templates
requirements.txt              - Python dependencies
```

## Troubleshooting

### MongoDB Connection Error
- Ensure MongoDB is running: `mongod`
- Check connection string in `database/db.py`

### Dependencies Not Installing
```bash
# Try with system Python
pip install --upgrade setuptools wheel
pip install -r requirements.txt
```

### Port 5000 Already in Use
```bash
# Use different port in app.py
app.run(debug=True, host="0.0.0.0", port=5001)
```

## Project Structure

```
E-Library/
├── app.py                      # Main Flask app
├── setup_mongodb.py           # Database setup
├── requirements.txt           # Dependencies
├── database/
│   └── db.py                 # MongoDB functions
├── model/
│   ├── hybrid.py             # Hybrid recommendation
│   ├── content_based.py       # Content-based filtering
│   ├── knn_recommend.py       # KNN recommendation
│   ├── recommender.py         # Recommendation interface
│   └── train.py              # Model training
├── dataset/
│   ├── set1/                 # STEM books dataset
│   ├── set2/                 # Humanities dataset
│   └── set3/                 # Random mix dataset
├── templates/
│   ├── base.html             # Base template
│   ├── login.html            # User login
│   ├── signup.html           # User signup
│   ├── admin_login.html      # Admin login
│   ├── admin_dashboard.html  # Admin main page
│   ├── admin_manage_*.html   # Admin management pages
│   ├── author_login.html     # Author login
│   ├── author_signup.html    # Author signup
│   ├── author_dashboard.html # Author main page
│   ├── author_upload_book.html
│   ├── author_my_books.html
│   ├── author_edit_book.html
│   ├── user_dashboard.html   # User dashboard
│   ├── homepage.html         # Home page
│   ├── books_list.html       # Books listing
│   ├── book_detail.html      # Book details
│   └── search_results.html   # Search results
└── static/                    # CSS, JS, images
```

## Database Schema

### Collections
- **users** - User accounts and preferences
- **authors** - Author profiles and status
- **admins** - System administrators
- **books** - Book catalog with approval status
- **ratings** - User ratings on books
- **saved_books** - User saved books
- **book_views** - Book view tracking
- **reading_history** - User reading history
- **notifications** - User notifications
- **author_requests** - Author approval status
- **recommendation_history** - Recommendation tracking

## API Endpoints

### Admin APIs
```
POST /api/admin/suspend-user/<id>
POST /api/admin/delete-user/<id>
POST /api/admin/suspend-author/<id>
POST /api/admin/delete-author/<id>
POST /api/admin/approve-book/<id>
POST /api/admin/reject-book/<id>
POST /api/admin/delete-book/<id>
```

### Author APIs
```
POST /api/author/delete-book/<id>
POST /api/approve-author/<id>
POST /api/reject-author/<id>
```

### User APIs
```
POST /api/save-book/<id>
POST /api/unsave-book/<id>
POST /api/rate-book/<id>
```

## Support & Documentation

For more details, see:
- `IMPLEMENTATION_COMPLETE.md` - Full feature documentation
- `README.md` - Project overview
- `INSTALL.md` - Detailed installation

---

**Version**: 1.0.0  
**Last Updated**: June 2024  
**Status**: Production Ready ✅
