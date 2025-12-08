from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Database connection
def get_db_connection():
    conn = sqlite3.connect('library.db', timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    return conn

# Initialize database
def init_db():
    conn = get_db_connection()
    with open('database_schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')


# Signup page 
@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    full_name = request.form['full_name']
    
    # Validation
    if password != confirm_password:
        flash('Passwords do not match!', 'danger')
        return redirect(url_for('signup'))
    
    if len(password) < 6:
        flash('Password must be at least 6 characters long!', 'danger')
        return redirect(url_for('signup'))
    
    # Hash the password
    hashed_password = generate_password_hash(password)
    
    conn = get_db_connection()
    try:
        conn.execute('''INSERT INTO users (username, email, password, full_name) 
                        VALUES (?, ?, ?, ?)''',
                     (username, email, hashed_password, full_name))
        conn.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    except sqlite3.IntegrityError:
        flash('Username or email already exists!', 'danger')
        return redirect(url_for('signup'))
    finally:
        conn.close()

# Login page
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        # Login successful
        session['user_id'] = user['user_id']
        session['username'] = user['username']
        session['full_name'] = user['full_name']
        flash(f'Welcome back, {user["full_name"]}!', 'success')
        return redirect(url_for('index'))
    else:
        flash('Invalid username or password!', 'danger')
        return redirect(url_for('login'))

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


# Books management
@app.route('/books')
@login_required
def books():
    search_query = request.args.get('search', '')
    
    conn = get_db_connection()
    if search_query:
        # Search in title, author, ISBN, or category
        books = conn.execute('''SELECT * FROM books 
                               WHERE title LIKE ? 
                               OR author LIKE ? 
                               OR isbn LIKE ? 
                               OR category LIKE ?
                               ORDER BY title''',
                            (f'%{search_query}%', f'%{search_query}%', 
                             f'%{search_query}%', f'%{search_query}%')).fetchall()
    else:
        books = conn.execute('SELECT * FROM books ORDER BY title').fetchall()
    conn.close()
    return render_template('books.html', books=books, search_query=search_query)

@app.route('/books/add')
@login_required
def add_book_form():
    return render_template('add_book.html')

@app.route('/books/add', methods=['POST'])
@login_required
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
@login_required
def edit_book_form(book_id):
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE book_id = ?', (book_id,)).fetchone()
    conn.close()
    return render_template('edit_book.html', book=book)

@app.route('/books/edit/<int:book_id>', methods=['POST'])
@login_required
def edit_book(book_id):
    isbn = request.form['isbn']
    title = request.form['title']
    author = request.form['author']
    publisher = request.form['publisher']
    year = request.form['year']
    category = request.form['category']
    new_total_copies = int(request.form['total_copies'])
    
    conn = get_db_connection()

    book = conn.execute('SELECT * FROM books WHERE book_id = ?', (book_id,)).fetchone()
    old_total_copies = book['total_copies']
    old_available_copies = book['available_copies']
    
    difference = new_total_copies - old_total_copies
    new_available_copies = old_available_copies + difference
    
    if new_available_copies < 0:
        new_available_copies = 0
    
    # Update book
    conn.execute('''UPDATE books SET isbn=?, title=?, author=?, publisher=?, 
                    year=?, category=?, total_copies=?, available_copies=? 
                    WHERE book_id=?''',
                 (isbn, title, author, publisher, year, category, 
                  new_total_copies, new_available_copies, book_id))
    conn.commit()
    conn.close()
    
    flash('Book updated successfully!', 'success')
    return redirect(url_for('books'))

@app.route('/books/delete/<int:book_id>')
@login_required
def delete_book(book_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM books WHERE book_id = ?', (book_id,))
    conn.commit()
    conn.close()
    
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('books'))


# Members management
@app.route('/members')
@login_required
def members():
    search_query = request.args.get('search', '')
    
    conn = get_db_connection()
    if search_query:
        # Search in name, email, or phone
        members = conn.execute('''SELECT * FROM members 
                                 WHERE name LIKE ? 
                                 OR email LIKE ? 
                                 OR phone LIKE ?
                                 ORDER BY name''',
                              (f'%{search_query}%', f'%{search_query}%', 
                               f'%{search_query}%')).fetchall()
    else:
        members = conn.execute('SELECT * FROM members ORDER BY name').fetchall()
    conn.close()
    return render_template('members.html', members=members, search_query=search_query)

# Add new member
@app.route('/members/add')
@login_required
def add_member_form():
    return render_template('add_member.html')

@app.route('/members/add', methods=['POST'])
@login_required
def add_member():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']
    
    conn = get_db_connection()
    conn.execute('''INSERT INTO members (name, email, phone, address, status) 
                    VALUES (?, ?, ?, ?, ?)''',
                 (name, email, phone, address, 'active'))
    conn.commit()
    conn.close()
    
    flash('Member added successfully!', 'success')
    return redirect(url_for('members'))

# Edit member 
@app.route('/members/edit/<int:member_id>')
@login_required
def edit_member_form(member_id):
    conn = get_db_connection()
    member = conn.execute('SELECT * FROM members WHERE member_id = ?', (member_id,)).fetchone()
    conn.close()
    return render_template('edit_member.html', member=member)

@app.route('/members/edit/<int:member_id>', methods=['POST'])
@login_required
def edit_member(member_id):
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']
    status = request.form['status']
    
    conn = get_db_connection()
    conn.execute('''UPDATE members SET name=?, email=?, phone=?, address=?, status=? 
                    WHERE member_id=?''',
                 (name, email, phone, address, status, member_id))
    conn.commit()
    conn.close()
    
    flash('Member updated successfully!', 'success')
    return redirect(url_for('members'))

# Delete member
@app.route('/members/delete/<int:member_id>')
@login_required
def delete_member(member_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM members WHERE member_id = ?', (member_id,))
    conn.commit()
    conn.close()
    
    flash('Member deleted successfully!', 'success')
    return redirect(url_for('members'))

# View member details and borrowing history
@app.route('/members/view/<int:member_id>')
@login_required
def view_member(member_id):
    conn = get_db_connection()
    member = conn.execute('SELECT * FROM members WHERE member_id = ?', (member_id,)).fetchone()
    
    # Borrowing history
    transactions = conn.execute('''
        SELECT t.*, b.title, b.author 
        FROM transactions t
        JOIN books b ON t.book_id = b.book_id
        WHERE t.member_id = ?
        ORDER BY t.issue_date DESC
    ''', (member_id,)).fetchall()
    
    conn.close()
    return render_template('member_detail.html', member=member, transactions=transactions)


# View all transactions
@app.route('/transactions')
@login_required
def transactions():
    conn = get_db_connection()
    transactions = conn.execute('''
        SELECT t.*, b.title, b.author, m.name as member_name
        FROM transactions t
        JOIN books b ON t.book_id = b.book_id
        JOIN members m ON t.member_id = m.member_id
        ORDER BY t.issue_date DESC
    ''').fetchall()
    conn.close()
    return render_template('transactions.html', transactions=transactions)

# Issue book 
@app.route('/transactions/issue')
@login_required
def issue_book_form():
    conn = get_db_connection()
    # Get only available books
    books = conn.execute('SELECT * FROM books WHERE available_copies > 0 ORDER BY title').fetchall()
    # Get only active members
    members = conn.execute('SELECT * FROM members WHERE status = "active" ORDER BY name').fetchall()
    conn.close()
    return render_template('issue_book.html', books=books, members=members)

@app.route('/transactions/issue', methods=['POST'])
@login_required
def issue_book():
    book_id = request.form['book_id']
    member_id = request.form['member_id']
    
    # Calculate dates
    issue_date = datetime.now().date()
    due_date = issue_date + timedelta(days=14)  # 14-day loan period
    
    conn = get_db_connection()
    
    # Check if book is available
    book = conn.execute('SELECT available_copies FROM books WHERE book_id = ?', (book_id,)).fetchone()
    
    if book and book['available_copies'] > 0:
        # Create transaction
        conn.execute('''INSERT INTO transactions (book_id, member_id, issue_date, due_date, status)
                        VALUES (?, ?, ?, ?, ?)''',
                     (book_id, member_id, issue_date, due_date, 'issued'))
        
        # Update book availability
        conn.execute('UPDATE books SET available_copies = available_copies - 1 WHERE book_id = ?', (book_id,))
        
        conn.commit()
        flash('Book issued successfully!', 'success')
    else:
        flash('Book is not available!', 'danger')
    
    conn.close()
    return redirect(url_for('transactions'))

# Return book
@app.route('/transactions/return/<int:transaction_id>')
@login_required
def return_book(transaction_id):
    return_date = datetime.now().date()
    
    conn = get_db_connection()
    
    # Get transaction details
    transaction = conn.execute('SELECT * FROM transactions WHERE transaction_id = ?', 
                              (transaction_id,)).fetchone()
    
    if transaction:
        # Update transaction
        conn.execute('''UPDATE transactions 
                        SET return_date = ?, status = ? 
                        WHERE transaction_id = ?''',
                     (return_date, 'returned', transaction_id))
        
        # Update book availability
        conn.execute('UPDATE books SET available_copies = available_copies + 1 WHERE book_id = ?',
                    (transaction['book_id'],))
        
        conn.commit()
        flash('Book returned successfully!', 'success')
    else:
        flash('Transaction not found!', 'danger')
    
    conn.close()
    return redirect(url_for('transactions'))


# View all reservations
@app.route('/reservations')
@login_required
def reservations():
    conn = get_db_connection()
    reservations = conn.execute('''
        SELECT r.*, b.title, b.author, m.name as member_name, b.available_copies
        FROM reservations r
        JOIN books b ON r.book_id = b.book_id
        JOIN members m ON r.member_id = m.member_id
        ORDER BY r.reservation_date DESC
    ''').fetchall()
    conn.close()
    return render_template('reservations.html', reservations=reservations)

# Reserve a book
@app.route('/books/reserve/<int:book_id>')
@login_required
def reserve_book(book_id):
    conn = get_db_connection()
    
    # Check if book exists
    book = conn.execute('SELECT * FROM books WHERE book_id = ?', (book_id,)).fetchone()
    
    if not book:
        flash('Book not found!', 'danger')
        conn.close()
        return redirect(url_for('books'))
    
    # Check if book is available
    if book['available_copies'] > 0:
        flash('This book is available! You can issue it directly.', 'info')
        conn.close()
        return redirect(url_for('books'))
    
    # Get all members to choose from
    members = conn.execute('SELECT * FROM members WHERE status = "active" ORDER BY name').fetchall()
    conn.close()
    
    return render_template('reserve_book.html', book=book, members=members)

# Handle reservation submission
@app.route('/books/reserve/<int:book_id>', methods=['POST'])
@login_required
def reserve_book_post(book_id):
    member_id = request.form['member_id']
    reservation_date = datetime.now().date()
    
    conn = get_db_connection()
    
    # Check if member already has a reservation for this book
    existing = conn.execute('''SELECT * FROM reservations 
                              WHERE book_id = ? AND member_id = ? AND status = "pending"''',
                           (book_id, member_id)).fetchone()
    
    if existing:
        flash('You already have a pending reservation for this book!', 'warning')
    else:
        # Create reservation
        conn.execute('''INSERT INTO reservations (book_id, member_id, reservation_date, status)
                        VALUES (?, ?, ?, ?)''',
                     (book_id, member_id, reservation_date, 'pending'))
        conn.commit()
        flash('Book reserved successfully! You will be notified when it becomes available.', 'success')
    
    conn.close()
    return redirect(url_for('reservations'))

# Cancel reservation
@app.route('/reservations/cancel/<int:reservation_id>')
@login_required
def cancel_reservation(reservation_id):
    conn = get_db_connection()
    conn.execute('UPDATE reservations SET status = ? WHERE reservation_id = ?',
                ('cancelled', reservation_id))
    conn.commit()
    conn.close()
    
    flash('Reservation cancelled successfully!', 'info')
    return redirect(url_for('reservations'))

# Fulfill reservation
@app.route('/reservations/fulfill/<int:reservation_id>')
@login_required
def fulfill_reservation(reservation_id):
    conn = get_db_connection()
    conn.execute('UPDATE reservations SET status = ? WHERE reservation_id = ?',
                ('fulfilled', reservation_id))
    conn.commit()
    conn.close()
    
    flash('Reservation fulfilled!', 'success')
    return redirect(url_for('reservations'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)