from model.content_based import train_content_model, recommend_similar_books
from database.db import initialize_db, get_books_by_dataset

initialize_db()

dataset = "set1"
books = get_books_by_dataset(dataset)

similarity = train_content_model(books)

book_id = input("Enter a book ID: ")

results = recommend_similar_books(book_id, books, similarity)

for i, r in enumerate(results, 1):
    print(f"{i}. {r['title']}")
    print(f"   Author: {r['author']}")
    print(f"   Score : {r['score']:.2f}\n")
