from flask import Flask, flash, request, jsonify
from con import set_connection

app = Flask(__name__)


# CREATE TABLE books (
#     id SERIAL PRIMARY KEY,
#     title TEXT NOT NULL,
#     author TEXT NOT NULL,
#     published_date DATE NOT NULL,
#     is_available BOOLEAN NOT NULL
# );

# didnt used the journals and magazines tables just used the books table
# CREATE TABLE journals (
#     id SERIAL PRIMARY KEY,
#     title TEXT NOT NULL,
#     publisher TEXT NOT NULL,
#     published_date DATE NOT NULL,
#     is_available BOOLEAN NOT NULL
# );
#
# CREATE TABLE magazines (
#     id SERIAL PRIMARY KEY,
#     title TEXT NOT NULL,
#     publisher TEXT NOT NULL,
#     published_date DATE NOT NULL,
#     issue_number INTEGER NOT NULL,
#     is_available BOOLEAN NOT NULL
# );


# Endpoint to retrieve all books in the library
@app.route('/books', methods=['GET'])
def get_books():
    try:
        cur, conn = set_connection()
        # to retrieve all books from the database
        cur.execute('SELECT * FROM books')
        rows = cur.fetchall()

        # Convert the rows into a list of dictionaries
        books = []
        for row in rows:
            book = {
                'id': row[0],
                'title': row[1],
                'author': row[2],
                'published_date': row[3],
                'is_available': row[4]
            }
            books.append(book)

        return jsonify(books), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Endpoint to add a new book to the library
@app.route('/books/add', methods=['POST'])
def add_book():
    try:
        # get the book data from the request body
        # {
        #     "title": "temp title",
        #     "author": "temp author",
        #     "published_date": "2022-02-02"
        # }
        book_data = request.get_json()
        cur, conn = set_connection()
        # Insert the book into the database
        cur.execute(
            'INSERT INTO books (title, author, published_date, is_available) VALUES (%s, %s, %s, %s)',
            (book_data['title'], book_data['author'], book_data['published_date'], True)
        )
        conn.commit()

        return jsonify({'message': 'Book added successfully'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500


# Endpoint to borrow a book
@app.route('/books/borrow', methods=['PUT'])
def borrow_book():
    try:
        # Get the book ID from the request body
        book_data = request.get_json()
        cur, conn = set_connection()
        # Check if the book is available
        cur.execute('SELECT is_available FROM books WHERE id = %s', (book_data['id'],))
        row = cur.fetchone()
        if not row[0]:
            return jsonify({'message': 'Book is not available'}), 400

        # Update the book's availability
        cur.execute('UPDATE books SET is_available = false WHERE id = %s', (book_data['id'],))
        conn.commit()

        return jsonify({'message': 'Book borrowed successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500


# Endpoint to return a borrowed book
@app.route('/books/return', methods=['PUT'])
def return_book():
    try:
        # Get the book ID from the request body
        book_data = request.get_json()
        cur, conn = set_connection()
        # Check if the book is borrowed
        cur.execute('SELECT is_available FROM books WHERE id = %s', (book_data['id'],))
        row = cur.fetchone()
        if row[0]:
            return jsonify({'message': 'Book is not borrowed'}), 400

        # Update the book's availability
        cur.execute('UPDATE books SET is_available = true WHERE id = %s', (book_data['id'],))
        conn.commit()

        return jsonify({'message': 'Book returned Successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
