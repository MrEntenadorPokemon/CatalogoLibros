# CatalogoLibros - Gemini Context

This project is a Flask-based web application for managing a book catalog, including user registration, book searches, loans, and reviews.

## Project Overview

- **Purpose:** A library management system ("Catalogo de Libros") for a final project (Admin II).
- **Core Technologies:**
  - **Backend:** Python 3, Flask, Flask-WTF (Forms), SQLite3.
  - **Frontend:** HTML5, Jinja2, Bootstrap 5.3.3 (CDN), Custom CSS.
- **Architecture:**
  - `app.py`: Main entry point containing all Flask routes and application logic.
  - `data.py`: Data Access Layer (DAO) using `sqlite3` and `Flask-WTF` form definitions.
  - `schema.sql`: SQL script for initializing the SQLite database (`identifier.sqlite`).
  - `templates/`: Jinja2 HTML templates, organized by module (auth, books, loans, admin, errors).
  - `static/`: Static assets (styles.css).

## Features

- **User Authentication:** Registration and login with hashed passwords (`werkzeug.security`).
- **Book Catalog:** Browsing, searching, and filtering by genre.
- **Book Details:** Detailed view with average ratings and user reviews.
- **Loan System:** Borrowing and returning books with status tracking.
- **Reviews & Ratings:** Users can leave a 1-5 star rating and a comment on books they have borrowed.
- **Admin Dashboard:** Statistics for total books, users, active loans, and top-rated books.

## Building and Running

### Prerequisites
- Python 3.x
- Virtual environment (recommended)

### Setup
1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Database Initialization:**
    The project uses `identifier.sqlite`. If the database needs to be re-initialized, run the `schema.sql` script against the SQLite database file.
3.  **Environment Variables:**
    - `SECRET_KEY`: (Optional) Set this for session security. Defaults to a placeholder in `app.py`.

### Running the Application
```bash
python app.py
```
The app will be available at `http://127.0.0.1:5000/` by default.

## Development Conventions

- **Database Access:** Direct use of `sqlite3` with a simple wrapper in `data.py`. Transactions are used for complex operations like creating a loan.
- **Forms:** All user input is handled and validated via `Flask-WTF` classes defined in `data.py`.
- **Security:**
  - Password hashing is mandatory for user registration/login.
  - Role-based access control (RBAC) is implemented via session checks (roles: `user`, `admin`).
- **Error Handling:** Custom 404 and 403 error pages are defined.
- **Naming:** Backend code uses mostly English for logic, while user-facing labels in `data.py` and templates are in Spanish.

## Project Structure

- `app.py`: Flask routes and core logic.
- `data.py`: Database queries and WTForms definitions.
- `schema.sql`: Database schema definition.
- `identifier.sqlite`: SQLite database file.
- `templates/`:
  - `base.html`: Main layout with Navbar and Flash messages.
  - `auth/`: Login and registration.
  - `books/`: Catalog and book details.
  - `loans/`: Loan history.
  - `admin/`: Dashboard.
  - `errors/`: 404 and 403 pages.
- `static/`:
  - `styles.css`: Custom project styling.
