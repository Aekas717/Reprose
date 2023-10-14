import isbnlib

isbn = '9781108847063'

book = isbnlib.meta(isbn)

print()
print("Type: ", type(book))
print("Book data: ")
print(book)