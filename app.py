from flask import Flask, request, redirect, jsonify, render_template 
from urllib.parse import urlparse
import sqlite3
import string
import random

app = Flask(__name__)


# Create the database
def init_db():
    connection = sqlite3.connect("urls.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT UNIQUE NOT NULL,
            original_url TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# Generate a random short code
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


# Home route
@app.route("/")
def home():
    return render_template("index.html")


# Create a shortened URL
@app.route("/shorten", methods=["POST"])
def shorten_url():
    data = request.get_json()

    original_url = data.get("url")

    if not original_url:
        return jsonify({"error": "URL is required"}), 400
    parsed_url = urlparse(original_url)

    if parsed_url.scheme not in ["http", "https"] or not parsed_url.netloc:
        return jsonify({"error": "Please enter a valid URL."}), 400

    short_code = generate_short_code()

    connection = sqlite3.connect("urls.db")
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO urls (short_code, original_url) VALUES (?, ?)",
        (short_code, original_url)
    )

    connection.commit()
    connection.close()

    short_url = f"http://127.0.0.1:5000/{short_code}"

    return jsonify({
        "original_url": original_url,
        "short_url": short_url
    })


# Redirect to the original URL
@app.route("/<short_code>")
def redirect_to_url(short_code):
    connection = sqlite3.connect("urls.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT original_url FROM urls WHERE short_code = ?",
        (short_code,)
    )

    result = cursor.fetchone()

    connection.close()

    if result:
        return redirect(result[0])

    return "Short URL not found", 404


if __name__ == "__main__":
    init_db()
    app.run(debug=True)