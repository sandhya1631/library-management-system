from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Database connection
def get_db_connection():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
def init_db():
    conn = get_db_connection()
    with open('database_schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Books management
@app.route('/books')
def books():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    return render_template('books.html', books=books)

@app.route('/books/add')
def add_book_form():
    return render_template('add_book.html')

@app.route('/books/add', methods=['POST'])
def add_book():
    isbn = request.form['isbn']
    title = request.form['title']
    author = request.form['author']
    publisher = request.form['publisher']
    year = request.form['year']
    category = request.form['category']
    total_copies = request.form['total_copies']
    
    conn = get_db_connection()
    conn.execute('''INSERT INTO books (isbn, title, author, publisher, year, category, 
                    total_copies, available_copies) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                 (isbn, title, author, publisher, year, category, total_copies, total_copies))
    conn.commit()
    conn.close()
    
    flash('Book added successfully!', 'success')
    return redirect(url_for('books'))

@app.route('/books/edit/<int:book_id>')
def edit_book_form(book_id):
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE book_id = ?', (book_id,)).fetchone()
    conn.close()
    return render_template('edit_book.html', book=book)

@app.route('/books/edit/<int:book_id>', methods=['POST'])
def edit_book(book_id):
    isbn = request.form['isbn']
    title = request.form['title']
    author = request.form['author']
    publisher = request.form['publisher']
    year = request.form['year']
    category = request.form['category']
    total_copies = request.form['total_copies']
    
    conn = get_db_connection()
    conn.execute('''UPDATE books SET isbn=?, title=?, author=?, publisher=?, 
                    year=?, category=?, total_copies=? WHERE book_id=?''',
                 (isbn, title, author, publisher, year, category, total_copies, book_id))
    conn.commit()
    conn.close()
    
    flash('Book updated successfully!', 'success')
    return redirect(url_for('books'))

@app.route('/books/delete/<int:book_id>')
def delete_book(book_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM books WHERE book_id = ?', (book_id,))
    conn.commit()
    conn.close()
    
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('books'))

# Members management
@app.route('/members')
def members():
    conn = get_db_connection()
    members = conn.execute('SELECT * FROM members').fetchall()
    conn.close()
    return render_template('members.html', members=members)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
