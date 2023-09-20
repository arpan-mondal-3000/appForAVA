from flask import Flask, render_template, request, redirect, session
from flask_session import Session
import sqlite3
import hashlib
import datetime

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def hash_password(password):
    hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return hash


def upcoming_bdays():
    current_datetime = datetime.datetime.now()
    current_month = current_datetime.month
    current_date = current_datetime.date()

    connection = sqlite3.connect("userdata.db")
    cursor = connection.cursor()

    if len(str(current_month)) == 1:
        query = f"SELECT id,name,dob FROM userdata WHERE dob LIKE '%-0{current_month}-%'"
    else:
        query = f"SELECT id,name,dob FROM userdata WHERE dob LIKE '%-{current_month}-%'"

    cursor.execute(query)
    rows = cursor.fetchall()

    upcoming_bdays = []
    for i in range(0, len(rows)):
        name = rows[i][1]
        dob = rows[i][2]

        if int(dob[:2]) >= int(str(current_date)[-2:]):
            upcoming_bdays.append(f"{name.title()} - {dob[:2]}/{dob[3:5]}")

    cursor.close()
    connection.close()
    return upcoming_bdays


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
        user_password = request.form.get("password")
        hashed_password = hash_password(user_password)
        cursor.execute(
            f"SELECT password FROM userdata WHERE name = '{name.upper()}'")
        rows = cursor.fetchall()
        if rows != []:
            password = rows[0][0]
            cursor.close()
            connection.close()
            if password == hashed_password:
                session["name"] = request.form.get("name")
                return redirect("/")
            else:
                return render_template("login.html", msg="Invalid Password")
        else:
            return render_template("login.html", msg="Invalid username")
    return render_template("login.html", msg="")


@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")


@app.route("/birthday-finder")
def birthday_finder():
    if not session.get("name"):
        return redirect("/login")
    return render_template("birthdayfinder.html", text="Forgot his/her birthday? Not to worry, you are just one search away 😊", upcoming_list=upcoming_bdays())


@app.route("/search")
def search():
    if not session.get("name"):
        return redirect("/login")
    try:
        name = request.args.get("person_name")
        connection = sqlite3.connect("userdata.db")
        cursor = connection.cursor()
        cursor.execute(f"SELECT dob FROM userdata WHERE name LIKE '{name}%'")
        rows = cursor.fetchall()
        cursor.execute(f"SELECT name FROM userdata WHERE name LIKE '{name}%';")
        names = cursor.fetchall()
        if names != []:
            name = names[0][0]
        if rows != []:
            dob = rows[0][0]
            birthdate = dob[:2] + "/" + dob[3:5]
        cursor.close()
        connection.close()

        text = f"{name.title()}'s birthday is on {birthdate}"
        return render_template("birthdayfinder.html", text=text, party_emoji="🥳", confetti="🎉", upcoming_list=upcoming_bdays())
    except:
        return render_template("birthdayfinder.html", error_text="Name not found in the database, try with a different name!", upcoming_list=upcoming_bdays())


if __name__ == "__main__":
    app.run(debug=True)
