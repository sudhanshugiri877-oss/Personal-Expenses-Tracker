from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import secrets

app = Flask(__name__)

# SECRET KEY — use a strong random key
app.secret_key = secrets.token_hex(32)

# DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

# =========================
# USER TABLE
# =========================

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True)

    password = db.Column(db.String(200))

# =========================
# EXPENSE TABLE
# =========================

class Expense(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    amount = db.Column(db.Float)

    category = db.Column(db.String(100))

    description = db.Column(db.String(200))

    user_id = db.Column(db.Integer)

# =========================
# LOGIN
# =========================

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])

def login():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):

            session["user"] = username

            return redirect("/dashboard")

        else:

            return "Invalid Username or Password"

    return render_template("login.html")

# =========================
# SIGNUP
# =========================

@app.route("/signup", methods=["GET", "POST"])

def signup():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        # FIX: Check if username already exists
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            return "Username already taken. Please choose another."

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(
            username=username,
            password=hashed_password
        )

        db.session.add(new_user)

        db.session.commit()

        return redirect("/login")

    return render_template("signup.html")

# =========================
# DASHBOARD
# =========================

@app.route("/dashboard", methods=["GET", "POST"])

def dashboard():

    if "user" not in session:

        return redirect("/login")

    # FIX: Get the actual logged-in user object
    user = User.query.filter_by(username=session["user"]).first()

    if request.method == "POST":

        amount = request.form["amount"]

        category = request.form["category"]

        description = request.form["description"]

        expense = Expense(
            amount=amount,
            category=category,
            description=description,
            user_id=user.id  # FIX: use real user ID, not hardcoded 1
        )

        db.session.add(expense)

        db.session.commit()

    # FIX: Only fetch expenses belonging to the current user
    expenses = Expense.query.filter_by(user_id=user.id).all()

    total = 0

    for expense in expenses:

        total += expense.amount

    return render_template(
        "dashboard.html",
        username=session["user"],
        expenses=expenses,
        total=total
    )

# =========================
# DELETE EXPENSE
# =========================

@app.route("/delete/<int:id>")

def delete(id):

    expense = Expense.query.get(id)

    db.session.delete(expense)

    db.session.commit()

    return redirect("/dashboard")

# =========================
# LOGOUT
# =========================

@app.route("/logout")

def logout():

    session.clear()

    return redirect("/login")

# =========================

if __name__ == "__main__":

    with app.app_context():

        db.create_all()

    app.run(debug=True)