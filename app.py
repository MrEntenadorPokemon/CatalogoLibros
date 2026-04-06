import os

from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash

from data import (
    RegisterForm, LoginForm, SearchBookForm, LoanForm, ReturnLoanForm,
    ReviewForm, DeleteForm,
    get_user_by_email, create_user,
    get_all_books, get_book_by_id, get_book_genres,
    get_book_reviews, get_average_rating,
    create_loan, get_active_loan, return_loan,
    has_user_borrowed_book, get_review_by_user_and_book,
    create_review, update_review, delete_review,
    get_user_loan_history, get_dashboard_stats
)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "cambia_esto_por_una_clave_segura")


@app.route("/")
def index():
    return redirect(url_for("catalog"))


# =========================================================
# AUTENTICACIÓN
# =========================================================
@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("catalog"))

    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = get_user_by_email(form.email.data.lower().strip())
        if existing_user:
            flash("Ese correo ya está registrado.", "danger")
            return render_template("auth/register.html", form=form)

        password_hash = generate_password_hash(form.password.data)
        create_user(
            name=form.name.data.strip(),
            email=form.email.data.lower().strip(),
            password_hash=password_hash,
            role="user"
        )

        flash("Usuario registrado correctamente. Ya puedes iniciar sesión.", "success")
        return redirect(url_for("login"))

    return render_template("auth/register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("catalog"))

    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_email(form.email.data.lower().strip())

        if not user or not check_password_hash(user["password"], form.password.data):
            flash("Correo o contraseña incorrectos.", "danger")
            return render_template("auth/login.html", form=form)

        session["user_id"] = user["idUser"]
        session["user_name"] = user["name"]
        session["user_email"] = user["email"]
        session["user_role"] = user["role"]

        flash("Sesión iniciada correctamente.", "success")
        return redirect(url_for("catalog"))

    return render_template("auth/login.html", form=form)


@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("login"))


# =========================================================
# CATÁLOGO / BÚSQUEDA
# =========================================================
@app.route("/catalog")
def catalog():
    query = request.args.get("q", "").strip()
    genre = request.args.get("genre", "").strip()

    books = get_all_books(query=query or None, genre=genre or None)
    genres = get_book_genres()

    return render_template(
        "books/catalog.html",
        books=books,
        genres=genres
    )


# =========================================================
# DETALLE DE LIBRO
# =========================================================
@app.route("/books/<int:book_id>")
def book_detail(book_id):
    book = get_book_by_id(book_id)
    if book is None:
        abort(404)

    reviews = get_book_reviews(book_id)
    avg_rating = get_average_rating(book_id)

    return render_template(
        "books/detail.html",
        book=book,
        reviews=reviews,
        avg_rating=avg_rating
    )


# =========================================================
# PRÉSTAMOS
# =========================================================
@app.route("/books/<int:book_id>/borrow", methods=["POST"])
def borrow_book(book_id):
    if not session.get("user_id"):
        flash("Debes iniciar sesión para solicitar un préstamo.", "warning")
        return redirect(url_for("login"))

    book = get_book_by_id(book_id)
    if book is None:
        abort(404)

    if not book["is_available"]:
        flash("Este libro no está disponible actualmente.", "danger")
        return redirect(url_for("book_detail", book_id=book_id))

    active_loan = get_active_loan(session["user_id"], book_id)
    if active_loan:
        flash("Ya tienes un préstamo activo para este libro.", "warning")
        return redirect(url_for("book_detail", book_id=book_id))

    try:
        create_loan(session["user_id"], book_id)
        flash("Préstamo solicitado correctamente.", "success")
    except Exception:
        flash("No se pudo registrar el préstamo.", "danger")

    return redirect(url_for("book_detail", book_id=book_id))


@app.route("/loans/history")
def loan_history():
    if not session.get("user_id"):
        flash("Debes iniciar sesión para ver tu historial.", "warning")
        return redirect(url_for("login"))

    loans = get_user_loan_history(session["user_id"])
    return render_template("loans/history.html", loans=loans)


@app.route("/loans/<int:loan_id>/return", methods=["POST"])
def return_book(loan_id):
    if not session.get("user_id"):
        flash("Debes iniciar sesión.", "warning")
        return redirect(url_for("login"))

    try:
        return_loan(loan_id)
        flash("Libro devuelto correctamente.", "success")
    except Exception:
        flash("No se pudo registrar la devolución.", "danger")

    return redirect(url_for("loan_history"))


# =========================================================
# RESEÑAS
# =========================================================
@app.route("/books/<int:book_id>/reviews/add", methods=["POST"])
def add_review(book_id):
    if not session.get("user_id"):
        flash("Debes iniciar sesión para escribir una reseña.", "warning")
        return redirect(url_for("login"))

    book = get_book_by_id(book_id)
    if book is None:
        abort(404)

    if not has_user_borrowed_book(session["user_id"], book_id):
        flash("Solo puedes reseñar libros que hayas prestado.", "warning")
        return redirect(url_for("book_detail", book_id=book_id))

    form = ReviewForm()
    if form.validate_on_submit():
        existing_review = get_review_by_user_and_book(session["user_id"], book_id)

        try:
            if existing_review:
                update_review(
                    review_id=existing_review["idReview"],
                    user_id=session["user_id"],
                    rating=int(form.rating.data),
                    comment=form.comment.data
                )
                flash("Reseña actualizada correctamente.", "success")
            else:
                create_review(
                    user_id=session["user_id"],
                    book_id=book_id,
                    rating=int(form.rating.data),
                    comment=form.comment.data
                )
                flash("Reseña creada correctamente.", "success")
        except Exception:
            flash("No se pudo guardar la reseña.", "danger")

    else:
        flash("Revisa los datos de la reseña.", "warning")

    return redirect(url_for("book_detail", book_id=book_id))


@app.route("/reviews/<int:review_id>/delete", methods=["POST"])
def remove_review(review_id):
    if not session.get("user_id"):
        flash("Debes iniciar sesión.", "warning")
        return redirect(url_for("login"))

    try:
        delete_review(review_id, session["user_id"])
        flash("Reseña eliminada correctamente.", "success")
    except Exception:
        flash("No se pudo eliminar la reseña.", "danger")

    return redirect(url_for("catalog"))


# =========================================================
# DASHBOARD
# =========================================================
@app.route("/admin/dashboard")
def dashboard():
    if not session.get("user_id") or session.get("user_role") != "admin":
        abort(403)

    stats = get_dashboard_stats()
    return render_template("admin/dashboard.html", stats=stats)


# =========================================================
# ERRORES
# =========================================================
@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(403)
def forbidden(error):
    return render_template("errors/403.html"), 403


if __name__ == "__main__":
    app.run(debug=True)