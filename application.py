import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

    # Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///final.db")

@app.route("/")
def index():
    #show main page for everyone where there are links to both filling a request and
    #going to the volunteer interface
    return render_template("index.html")

@app.route("/home")
@login_required
def home():
    #for each volunteer shows a table of people in his location that needs help
    city = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]["city"].lower()
    area = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]["area"].lower()
    rows = db.execute("SELECT * FROM askers WHERE city = ? AND helper = ? ORDER BY date", city, "no" )
    rows2 = db.execute("SELECT * FROM askers WHERE area = ? AND city != ? AND helper = ? ORDER BY date"
       , area, city, "no" )
    return render_template("home.html", rows = rows, rows2 = rows2)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()
    if request.method == "GET":
        # User reached route via GET (as by clicking a link or via redirect)
        return render_template("login.html")
    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/home")



@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    #register user
    if request.method == "GET":
       return render_template("register.html")
    else:
         # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        #ensure password verification was submitted
        elif not request.form.get("v-password"):
            return apology("must verify your password", 403)
        #ensure area was submitted
        elif not request.form.get("area"):
            return apology("must provide area", 403)
        #ensure city was submitted
        elif not request.form.get("city"):
            return apology("must provide city", 403)
        #ensure first name was submitted
        elif not request.form.get("f-name"):
            return apology("must provide first name", 403)
        #ensure last name was submitted
        elif not request.form.get("l-name"):
            return apology("must provide last name", 403)
        #ensure phone number was submitted
        elif not request.form.get("phone"):
            return apology("must provide phone number", 403)
        #check if password match verification
        elif request.form.get("password") != request.form.get("v-password"):
            return apology("Passwords do not match", 403)
        #check if username already exists
        else:
            rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
            if len(rows) != 0:
                return apology("username already exists", 404)

            #checks if password has both letters and numbers
            password = request.form.get("password")

            let = False
            num = False
            for letter in password:
                if ord(letter) in range (48,58): #ord() gets ascii code
                    num = True
                if ord(letter) in range (65,91):
                    let = True
                if ord(letter) in range (97,123):
                    let = True
            if num == False:
                return apology ("password must have numbers", 403)
            if let == False:
                return apology ("password must have letters", 403)
            if len(password) < 6:
                return apology ("password must be atleast 6 letters long", 403)
            #checks if area is correct
            area = request.form.get("area").lower()
            if area!= "center" and area != "north" and area != "south":
                return apology ("invalid area", 403)
            #checks if phone number is valid
            phone = request.form.get("phone")
            if len(phone) < 10 or phone.isdigit() == False:
                return apology ("invalid phone number", 403)
            #checks if name includes only letters
            username = request.form.get("username")
            this_hash = generate_password_hash(request.form.get("password"))
            f_name = request.form.get("f-name")
            l_name = request.form.get("l-name")
            area = request.form.get("area").lower()
            phone = request.form.get("phone")
            city = request.form.get("city").lower()
            if f_name.isalpha() == False:
                return apology ("invalid first name", 403)
            if l_name.isalpha() == False:
                return apology ("invalid last name", 403)
            #check city
            for letter in city:
                if letter.isalpha() == False and letter !=" ":
                    return apology ("invalid city name", 403)
            #everything is good, adds to database
            db.execute("INSERT INTO users (username, password, f_name, l_name, city, area, phone) VALUES(?,?,?,?,?,?,?);"
              , username, this_hash, f_name, l_name, city, area, phone,)
            return redirect("/login")

@app.route("/helping", methods=["GET", "POST"])
def helping():
    if request.method == "GET":
        return render_template("helping.html")
    else:
         # Ensure name was submitted
        if not request.form.get("name"):
            return apology("must provide name", 403)
        #ensure type was submitted
        if not request.form.get("type"):
            return apology("must provide help type", 403)
        #ensure city was submitted
        elif not request.form.get("city"):
            return apology("must provide city", 403)
        #ensure phone was submitted
        elif not request.form.get("phone"):
            return apology("must provide phone number", 403)
        #check name
        help_type = request.form.get("type")
        name = request.form.get("name")
        city = request.form.get("city").lower()
        area = request.form.get("area").lower()
        phone = request.form.get("phone")
        for letter in name:
            if letter.isalpha() == False and letter !=" ":
                return apology ("invalid name", 403)
        #check help type
        if help_type not in ["food", "med", "other"]:
            return apology ("help must be food/med/other", 403)
        #check city
        for letter in city:
            if letter.isalpha() == False and letter !=" ":
                return apology ("invalid city name", 403)
         #checks if area is correct
        if area!= "center" and area != "north" and area != "south":
            return apology ("invalid area", 403)
        #check phone
        if len(phone) < 10 or phone.isdigit() == False:
            return apology ("invalid phone number", 403)
        #everything is good, insert to database
        db.execute("INSERT INTO askers(name,help_type,city,area,phone,date) VALUES(?,?,?,?,?,?)"
          , name, help_type, city, area, phone, datetime.now())
        return render_template("helped.html")

@app.route("/report", methods=["GET", "POST"])
@login_required
def report():
    if request.method == "GET":
        return render_template("report.html")
    else:
         # Ensure id was submitted
        if not request.form.get("request"):
            return apology("must provide id", 403)
         # Ensure name was submitted
        if not request.form.get("name"):
            return apology("must provide name", 403)
        #ensure there is a request with the matching name and request id
        request_id = request.form.get("request")
        name = request.form.get("name")
        rows = db.execute("SELECT * FROM askers WHERE name = ? and id = ?", name, request_id)
        if len(rows) != 1:
            return apology("incorrect details", 403)
        #all good, continue
        username = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]["username"]
        db.execute("UPDATE askers SET helper = ? WHERE id = ?", username, request_id)
        return render_template("reported.html")

@app.route("/history")
@login_required
def history():
    username = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]["username"]
    rows = db.execute("SELECT * FROM askers WHERE helper = ? ORDER BY date DESC", username)
    return render_template("history.html", rows = rows)






def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
