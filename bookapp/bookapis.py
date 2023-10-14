# Get the ISBN for the book

import requests
import os
key = os.environ.get('Google_Cloud_API_Key')

key = 'AIzaSyDxM0hcZbiTkjMmR6-japeENTi5418T6Wk'


def get_isbn_from_title(title, api_key):
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": f"intitle:{title}",
        "key": api_key,
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if "items" in data:
            book = data["items"][0]
            volume_info = book.get("volumeInfo", {})
            isbn = volume_info.get("industryIdentifiers", [])
            for identifier in isbn:
                if identifier["type"] == "ISBN_13":
                    return identifier["identifier"]

        return "ISBN not found"
    except Exception as e:
        return f"An error occurred: {str(e)}"


def get_book_info_from_isbn(isbn):
    api_key = 'AIzaSyDxM0hcZbiTkjMmR6-japeENTi5418T6Wk'
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": f"isbn:{isbn}",
        "key": api_key,
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if "items" in data:
            book = data["items"][0]
            volume_info = book.get("volumeInfo", {})
            title = volume_info.get("title", "Title not found")
            description = volume_info.get(
                "description", "Description not found")
            categories = volume_info.get("categories", "Categories not found")
            averageRating = volume_info.get(
                "averageRating", "Rating not found")
            maturityRating = volume_info.get(
                "maturityRating", "Maturity rating not found")
            image_url = "https://covers.openlibrary.org/b/isbn/" + isbn + "-L.jpg"

            return title, description, categories, averageRating, maturityRating, image_url

        return "Book not found"
    except Exception as e:
        return f"An error occurred: {str(e)}"


# print(get_book_info_from_isbn(9781593156329, key))

if __name__ == "__main__":
    api_key = key
    book_isbn = input("Enter the book isbn: ")
    book_info = get_book_info_from_isbn(book_isbn)
    print(book_info)
