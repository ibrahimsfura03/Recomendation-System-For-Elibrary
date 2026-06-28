import pandas as pd
from surprise import Dataset, Reader, KNNBasic
from load_books import load_books

books = load_books()

df = pd.read_csv("dataset/interactions.csv")

reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(df[["user_id", "book_id", "rating"]], reader)
trainset = data.build_full_trainset()

sim_options = {
    "name": "cosine",
    "user_based": True
}

model = KNNBasic(sim_options=sim_options)
model.fit(trainset)

user_id = "U001"

all_books = df["book_id"].unique()

rated_books = df[df["user_id"] == user_id]["book_id"].tolist()
unrated_books = [b for b in all_books if b not in rated_books]

predictions = []

for book_id in unrated_books:
    pred = model.predict(user_id, book_id)
    predictions.append((book_id, pred.est))

predictions.sort(key=lambda x: x[1], reverse=True)

print(f"\nTop recommendations for {user_id}:\n")

for book_id, score in predictions[:5]:
    book = books.get(book_id, None)

    if book:
        print(f"{book.get('title', 'Unknown')} by {book.get('author', 'Unknown')} → Score: {score:.2f}")
    else:
        print(f"{book_id} → Score: {score:.2f}")
