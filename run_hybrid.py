from model.hybrid import hybrid_recommend
from database.db import initialize_db

initialize_db()

dataset = input("Enter dataset: ")
user_id = input("Enter user ID: ")
book_id = input("Enter a reference book ID (optional, press enter to skip): ")

if book_id == "":
    book_id = None

results = hybrid_recommend(user_id, dataset, book_id)

print("\nHYBRID RECOMMENDATIONS\n")

for i, r in enumerate(results, 1):
    print(f"{i}. {r['title']}")
    print(f"   Author: {r['author']}")
    print(f"   Score : {r['score']:.2f}\n")
