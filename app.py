import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from functions import *

# TODO: Reformat items and entries tables, items need their own ids seperate from userid
# TODO: Using this new ID, implement the addentry functionality by using the entry id instead of userid to avoid duplication
# TODO: Implement dynamic error messages



app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///progress.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        if session.get("user_id") is None:
            return redirect("/login")

        username = db.execute("SELECT username FROM users WHERE id = ?;", session["user_id"])  # CREATE TABLE items (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, userid INTEGER, name TEXT);

        items = db.execute("SELECT * FROM items WHERE userid = ?;", session["user_id"])

        for item in items:
            item["name"] = item["name"].title()

        if 1 <= len(items):
            return render_template("index.html", username=username[0]["username"], items=items)
        else:
            return render_template("index.html", username=username[0]["username"], items=None)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Forget user id
        session.clear()

        if not request.form.get("username"):
            return render_template("failure.html", message="Please enter a username")

        elif not request.form.get("password"):
            return render_template("failure.html", message="Please enter a password")

        rows = db.execute("SELECT * FROM users WHERE username = ?;", request.form.get("username"))

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("failure.html", message="Invalid username or password")

        if request.form.get("username") in rows[0]["username"]:

            session["user_id"] = rows[0]["id"]

            return redirect("/")

    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        usernames = db.execute("SELECT username FROM users;")

        if usernames:
            if request.form.get("username") in usernames[0]["username"]:
                return render_template("failure.html", message="Username taken")

        if request.form.get("confirm") != request.form.get("password"):
            return render_template("failure.html", message="Passwords do not match")

        hash = generate_password_hash(request.form.get("password"))

        db.execute("INSERT INTO users (username, hash) VALUES (?, ?);", request.form.get("username"), hash)

        id = db.execute("SELECT id FROM users WHERE hash = ?;", hash)

        session["user_id"] = id[0]["id"]

        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/view", methods=["GET", "POST"])
def view():
    if request.method == "GET":
        return redirect("/")

    else:

        id = request.form.get("id")

        item = db.execute("SELECT * FROM items WHERE id = ?;", id)

        entries = db.execute("SELECT * FROM entries WHERE id = ?;", id)

        if len(entries) >= 1:
            return render_template("view.html", item=item[0], entries=entries)

        else:
            return render_template("view.html", item=item[0], entries=None)

@app.route("/addentry", methods=["GET", "POST"])
def addentry():

    if request.method == "GET":
        return render_template("addentry.html")

    else:

        id = request.form.get("id")

        item = db.execute("SELECT * FROM items WHERE id = ?;", id)

        if not request.form.get("statement"):
            if not request.form.get("id2"):
                return render_template("addentry.html", id=id)
            else:
                return render_template("failure.html", message="Please enter a statement")

        else:
            id2 = request.form.get("id2")
            item = db.execute("SELECT * FROM items WHERE id = ?;", id2)
            now = datetime.now()
            db.execute("INSERT INTO entries (id, name, statement, date) VALUES (?, ?, ?, ?);", id2, item[0]["name"], request.form.get("statement"), now.strftime("%A %B %d, %I:%M%p"))
            return redirect("/view")


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        if not request.form.get("name"):
            return render_template("failure.html", message="Please enter name of journey")

        db.execute("INSERT INTO items (userid, name) VALUES (?, ?);", session["user_id"], request.form.get("name").title())

        items = db.execute("SELECT * FROM items;")

        if len(items) == 1:
            db.execute("UPDATE items SET id = 1000;")

        return redirect("/")

    else:
        return render_template("add.html")


@app.route("/failure")
def failure():
    return render_template("failure.html")


@app.route("/delete")
def delete():
    return render_template("delete.html")


@app.route("/sucess")
def sucess():
    return render_template("sucess.html")


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")