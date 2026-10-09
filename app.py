"""
Online Bookshop Application — Flask, Jinja2, Bootstrap, JavaScript/jQuery/AJAX, SQLite
======================================================================================
Features implemented:
1. User Authentication: Secure registration, login, logout, password hashing, and Flask session management.
2. User Profile Management: Dashboard allowing users to view and edit their profile information, shipping address, and password.
3. Cart Management: Robust shopping cart supporting add, quantity update, and item removal with real-time AJAX updates.
4. Search Functionality: Real-time book search bar powered by JavaScript, jQuery, and AJAX (`/api/search`).
5. Order Processing: Complete checkout workflow with dummy payment processing (Credit/Debit Card, UPI, NetBanking) and order confirmation.
6. Order History: Full order history dashboard with itemized details and invoice view for every placed order.
"""

import os
import uuid
import sqlite3
from datetime import datetime
from functools import wraps
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
    g,
)
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
DATABASE_PATH = os.path.join(INSTANCE_DIR, "bookshop.db")

os.makedirs(INSTANCE_DIR, exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "online-bookshop-secret-key-2026")


# =====================================================================
# DATABASE CONNECTION & SEED DATA
# =====================================================================

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


SEED_BOOKS = [
    (
        "Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow",
        "Aurélien Géron",
        "AI & Machine Learning",
        "978-1098125974",
        649.00,
        4.9,
        42,
        "A practical guide to building intelligent systems using Python, Scikit-Learn, Keras, and TensorFlow with end-to-end ML pipelines.",
        "#0284c7",
    ),
    (
        "Deep Learning",
        "Ian Goodfellow, Yoshua Bengio, Aaron Courville",
        "AI & Machine Learning",
        "978-0262035613",
        799.00,
        4.8,
        30,
        "The definitive textbook on deep learning covering neural networks, CNNs, RNNs, optimization, and generative models.",
        "#7c3aed",
    ),
    (
        "Designing Data-Intensive Applications",
        "Martin Kleppmann",
        "Software Engineering",
        "978-1449373320",
        599.00,
        4.9,
        35,
        "The big ideas behind reliable, scalable, and maintainable distributed systems, databases, and stream processing.",
        "#059669",
    ),
    (
        "Clean Code: A Handbook of Agile Software Craftsmanship",
        "Robert C. Martin",
        "Software Engineering",
        "978-0132350884",
        499.00,
        4.7,
        50,
        "Best practices, design patterns, and principles for writing readable, maintainable, and testable object-oriented code.",
        "#d97706",
    ),
    (
        "Introduction to Algorithms (CLRS)",
        "Thomas H. Cormen, Charles E. Leiserson",
        "Data Structures & Algorithms",
        "978-0262046305",
        899.00,
        4.9,
        25,
        "Comprehensive guide to data structures, graph algorithms, dynamic programming, and computational complexity.",
        "#dc2626",
    ),
    (
        "Flask Web Development: Developing Web Applications with Python",
        "Miguel Grinberg",
        "Web Development",
        "978-1491991732",
        459.00,
        4.6,
        38,
        "Step-by-step guide to building full-stack Python web applications with Flask, Jinja2 templates, SQLite, and REST APIs.",
        "#2563eb",
    ),
    (
        "Artificial Intelligence: A Modern Approach",
        "Stuart Russell, Peter Norvig",
        "AI & Machine Learning",
        "978-0134610993",
        849.00,
        4.8,
        28,
        "Foundational exploration of search algorithms, knowledge representation, probabilistic reasoning, NLP, and robotics.",
        "#4f46e5",
    ),
    (
        "Fluent Python: Clear, Concise, and Effective Programming",
        "Luciano Ramalho",
        "Programming Languages",
        "978-1492056355",
        579.00,
        4.9,
        40,
        "Master Pythonic idioms, data structures, decorators, async concurrency, and metaprogramming.",
        "#0d9488",
    ),
    (
        "Eloquent JavaScript: A Modern Introduction to Programming",
        "Marijn Haverbeke",
        "Web Development",
        "978-1593279509",
        399.00,
        4.7,
        45,
        "Deep dive into JavaScript ES6+, DOM manipulation, asynchronous programming, AJAX, and browser application architecture.",
        "#ea580c",
    ),
    (
        "Grokking Algorithms",
        "Aditya Bhargava",
        "Data Structures & Algorithms",
        "978-1617292231",
        379.00,
        4.8,
        60,
        "An illustrated, friendly guide to applying common algorithms to practical programming problems.",
        "#db2777",
    ),
    (
        "Pattern Recognition and Machine Learning",
        "Christopher M. Bishop",
        "AI & Machine Learning",
        "978-0387310732",
        729.00,
        4.7,
        20,
        "Rigorous statistical treatment of Bayesian inference, kernel methods, graphical models, and ensemble learning.",
        "#9333ea",
    ),
    (
        "Database Internals: A Deep Dive into How Distributed Data Systems Work",
        "Alex Petrov",
        "Software Engineering",
        "978-1492040347",
        549.00,
        4.8,
        32,
        "Covers B-Trees, LSM-Trees, storage engines, transaction isolation, and distributed consensus protocols.",
        "#0891b2",
    ),
]


def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            phone TEXT DEFAULT '',
            address TEXT DEFAULT '',
            city TEXT DEFAULT 'Hyderabad',
            postal_code TEXT DEFAULT '500075',
            bio TEXT DEFAULT 'Avid reader & Computer Science enthusiast.',
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT NOT NULL,
            isbn TEXT UNIQUE NOT NULL,
            price REAL NOT NULL,
            rating REAL DEFAULT 4.8,
            stock INTEGER DEFAULT 25,
            description TEXT NOT NULL,
            cover_color TEXT DEFAULT '#2563eb'
        );

        CREATE TABLE IF NOT EXISTS cart_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            UNIQUE(user_id, book_id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (book_id) REFERENCES books (id)
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            payment_method TEXT NOT NULL,
            payment_reference TEXT NOT NULL,
            shipping_name TEXT NOT NULL,
            shipping_phone TEXT NOT NULL,
            shipping_address TEXT NOT NULL,
            shipping_city TEXT NOT NULL,
            shipping_postal_code TEXT NOT NULL,
            status TEXT DEFAULT 'Confirmed',
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            book_title TEXT NOT NULL,
            book_author TEXT NOT NULL,
            unit_price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (book_id) REFERENCES books (id)
        );
        """
    )

    # Seed Books if empty
    cur.execute("SELECT COUNT(*) as cnt FROM books")
    if cur.fetchone()["cnt"] == 0:
        cur.executemany(
            """
            INSERT INTO books (title, author, category, isbn, price, rating, stock, description, cover_color)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            SEED_BOOKS,
        )

    # Seed Demo User & Sample Order if empty
    cur.execute("SELECT COUNT(*) as cnt FROM users")
    if cur.fetchone()["cnt"] == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        cur.execute(
            """
            INSERT INTO users (username, full_name, email, password_hash, phone, address, city, postal_code, bio, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "praveen",
                "Pidamarthi Praveen Kumar",
                "praveenkumarpidamarthi01@gmail.com",
                generate_password_hash("praveen123"),
                "+91 8317668826",
                "Gandipet, CBIT Campus Road",
                "Hyderabad",
                "500075",
                "B.Tech AI & ML at CBIT | Building Full-Stack & Deep Learning Applications.",
                now,
            ),
        )
        user_id = cur.lastrowid

        # Seed a sample completed order for Order History demonstration
        cur.execute(
            """
            INSERT INTO orders (
                order_number, user_id, total_amount, payment_method, payment_reference,
                shipping_name, shipping_phone, shipping_address, shipping_city, shipping_postal_code,
                status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "ORD-2026-84920",
                user_id,
                1148.00,
                "Credit Card (Dummy Gateway)",
                "TXN-99481204",
                "Pidamarthi Praveen Kumar",
                "+91 8317668826",
                "Gandipet, CBIT Campus Road",
                "Hyderabad",
                "500075",
                "Delivered",
                now,
            ),
        )
        order_id = cur.lastrowid
        cur.execute(
            """
            INSERT INTO order_items (order_id, book_id, book_title, book_author, unit_price, quantity, subtotal)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                order_id,
                1,
                "Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow",
                "Aurélien Géron",
                649.00,
                1,
                649.00,
            ),
        )
        cur.execute(
            """
            INSERT INTO order_items (order_id, book_id, book_title, book_author, unit_price, quantity, subtotal)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                order_id,
                4,
                "Clean Code: A Handbook of Agile Software Craftsmanship",
                "Robert C. Martin",
                499.00,
                1,
                499.00,
            ),
        )

    conn.commit()
    conn.close()


# =====================================================================
# AUTHENTICATION & CART CONTEXT HELPERS
# =====================================================================

def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"success": False, "error": "Authentication required", "redirect": url_for("login")}), 401
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped


def get_cart_summary(user_id):
    if not user_id:
        return {"items": [], "total_quantity": 0, "subtotal": 0.0, "tax": 0.0, "grand_total": 0.0}

    db = get_db()
    rows = db.execute(
        """
        SELECT ci.id as cart_item_id, ci.quantity, b.*
        FROM cart_items ci
        JOIN books b ON ci.book_id = b.id
        WHERE ci.user_id = ?
        ORDER BY ci.id DESC
        """,
        (user_id,),
    ).fetchall()

    items = []
    total_qty = 0
    subtotal = 0.0
    for r in rows:
        item_total = round(r["price"] * r["quantity"], 2)
        total_qty += r["quantity"]
        subtotal += item_total
        items.append(
            {
                "cart_item_id": r["cart_item_id"],
                "book_id": r["id"],
                "title": r["title"],
                "author": r["author"],
                "category": r["category"],
                "isbn": r["isbn"],
                "price": r["price"],
                "quantity": r["quantity"],
                "item_total": item_total,
                "cover_color": r["cover_color"],
            }
        )

    subtotal = round(subtotal, 2)
    tax = round(subtotal * 0.05, 2)
    grand_total = round(subtotal + tax, 2)
    return {
        "items": items,
        "total_quantity": total_qty,
        "subtotal": subtotal,
        "tax": tax,
        "grand_total": grand_total,
    }


@app.context_processor
def inject_globals():
    user = None
    cart_count = 0
    if "user_id" in session:
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
        row = db.execute(
            "SELECT COALESCE(SUM(quantity), 0) AS total_qty FROM cart_items WHERE user_id = ?",
            (session["user_id"],),
        ).fetchone()
        cart_count = row["total_qty"] if row else 0
    return {"current_user": user, "cart_count": cart_count}


# =====================================================================
# STOREFRONT & AJAX SEARCH ROUTES
# =====================================================================

@app.route("/")
def index():
    db = get_db()
    category = request.args.get("category", "").strip()
    q = request.args.get("q", "").strip()

    query = "SELECT * FROM books WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)
    if q:
        query += " AND (LOWER(title) LIKE ? OR LOWER(author) LIKE ? OR LOWER(category) LIKE ? OR isbn LIKE ?)"
        like_q = f"%{q.lower()}%"
        params.extend([like_q, like_q, like_q, like_q])

    query += " ORDER BY rating DESC, id ASC"
    books = db.execute(query, params).fetchall()

    categories = [
        r["category"]
        for r in db.execute("SELECT DISTINCT category FROM books ORDER BY category ASC").fetchall()
    ]
    return render_template("index.html", books=books, categories=categories, selected_category=category, search_query=q)


@app.route("/book/<int:book_id>")
def book_detail(book_id):
    db = get_db()
    book = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if not book:
        flash("Book not found.", "warning")
        return redirect(url_for("index"))

    related = db.execute(
        "SELECT * FROM books WHERE category = ? AND id != ? LIMIT 4",
        (book["category"], book_id),
    ).fetchall()
    return render_template("book_detail.html", book=book, related_books=related)


@app.route("/api/search")
def api_search():
    """
    AJAX endpoint queried by JavaScript / jQuery search bar for real-time book title/author lookup.
    """
    q = request.args.get("q", "").strip().lower()
    category = request.args.get("category", "").strip()

    db = get_db()
    sql = "SELECT * FROM books WHERE 1=1"
    params = []

    if category:
        sql += " AND category = ?"
        params.append(category)

    if q:
        sql += " AND (LOWER(title) LIKE ? OR LOWER(author) LIKE ? OR LOWER(category) LIKE ? OR isbn LIKE ?)"
        like_q = f"%{q}%"
        params.extend([like_q, like_q, like_q, like_q])

    sql += " ORDER BY rating DESC, title ASC LIMIT 24"
    rows = db.execute(sql, params).fetchall()

    results = [
        {
            "id": r["id"],
            "title": r["title"],
            "author": r["author"],
            "category": r["category"],
            "isbn": r["isbn"],
            "price": r["price"],
            "rating": r["rating"],
            "stock": r["stock"],
            "description": r["description"],
            "cover_color": r["cover_color"],
            "detail_url": url_for("book_detail", book_id=r["id"]),
        }
        for r in rows
    ]
    return jsonify({"count": len(results), "books": results})


# =====================================================================
# USER AUTHENTICATION & PROFILE MANAGEMENT ROUTES
# =====================================================================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        city = request.form.get("city", "Hyderabad").strip()
        postal_code = request.form.get("postal_code", "").strip()

        if not username or not full_name or not email or not password:
            flash("Please complete all required fields.", "danger")
            return redirect(url_for("register"))

        db = get_db()
        existing = db.execute(
            "SELECT id FROM users WHERE LOWER(username) = ? OR LOWER(email) = ?",
            (username, email),
        ).fetchone()
        if existing:
            flash("An account with that username or email already exists.", "danger")
            return redirect(url_for("register"))

        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        cur = db.execute(
            """
            INSERT INTO users (username, full_name, email, password_hash, phone, address, city, postal_code, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                full_name,
                email,
                generate_password_hash(password),
                phone,
                address,
                city,
                postal_code,
                now,
            ),
        )
        db.commit()
        session["user_id"] = cur.lastrowid
        flash(f"Welcome to BookVerse, {full_name}! Your account has been created.", "success")
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip().lower()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE LOWER(username) = ? OR LOWER(email) = ?",
            (identifier, identifier),
        ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            flash(f"Welcome back, {user['full_name']}!", "success")
            return redirect(url_for("index"))

        flash("Invalid username/email or password.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been safely logged out.", "info")
    return redirect(url_for("login"))


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    db = get_db()
    user_id = session["user_id"]

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        city = request.form.get("city", "").strip()
        postal_code = request.form.get("postal_code", "").strip()
        bio = request.form.get("bio", "").strip()
        new_password = request.form.get("new_password", "").strip()

        if not full_name or not email:
            flash("Full Name and Email cannot be empty.", "danger")
            return redirect(url_for("profile"))

        db.execute(
            """
            UPDATE users
            SET full_name = ?, email = ?, phone = ?, address = ?, city = ?, postal_code = ?, bio = ?
            WHERE id = ?
            """,
            (full_name, email, phone, address, city, postal_code, bio, user_id),
        )
        if new_password:
            db.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (generate_password_hash(new_password), user_id),
            )
        db.commit()
        flash("Your profile information has been updated.", "success")
        return redirect(url_for("profile"))

    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    order_stats = db.execute(
        "SELECT COUNT(*) as order_count, COALESCE(SUM(total_amount), 0) as total_spent FROM orders WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    return render_template("profile.html", user=user, order_stats=order_stats)


# =====================================================================
# CART MANAGEMENT ROUTES (REAL-TIME AJAX + STANDARD VIEWS)
# =====================================================================

@app.route("/cart")
@login_required
def cart_view():
    summary = get_cart_summary(session["user_id"])
    return render_template("cart.html", cart=summary)


@app.route("/api/cart/add", methods=["POST"])
@login_required
def api_cart_add():
    data = request.get_json(silent=True) or request.form
    book_id = int(data.get("book_id", 0))
    quantity = max(1, int(data.get("quantity", 1)))

    db = get_db()
    book = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if not book:
        return jsonify({"success": False, "error": "Book not found"}), 404

    existing = db.execute(
        "SELECT id, quantity FROM cart_items WHERE user_id = ? AND book_id = ?",
        (session["user_id"], book_id),
    ).fetchone()

    if existing:
        new_qty = existing["quantity"] + quantity
        db.execute(
            "UPDATE cart_items SET quantity = ? WHERE id = ?",
            (new_qty, existing["id"]),
        )
    else:
        db.execute(
            "INSERT INTO cart_items (user_id, book_id, quantity) VALUES (?, ?, ?)",
            (session["user_id"], book_id, quantity),
        )
    db.commit()

    summary = get_cart_summary(session["user_id"])
    return jsonify(
        {
            "success": True,
            "message": f"Added '{book['title']}' to your cart!",
            "cart": summary,
        }
    )


@app.route("/api/cart/update", methods=["POST"])
@login_required
def api_cart_update():
    data = request.get_json(silent=True) or request.form
    book_id = int(data.get("book_id", 0))
    quantity = int(data.get("quantity", 1))

    db = get_db()
    if quantity <= 0:
        db.execute(
            "DELETE FROM cart_items WHERE user_id = ? AND book_id = ?",
            (session["user_id"], book_id),
        )
    else:
        db.execute(
            "UPDATE cart_items SET quantity = ? WHERE user_id = ? AND book_id = ?",
            (quantity, session["user_id"], book_id),
        )
    db.commit()

    summary = get_cart_summary(session["user_id"])
    return jsonify({"success": True, "cart": summary})


@app.route("/api/cart/remove", methods=["POST"])
@login_required
def api_cart_remove():
    data = request.get_json(silent=True) or request.form
    book_id = int(data.get("book_id", 0))

    db = get_db()
    db.execute(
        "DELETE FROM cart_items WHERE user_id = ? AND book_id = ?",
        (session["user_id"], book_id),
    )
    db.commit()

    summary = get_cart_summary(session["user_id"])
    return jsonify({"success": True, "cart": summary})


# =====================================================================
# CHECKOUT, DUMMY PAYMENT PROCESSING & ORDER HISTORY ROUTES
# =====================================================================

@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    user_id = session["user_id"]
    summary = get_cart_summary(user_id)

    if not summary["items"]:
        flash("Your cart is empty. Add some books before checking out!", "warning")
        return redirect(url_for("index"))

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    if request.method == "POST":
        shipping_name = request.form.get("shipping_name", "").strip() or user["full_name"]
        shipping_phone = request.form.get("shipping_phone", "").strip() or user["phone"]
        shipping_address = request.form.get("shipping_address", "").strip() or user["address"]
        shipping_city = request.form.get("shipping_city", "").strip() or user["city"]
        shipping_postal = request.form.get("shipping_postal_code", "").strip() or user["postal_code"]
        payment_method = request.form.get("payment_method", "Credit / Debit Card")

        if not shipping_address or not shipping_city or not shipping_postal:
            flash("Please provide a complete shipping address.", "danger")
            return redirect(url_for("checkout"))

        # Generate dummy payment transaction reference & unique order number
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:5].upper()}"
        payment_ref = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        cur = db.execute(
            """
            INSERT INTO orders (
                order_number, user_id, total_amount, payment_method, payment_reference,
                shipping_name, shipping_phone, shipping_address, shipping_city, shipping_postal_code,
                status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                order_number,
                user_id,
                summary["grand_total"],
                payment_method,
                payment_ref,
                shipping_name,
                shipping_phone,
                shipping_address,
                shipping_city,
                shipping_postal,
                "Confirmed & Paid",
                now,
            ),
        )
        order_id = cur.lastrowid

        for item in summary["items"]:
            db.execute(
                """
                INSERT INTO order_items (order_id, book_id, book_title, book_author, unit_price, quantity, subtotal)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    order_id,
                    item["book_id"],
                    item["title"],
                    item["author"],
                    item["price"],
                    item["quantity"],
                    item["item_total"],
                ),
            )
            db.execute(
                "UPDATE books SET stock = MAX(0, stock - ?) WHERE id = ?",
                (item["quantity"], item["book_id"]),
            )

        # Clear user's cart after order placement
        db.execute("DELETE FROM cart_items WHERE user_id = ?", (user_id,))
        db.commit()

        flash(f"Order {order_number} placed successfully! Payment Reference: {payment_ref}", "success")
        return redirect(url_for("order_detail", order_id=order_id))

    return render_template("checkout.html", cart=summary, user=user)


@app.route("/orders")
@login_required
def order_history():
    db = get_db()
    orders = db.execute(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC",
        (session["user_id"],),
    ).fetchall()

    items_by_order = {}
    for o in orders:
        items_by_order[o["id"]] = db.execute(
            "SELECT * FROM order_items WHERE order_id = ?", (o["id"],)
        ).fetchall()

    return render_template("orders.html", orders=orders, items_by_order=items_by_order)


@app.route("/order/<int:order_id>")
@login_required
def order_detail(order_id):
    db = get_db()
    order = db.execute(
        "SELECT * FROM orders WHERE id = ? AND user_id = ?",
        (order_id, session["user_id"]),
    ).fetchone()
    if not order:
        flash("Order not found.", "warning")
        return redirect(url_for("order_history"))

    items = db.execute(
        "SELECT * FROM order_items WHERE order_id = ?", (order_id,)
    ).fetchall()
    return render_template("order_detail.html", order=order, items=items)


init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
