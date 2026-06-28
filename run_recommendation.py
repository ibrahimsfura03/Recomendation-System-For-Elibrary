from model.recommender import recommend
from database.db import initialize_db

initialize_db()

dataset = input("Enter dataset (set1/set2/set3): ")
user_id = input("Enter user ID: ")

results = recommend(user_id, dataset)

for r in results:
    print("\nTOP RECOMMENDATIONS\n")

for i, r in enumerate(results, 1):
    print(f"{i}. {r['title']}")
    print(f"   Author : {r['author']}")
    print(f"   Score  : {r['score']:.2f}\n")

