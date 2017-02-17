from flask import Flask, render_template, request, redirect, url_for

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import os

app = Flask(__name__)
app.config['STATIC_FOLDER'] = 'static'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///datastore.db'    # /// is for relative path
app.config['SECRET_KEY'] = os.urandom(30)

# Create DB object
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

## For each table in the DB, create a seperate class

# Table-1: User table template
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True)    # also serves as username
    name = db.Column(db.String(100))
    department = db.Column(db.String(100))
    password = db.Column(db.String(50))

    def __init__(self, email, password, name, department):
        self.email = email
        self.password = password
        self.name = name
        self.department = department

    def __repr__(self):
        return '<User %r>' % self.email

"""
#Table-2: book details
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(254))
    department = db.Column(db.String(100))
    email = db.Column(db.String(254), unique=True)
    book_name = db.Column(db.String(254))
    book_edition = db.Column(db.Integer(20))
    author_name = db.Column(db.String(254))
    price = db.Column(db.Integer(20))

    def __init__(self, name, department, email, book_name, book_edition, author_name ):
        self.name = name
        self.department = department
        self.email=email
        self.book_name=book_name
        self.book_edition=book_edition
        self.author_name=author_name

    def __repr__(self):
        return '<User %r>' % self.email
"""

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":    # any POST call will be handled by request object
        form = request.form
        email = form["email"]
        password = form["psw"]
        # check if email and corresponding password exists in the database
        # If yes
        user = User.query.filter_by(email=email).filter_by(password=password).first()
        if user:
            login_user(user)
            return redirect("/profile")
        else:
            return redirect("/")

    return render_template("home1.html")

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        return redirect("/upload")
    return render_template("userpro.html")

@app.route("/upload")
@login_required
def upload():

    return  render_template("upload.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        print "signup post"
        form = request.form
        name = form["name"]
        department = form["dpt"]
        email = form["email"]
        password = form["pwd1"]
        # conpassword = form["pwd2"]    # prevalidated in front-end

        # Add new user info to DB
        new_user = User(name=name, email=email, department=department, password=password)    # create a User table record (row)
        db.session.add(new_user)
        db.session.commit()

        return redirect("/")

    return render_template("signup.html")

@app.route("/logout")
@login_required
def signout():
    logout_user()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)