from flask import Flask, render_template, request, redirect, session
from flask_session import Session
import sqlite3

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/')
def index():
    if not session.get("name"):
        return redirect("/login")
    return render_template("index.html", name=session.get("name"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        connection = sqlite3.connect("userdata.db")
        cursor = connection.cursor()
        name = request.form.get("name")
        cursor.execute(f"SELECT password FROM userdata WHERE name = '{name}'")
        rows = cursor.fetchall()
        if rows != []:
            password = rows[0][0]
            cursor.close()
            connection.close()
            if password == request.form.get("password"):
                session["name"] = request.form.get("name")
                return redirect("/")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
