from flask import (
    Flask, render_template, request,
    redirect, url_for, session
)
from werkzeug.security import check_password_hash
from functools import wraps
import secrets
import sqlite3
import os

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY")

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH")

# Always use the database inside the restaurant folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")

def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped_view

def create_database():
    connection = sqlite3.connect(DATABASE)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            guests INTEGER NOT NULL
        )
    """)

    connection.commit()
    connection.close()


@app.route("/")
def home():
    return render_template("index.html")


# ONE reservation route only
@app.route("/reserve", methods=["POST"])
def reserve():

    name = request.form.get("name")
    phone = request.form.get("phone")
    date = request.form.get("date")
    time = request.form.get("time")
    guests = request.form.get("guests")

    connection = sqlite3.connect(DATABASE)

    connection.execute("""
        INSERT INTO reservations
        (name, phone, date, time, guests)
        VALUES (?, ?, ?, ?, ?)
    """, (name, phone, date, time, guests))

    connection.commit()
    connection.close()

    return """
    <html>
    <head>
        <title>Reservation Successful</title>
    </head>
    <body style="text-align:center; padding:50px;">
        <h1>Reservation Successful!</h1>
        <p>Your table has been booked successfully.</p>
        <a href="/">Back to Home</a>
        <br><br>
        <a href="/admin">View Admin Database</a>
    </body>
    </html>
    """


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if (
            username == ADMIN_USERNAME
            and ADMIN_PASSWORD_HASH
            and check_password_hash(ADMIN_PASSWORD_HASH, password)
        ):
            session.clear()
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))

        return render_template(
            "admin_login.html",
            error="Invalid username or password"
        )

    return render_template("admin_login.html")


@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


# Admin page
@app.route("/admin")
@admin_required
def admin():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    reservations = connection.execute(
        "SELECT * FROM reservations ORDER BY id DESC"
    ).fetchall()

    connection.close()

    session.setdefault("csrf_token", secrets.token_urlsafe(32))

    return render_template(
        "admin.html",
        reservations=reservations,
        csrf_token=session["csrf_token"]
    )

@app.route("/admin/delete/<int:reservation_id>", methods=["POST"])
@admin_required
def delete_reservation(reservation_id):
    submitted_token = request.form.get("csrf_token", "")
    saved_token = session.get("csrf_token", "")

    if not saved_token or not secrets.compare_digest(
        submitted_token, saved_token
    ):
        return "Invalid request. Please return to the admin page.", 400

    connection = sqlite3.connect(DATABASE)

    connection.execute(
        "DELETE FROM reservations WHERE id = ?",
        (reservation_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("admin"))

if __name__ == "__main__":
    create_database()
    app.run(debug=True)
