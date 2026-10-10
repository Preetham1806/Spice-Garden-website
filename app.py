from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

# Always use the database inside the restaurant folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")


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


# Admin page
@app.route("/admin")
def admin():

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    reservations = connection.execute(
        "SELECT * FROM reservations ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return render_template(
        "admin.html",
        reservations=reservations
    )


if __name__ == "__main__":
    create_database()
    app.run(debug=True)