import os
import sqlite3
from contextlib import closing

from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, TextAreaField, IntegerField,
    SelectField, BooleanField, HiddenField, SubmitField
)
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, Optional,
    NumberRange, URL
)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "identifier.sqlite")


# =========================================================
# FORMULARIOS
# =========================================================

# =========================
# USUARIOS
# =========================
class RegisterForm(FlaskForm):
    name = StringField(
        "Nombre",
        validators=[DataRequired(), Length(min=2, max=100)]
    )
    email = StringField(
        "Correo electrónico",
        validators=[DataRequired(), Email(), Length(max=120)]
    )
    password = PasswordField(
        "Contraseña",
        validators=[DataRequired(), Length(min=6, max=100)]
    )
    confirm_password = PasswordField(
        "Confirmar contraseña",
        validators=[DataRequired(), EqualTo("password", message="Las contraseñas no coinciden")]
    )
    submit = SubmitField("Registrarse")


class LoginForm(FlaskForm):
    email = StringField(
        "Correo electrónico",
        validators=[DataRequired(), Email(), Length(max=120)]
    )
    password = PasswordField(
        "Contraseña",
        validators=[DataRequired()]
    )
    submit = SubmitField("Iniciar sesión")


class UserForm(FlaskForm):
    name = StringField(
        "Nombre",
        validators=[DataRequired(), Length(min=2, max=100)]
    )
    email = StringField(
        "Correo electrónico",
        validators=[DataRequired(), Email(), Length(max=120)]
    )
    password = PasswordField(
        "Contraseña",
        validators=[Optional(), Length(min=6, max=100)]
    )
    role = SelectField(
        "Rol",
        choices=[("user", "Usuario"), ("admin", "Administrador")],
        validators=[DataRequired()]
    )
    submit = SubmitField("Guardar usuario")


# =========================
# LIBROS
# =========================
class BookForm(FlaskForm):
    title = StringField(
        "Título",
        validators=[DataRequired(), Length(min=1, max=200)]
    )
    author = StringField(
        "Autor",
        validators=[DataRequired(), Length(min=2, max=150)]
    )
    genre = StringField(
        "Género",
        validators=[DataRequired(), Length(min=2, max=100)]
    )
    publisher = StringField(
        "Editorial",
        validators=[Optional(), Length(max=150)]
    )
    year = IntegerField(
        "Año",
        validators=[Optional(), NumberRange(min=1000, max=2100)]
    )
    synopsis = TextAreaField(
        "Sinopsis",
        validators=[DataRequired(), Length(min=10, max=5000)]
    )
    cover_url = StringField(
        "URL de portada",
        validators=[Optional(), URL(message="Ingresa una URL válida"), Length(max=500)]
    )
    is_available = BooleanField("Disponible")
    submit = SubmitField("Guardar libro")


class SearchBookForm(FlaskForm):
    query = StringField(
        "Buscar",
        validators=[Optional(), Length(max=200)]
    )
    filter_genre = StringField(
        "Género",
        validators=[Optional(), Length(max=100)]
    )
    submit = SubmitField("Buscar")


# =========================
# PRESTAMOS
# =========================
class LoanForm(FlaskForm):
    user_id = HiddenField(validators=[DataRequired()])
    book_id = HiddenField(validators=[DataRequired()])
    submit = SubmitField("Solicitar préstamo")


class ReturnLoanForm(FlaskForm):
    loan_id = HiddenField(validators=[DataRequired()])
    submit = SubmitField("Registrar devolución")


# =========================
# RESEÑAS + CALIFICACIONES
# =========================
class ReviewForm(FlaskForm):
    user_id = HiddenField(validators=[DataRequired()])
    book_id = HiddenField(validators=[DataRequired()])
    rating = SelectField(
        "Calificación",
        choices=[
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4", "4"),
            ("5", "5")
        ],
        validators=[DataRequired()]
    )
    comment = TextAreaField(
        "Reseña",
        validators=[Optional(), Length(max=2000)]
    )
    submit = SubmitField("Guardar reseña")


# =========================
# CONFIRMACION DE ELIMINACION
# =========================
class DeleteForm(FlaskForm):
    submit = SubmitField("Eliminar")


# =========================================================
# CONEXIÓN A SQLITE
# =========================================================
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def execute_query(query, params=(), commit=False):
    with closing(get_db_connection()) as conn:
        cur = conn.execute(query, params)
        if commit:
            conn.commit()
        return cur


def fetch_one(query, params=()):
    with closing(get_db_connection()) as conn:
        cur = conn.execute(query, params)
        return cur.fetchone()


def fetch_all(query, params=()):
    with closing(get_db_connection()) as conn:
        cur = conn.execute(query, params)
        return cur.fetchall()


# =========================================================
# USUARIOS
# =========================================================
def get_user_by_email(email):
    return fetch_one(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    )


def get_user_by_id(user_id):
    return fetch_one(
        "SELECT * FROM users WHERE idUser = ?",
        (user_id,)
    )


def create_user(name, email, password_hash, role="user"):
    execute_query(
        """
        INSERT INTO users (name, email, password, role)
        VALUES (?, ?, ?, ?)
        """,
        (name, email, password_hash, role),
        commit=True
    )


def count_users():
    row = fetch_one("SELECT COUNT(*) AS total FROM users")
    return row["total"] if row else 0


# =========================================================
# LIBROS
# =========================================================
def get_book_genres():
    rows = fetch_all(
        """
        SELECT DISTINCT genre
        FROM books
        WHERE genre IS NOT NULL AND genre != ''
        ORDER BY genre
        """
    )
    return [row["genre"] for row in rows]


def get_book_authors():
    rows = fetch_all(
        """
        SELECT DISTINCT author
        FROM books
        WHERE author IS NOT NULL AND author != ''
        ORDER BY author
        """
    )
    return [row["author"] for row in rows]


def get_book_publishers():
    rows = fetch_all(
        """
        SELECT DISTINCT publisher
        FROM books
        WHERE publisher IS NOT NULL AND publisher != ''
        ORDER BY publisher
        """
    )
    return [row["publisher"] for row in rows]


def get_all_books(query=None, genre=None, author=None, publisher=None, 
                  year_min=None, year_max=None, min_rating=None,
                  available_only=False, sort_by="title_asc"):
    sql = """
        SELECT
            b.idBook,
            b.title,
            b.author,
            b.genre,
            b.publisher,
            b.year,
            b.synopsis,
            b.cover_url,
            b.is_available,
            ROUND(AVG(r.rating), 1) AS avg_rating
        FROM books b
        LEFT JOIN reviews r ON b.idBook = r.idBookRef
    """
    conditions = []
    params = []

    if query:
        conditions.append("(b.title LIKE ? OR b.author LIKE ? OR b.genre LIKE ?)")
        like_query = f"%{query}%"
        params.extend([like_query, like_query, like_query])

    if genre:
        conditions.append("b.genre = ?")
        params.append(genre)

    if author:
        conditions.append("b.author = ?")
        params.append(author)

    if publisher:
        conditions.append("b.publisher = ?")
        params.append(publisher)

    if year_min:
        conditions.append("b.year >= ?")
        params.append(year_min)
    
    if year_max:
        conditions.append("b.year <= ?")
        params.append(year_max)

    if available_only:
        conditions.append("b.is_available = 1")

    sql += " GROUP BY b.idBook "
    
    # El filtro de rating se aplica después del GROUP BY usando HAVING
    having_conditions = []
    if min_rating:
        having_conditions.append("AVG(r.rating) >= ?")
        params.append(min_rating)

    if conditions:
        sql = sql.replace(" GROUP BY b.idBook ", " WHERE " + " AND ".join(conditions) + " GROUP BY b.idBook ")

    if having_conditions:
        sql += " HAVING " + " AND ".join(having_conditions)

    # Ordenamiento
    if sort_by == "title_asc":
        sql += " ORDER BY b.title ASC "
    elif sort_by == "title_desc":
        sql += " ORDER BY b.title DESC "
    elif sort_by == "rating_desc":
        sql += " ORDER BY avg_rating DESC, b.title ASC "
    elif sort_by == "year_desc":
        sql += " ORDER BY b.year DESC, b.title ASC "
    elif sort_by == "year_asc":
        sql += " ORDER BY b.year ASC, b.title ASC "
    elif sort_by == "newest":
        sql += " ORDER BY b.idBook DESC "
    else:
        sql += " ORDER BY b.title ASC "

    return fetch_all(sql, tuple(params))


def get_book_by_id(book_id):
    return fetch_one(
        """
        SELECT
            b.idBook,
            b.title,
            b.author,
            b.genre,
            b.publisher,
            b.year,
            b.synopsis,
            b.cover_url,
            b.is_available,
            ROUND(AVG(r.rating), 1) AS avg_rating
        FROM books b
        LEFT JOIN reviews r ON b.idBook = r.idBookRef
        WHERE b.idBook = ?
        GROUP BY b.idBook
        """,
        (book_id,)
    )


def get_book_reviews(book_id):
    return fetch_all(
        """
        SELECT
            r.idReview,
            r.rating,
            r.comment,
            r.created_at,
            r.updated_at,
            u.name AS user_name
        FROM reviews r
        JOIN users u ON u.idUser = r.idUserRef
        WHERE r.idBookRef = ?
        ORDER BY r.created_at DESC
        """,
        (book_id,)
    )


def get_average_rating(book_id):
    row = fetch_one(
        "SELECT ROUND(AVG(rating), 1) AS avg_rating FROM reviews WHERE idBookRef = ?",
        (book_id,)
    )
    return row["avg_rating"] if row and row["avg_rating"] is not None else None


def count_books():
    row = fetch_one("SELECT COUNT(*) AS total FROM books")
    return row["total"] if row else 0


def create_book(title, author, genre, publisher, year, synopsis, cover_url, is_available=True):
    execute_query(
        """
        INSERT INTO books (title, author, genre, publisher, year, synopsis, cover_url, is_available)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (title, author, genre, publisher, year, synopsis, cover_url, 1 if is_available else 0),
        commit=True
    )


def update_book(book_id, title, author, genre, publisher, year, synopsis, cover_url, is_available):
    execute_query(
        """
        UPDATE books
        SET title = ?,
            author = ?,
            genre = ?,
            publisher = ?,
            year = ?,
            synopsis = ?,
            cover_url = ?,
            is_available = ?
        WHERE idBook = ?
        """,
        (title, author, genre, publisher, year, synopsis, cover_url, 1 if is_available else 0, book_id),
        commit=True
    )


def delete_book(book_id):
    # Nota: La base de datos tiene llaves foráneas activadas. 
    # Si hay préstamos o reseñas vinculadas, se debe decidir si borrar en cascada o impedir el borrado.
    # Por ahora simplemente intentamos borrar.
    execute_query("DELETE FROM books WHERE idBook = ?", (book_id,), commit=True)


def get_top_rated_books(limit=5):
    return fetch_all(
        """
        SELECT
            b.idBook,
            b.title,
            b.author,
            b.genre,
            b.cover_url,
            ROUND(AVG(r.rating), 1) AS avg_rating
        FROM books b
        JOIN reviews r ON b.idBook = r.idBookRef
        GROUP BY b.idBook
        ORDER BY avg_rating DESC, b.title ASC
        LIMIT ?
        """,
        (limit,)
    )


def get_random_recommendations(limit=6):
    return fetch_all(
        """
        SELECT
            b.idBook,
            b.title,
            b.author,
            b.genre,
            b.cover_url,
            ROUND(AVG(r.rating), 1) AS avg_rating
        FROM books b
        LEFT JOIN reviews r ON b.idBook = r.idBookRef
        GROUP BY b.idBook
        ORDER BY RANDOM()
        LIMIT ?
        """,
        (limit,)
    )


# =========================================================
# PRÉSTAMOS
# =========================================================
def get_active_loan(user_id, book_id):
    return fetch_one(
        """
        SELECT *
        FROM loans
        WHERE idUserRef = ? AND idBookRef = ? AND status = 'active'
        """,
        (user_id, book_id)
    )


def create_loan(user_id, book_id):
    with closing(get_db_connection()) as conn:
        try:
            conn.execute("BEGIN")
            conn.execute(
                """
                INSERT INTO loans (idUserRef, idBookRef, loan_date, status)
                VALUES (?, ?, CURRENT_TIMESTAMP, 'active')
                """,
                (user_id, book_id)
            )
            conn.execute(
                "UPDATE books SET is_available = 0 WHERE idBook = ?",
                (book_id,)
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise


def return_loan(loan_id):
    with closing(get_db_connection()) as conn:
        try:
            conn.execute("BEGIN")

            loan = conn.execute(
                "SELECT * FROM loans WHERE idLoan = ?",
                (loan_id,)
            ).fetchone()

            if loan is None:
                raise ValueError("El préstamo no existe")

            conn.execute(
                """
                UPDATE loans
                SET return_date = CURRENT_TIMESTAMP,
                    status = 'returned'
                WHERE idLoan = ?
                """,
                (loan_id,)
            )

            conn.execute(
                "UPDATE books SET is_available = 1 WHERE idBook = ?",
                (loan["idBookRef"],)
            )

            conn.commit()
        except Exception:
            conn.rollback()
            raise


def get_user_loan_history(user_id):
    return fetch_all(
        """
        SELECT
            l.idLoan,
            l.loan_date,
            l.return_date,
            l.status,
            b.idBook,
            b.title,
            b.author
        FROM loans l
        JOIN books b ON b.idBook = l.idBookRef
        WHERE l.idUserRef = ?
        ORDER BY l.loan_date DESC
        """,
        (user_id,)
    )


def count_active_loans():
    row = fetch_one(
        "SELECT COUNT(*) AS total FROM loans WHERE status = 'active'"
    )
    return row["total"] if row else 0


# =========================================================
# RESEÑAS
# =========================================================
def has_user_borrowed_book(user_id, book_id):
    row = fetch_one(
        """
        SELECT 1
        FROM loans
        WHERE idUserRef = ? AND idBookRef = ? AND status IN ('active', 'returned')
        LIMIT 1
        """,
        (user_id, book_id)
    )
    return row is not None


def get_review_by_user_and_book(user_id, book_id):
    return fetch_one(
        """
        SELECT *
        FROM reviews
        WHERE idUserRef = ? AND idBookRef = ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (user_id, book_id)
    )


def create_review(user_id, book_id, rating, comment):
    execute_query(
        """
        INSERT INTO reviews (idUserRef, idBookRef, rating, comment, created_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
        (user_id, book_id, rating, comment),
        commit=True
    )


def update_review(review_id, user_id, rating, comment):
    execute_query(
        """
        UPDATE reviews
        SET rating = ?,
            comment = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE idReview = ? AND idUserRef = ?
        """,
        (rating, comment, review_id, user_id),
        commit=True
    )


def delete_review(review_id, user_id):
    execute_query(
        "DELETE FROM reviews WHERE idReview = ? AND idUserRef = ?",
        (review_id, user_id),
        commit=True
    )


# =========================================================
# DASHBOARD / ESTADÍSTICAS
# =========================================================
def get_dashboard_stats():
    top_books = get_top_rated_books(limit=5)

    return {
        "total_books": count_books(),
        "total_users": count_users(),
        "active_loans": count_active_loans(),
        "top_books": top_books
    }