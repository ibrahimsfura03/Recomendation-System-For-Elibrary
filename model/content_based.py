from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from database.db import get_books_by_dataset

def build_corpus(books):
    corpus = []
    for b in books.values():
        text = f"{b.get('title','')} {b.get('author','')} {b.get('category','')} {b.get('description','')}"
        corpus.append(text)
    return corpus


def train_content_model(books):
    corpus = build_corpus(books)
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(corpus)
    similarity = cosine_similarity(matrix)
    return similarity


def recommend_similar_books(book_id, books, similarity, top_n=5):
    book_list = list(books.values())

    index_map = {b["book_id"]: i for i, b in enumerate(book_list)}

    if book_id not in index_map:
        return []

    idx = index_map[book_id]
    scores = list(enumerate(similarity[idx]))

    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    results = []

    for i, score in scores[1:top_n + 1]:
        b = book_list[i]

        results.append({
            "book_id": b["book_id"],
            "title": b.get("title", ""),
            "author": b.get("author", ""),
            "score": round(float(score), 2)
        })

    return results
