# Online Bookshop Application (`BookVerse`)

A full-stack **Online Bookshop Application** built with **Python, Flask, Jinja2, Bootstrap 5, JavaScript (jQuery & AJAX), and SQLite**.

---

## Key Features

1. **User Authentication**:
   - Secure user registration, login, logout, password hashing (`Werkzeug`), and session management using Flask.
2. **User Profile Management**:
   - Dedicated dashboard (`/profile`) enabling users to view and edit their profile information, shipping address, contact details, and password.
3. **Cart Management**:
   - Robust shopping cart system allowing users to add, update quantities, and remove items with **real-time AJAX updates** (`/api/cart/add`, `/api/cart/update`, `/api/cart/remove`) to cart subtotals, tax, and navbar badge counts.
4. **Search Functionality**:
   - Real-time search bar implemented using **JavaScript, jQuery, and AJAX** (`/api/search`) with instant dropdown suggestions and catalog filtering by book title, author, category, and ISBN.
5. **Order Processing**:
   - Complete checkout workflow (`/checkout`) with dummy payment processing (Credit/Debit Card, UPI, NetBanking, Cash on Delivery), shipping validation, and order confirmation receipt.
6. **Order History**:
   - Full order history dashboard (`/orders` and `/order/<id>`) allowing users to view past orders, payment references, shipping details, and itemized invoices.

---

## Project Structure

```text
bookshop/
├── app.py                  # Flask application, SQLite models, REST/AJAX endpoints & routes
├── requirements.txt        # Python dependencies
├── static/
│   └── js/
│       └── bookshop.js     # jQuery + AJAX real-time search & cart management logic
├── templates/
│   ├── base.html           # Master layout with live AJAX search bar & navbar
│   ├── index.html          # Book catalog & category filter view
│   ├── book_detail.html    # Individual book details & related titles
│   ├── cart.html           # Interactive shopping cart with real-time updates
│   ├── checkout.html       # Shipping & dummy payment gateway checkout
│   ├── orders.html         # User order history list
│   ├── order_detail.html   # Individual order receipt & printable invoice
│   ├── profile.html        # User profile dashboard & settings
│   ├── login.html          # User login page
│   └── register.html       # User registration page
└── instance/
    └── bookshop.db         # Auto-initialized & pre-seeded SQLite database
```

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```
Open `http://127.0.0.1:5001` in your browser.
- **Demo Account**: Username `praveen` / Password `praveen123`

---

## Author
**Pidamarthi Praveen Kumar**
- B.Tech in Artificial Intelligence and Machine Learning — Chaitanya Bharathi Institute of Technology (CBIT)
- GitHub: [@praveen-79](https://github.com/praveen-79)
