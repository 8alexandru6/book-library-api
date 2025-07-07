from flask import Flask, jsonify, request
import requests
import os  

app = Flask(__name__)

GOOGLE_BOOKS_API_KEY = "AIzaSyBSFAic7qUOqbYGRo31bYJi7nloV11cTVo"
GOOGLE_BOOKS_API_BASE_URL = "https://www.googleapis.com/books/v1/volumes"

def fetch_book_data(query):
    """
    Fetches book data from the Google Books API.

    Args:
        query (str): The search query.

    Returns:
        dict: A dictionary containing book details if found, or an error message.
    """
    params = {
        "q": query,
        "key": GOOGLE_BOOKS_API_KEY,
        "maxResults": 10  
    }
    try:
        response = requests.get(GOOGLE_BOOKS_API_BASE_URL, params=params)
        response.raise_for_status() 
        data = response.json()

        books = []
        if "items" in data:
            for item in data["items"]:
                book = {}
                if "volumeInfo" in item:
                    volume_info = item["volumeInfo"]
                    book["title"] = volume_info.get("title", "N/A")
                    book["authors"] = volume_info.get("authors", ["N/A"])
                    book["description"] = volume_info.get("description", "N/A")
                    book["imageLink"] = volume_info.get("imageLinks", {}).get("thumbnail", None)  # Handle missing image links
                    book["isbn"] =  next((identifier['identifier'] for identifier in volume_info.get('industryIdentifiers', []) if identifier['type'] == 'ISBN_13'), None) or next((identifier['identifier'] for identifier in volume_info.get('industryIdentifiers', []) if identifier['type'] == 'ISBN_10'), None)

                books.append(book)
        return books  
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}") 
        return {"error": "Failed to connect to Google Books API"}
    except (KeyError, TypeError) as e:
        print(f"Data parsing error: {e}") 
        return {"error": "Error parsing data from Google Books API"}


@app.route('/books', methods=['GET'])
def search_books():
    """
    Searches for books based on a query.
    """
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Missing query parameter"}), 

    book_data = fetch_book_data(query)

    if isinstance(book_data, list): 
       return jsonify(book_data) 
    else:
        return jsonify(book_data), 

if __name__ == '__main__':
    if not GOOGLE_BOOKS_API_KEY:
        print("Error: GOOGLE_BOOKS_API_KEY environment variable not set.")
    else:
        app.run(debug=True) 