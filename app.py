from flask import Flask, render_template, request, redirect, url_for
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
