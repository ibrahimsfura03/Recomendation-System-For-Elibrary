import json
import glob

def load_books():
    books = {}

    # load all book json files
    files = glob.glob("dataset/t*.json")

    for file in files:
        with open(file, "r") as f:
            try:
                data = json.load(f)

                # case: {"books": [...]}
                if isinstance(data, dict):
                    for key in data:
                        if isinstance(data[key], list):
                            for book in data[key]:
                                if "book_id" in book:
                                    books[book["book_id"]] = book

                # case: direct list
                elif isinstance(data, list):
                    for book in data:
                        if "book_id" in book:
                            books[book["book_id"]] = book

            except:
                pass

    return books
