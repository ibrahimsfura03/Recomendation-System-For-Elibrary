try:
    from model.recommender import recommend
except Exception as e:
    print(f"Warning: KNN recommendation module unavailable: {e}")
    recommend = None

try:
    from model.content_based import train_content_model, recommend_similar_books
except Exception as e:
    print(f"Warning: content-based recommendation module unavailable: {e}")
    train_content_model = None
    recommend_similar_books = None

from database.db import get_books_by_dataset, save_recommendation_history

def hybrid_recommend(user_id, dataset_name, target_book_id=None):

    books = get_books_by_dataset(dataset_name)

    content_scores = {}
    if target_book_id and train_content_model and recommend_similar_books:
        similarity = train_content_model(books)
        content_results = recommend_similar_books(target_book_id, books, similarity)
        for r in content_results:
            content_scores[r["book_id"]] = r["score"]

    knn_results = recommend(user_id, dataset_name) if recommend else []

    final_scores = {}

    for r in knn_results:
        book_id = r["book_id"]
        knn_score = r["score"]
        content_score = content_scores.get(book_id, 0)

        final_scores[book_id] = knn_score + content_score

    sorted_books = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)

    output = []
    for book_id, score in sorted_books[:5]:
        book = books.get(book_id, {})

        output.append({
            "book_id": book_id,
            "title": book.get("title", ""),
            "author": book.get("author", ""),
            "score": score
        })

    save_recommendation_history(user_id, output, "Hybrid", dataset_name)
    return output
