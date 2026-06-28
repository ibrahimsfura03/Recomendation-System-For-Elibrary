import pandas as pd
from surprise import Dataset, Reader, KNNBasic
from database.db import get_books_by_dataset, get_ratings_by_dataset

def train_model(df):
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df[["user_id", "book_id", "rating"]], reader)
    trainset = data.build_full_trainset()

    sim_options = {"name": "cosine", "user_based": True}
    model = KNNBasic(sim_options=sim_options)
    model.fit(trainset)

    return model, trainset

def recommend(user_id, dataset_name):
    books = get_books_by_dataset(dataset_name)
    df = get_ratings_by_dataset(dataset_name)

    model, trainset = train_model(df)

    all_books = set(df["book_id"].unique())
    user_books = set(df[df["user_id"] == user_id]["book_id"].unique())
    unseen_books = all_books - user_books

    predictions = []

    for book_id in unseen_books:
        pred = model.predict(user_id, book_id)
        predictions.append((book_id, pred.est))

    predictions.sort(key=lambda x: x[1], reverse=True)

    result = []
    for book_id, score in predictions[:5]:
        book = books.get(book_id, {})
        result.append({
            "book_id": book_id,
            "title": book.get("title", ""),
            "author": book.get("author", ""),
            "score": score
        })

    return result
