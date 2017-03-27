from flask import Flask, render_template, request, redirect, url_for, flash, make_response

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import dropbox
import os
import uuid
import datetime
from whoosh.analysis import StemmingAnalyzer
import flask_whooshalchemy
import json
from flask_basicauth import BasicAuth
from custom_exceptions import *


app = Flask(__name__)
app.config['STATIC_FOLDER'] = 'static'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///datastore.db')    # /// is for relative path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['BASIC_AUTH_USERNAME'] = 'projectbookshelf2017@gmail.com'
app.config['BASIC_AUTH_PASSWORD'] = 'G680y7%4'
app.config['SECRET_KEY'] = os.urandom(30)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'

# These are the extension that we are accepting to be uploaded
# app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['ALLOWED_EXTENSIONS'] = set(['pdf',])

#  dropbox configuration
dropbox_token = "A5RdmUqkkXAAAAAAAAAACvYfU28rObYWB_hs60GCleXmTVjc2lYMa1JnwKvXxnWV"

# app.config['DROPBOX_KEY'] = 'd7vcyguscijcpdw'
# app.config['DROPBOX_SECRET'] = 'uvjjh2xkyz9qhbj'
# app.config['DROPBOX_ACCESS_TYPE'] = 'app_folder'

# Create DB object
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
admin = Admin(app, name="bookshelf admin", template_mode="bootstrap3")

# dropbox = Dropbox(app)
# dropbox.register_blueprint(url_prefix='/dropbox')

# Whoosh search
# basedir = os.path.dirname(os.path.abspath(__name__))
# WHOOSH_BASE = os.path.join(basedir, 'search.db')


## For each table in the DB, create a seperate class

# Table-1: User table template
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True)    # also serves as username
    name = db.Column(db.String(100))
    department = db.Column(db.String(100))
    password = db.Column(db.String(50))
    notes_bought = db.Column(db.Text())  # JSON list of notes items bought
    books = db.relationship('Books', backref='users', lazy='dynamic')
    notes_owned = db.relationship('Notes', backref='users', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % self.email

#Table-2: book details
class Books(db.Model):
    __searchable__ = ['book_name', 'author_name'] # author_name
    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(254))
    book_edition = db.Column(db.Integer)
    author_name = db.Column(db.String(254))
    price = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Books %r>' % self.book_name

# Table-3: Notes
class Notes(db.Model):
    __searchable__ = ['title', 'description']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(254))
    description = db.Column(db.Text())
    original_filename = db.Column(db.String(512))
    dropbox_path = db.Column(db.Text())
    content_hash = db.Column(db.String(254))
    price = db.Column(db.Integer())

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Notes %r>' % self.title

# Creating basic_auth obj
basic_auth = BasicAuth(app)

class AuthModelView(ModelView):
    """Overriding inbuilt ModelView class with this class so that, the password protection applies only to admin"""
    def is_accessible(self):
        if not basic_auth.authenticate():
            raise AuthException("Not Authenticated")
        else:
            return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(basic_auth.challenge())

# Adding table views to admin panel
admin.add_view(AuthModelView(Users, db.session))
admin.add_view(AuthModelView(Books, db.session))
admin.add_view(AuthModelView(Notes, db.session))

flask_whooshalchemy.whoosh_index(app, Books)
flask_whooshalchemy.whoosh_index(app, Notes)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# support functions
def allowed_file(filename):
    """ For a given file, return whether it's an allowed type or not"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# Routes
@app.route("/", methods=["GET", "POST"])
def home():
    # print(dropbox.is_authenticated)
    if request.method == "POST":    # any POST call will be handled by request object
        form = request.form
        email = form["email"]
        password = form["psw"]
        # check if email and corresponding password exists in the database
        # If yes
        user = Users.query.filter_by(email=email).filter_by(password=password).first()
        if user:
            login_user(user)
            return redirect("/profile")
        else:
            flash("Unauthorized User. Please Signup")
            # return redirect("/")
    flash("Hi user")
    print("Hi user")
    return render_template("home1.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        print "signup post"
        # TODO Check if the user already exists

        form = request.form
        print(form)

        name = form["name"]
        department = form["dpt"]
        email = form["email"]
        password = form["pwd1"]
        # conpassword = form["pwd2"]    # prevalidated in front-end


        # Add new user info to DB
        new_user = Users(name=name, email=email, department=department, password=password)    # create a Users table record (row)
        db.session.add(new_user)
        db.session.commit()

        return redirect("/")

    return render_template("signup.html")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        print(request.form)
        search_text = request.form.get('search')
        book_results = Books.query.whoosh_search(search_text).all()
        note_results = Notes.query.whoosh_search(search_text).all()
        book_names = [item.book_name for item in book_results]
        note_names = [{"id": item.id, "title": item.title, "description": item.description, "price": item.price*100} for item in note_results]
        print(book_names)
        print(note_names)
        return redirect(url_for("search_results", book_results=json.dumps(book_names),
                                note_results=json.dumps(note_names)))
    return render_template("userpro.html")

@app.route("/results", methods=['GET', 'POST'])
@login_required
def search_results():
    if request.method == "POST":
        print("After transaction")
        print(request.form)
        form = request.form
        notes_id = form['notes_id']  # Notes ID
        payment_id = form['razorpay_payment_id']    # TODO store this in DB
        notes_bought_json = current_user.notes_bought

        if not notes_bought_json:
            # if empty, create a empty list
            notes_bought_json = "[]"

        notes_bought = json.loads(notes_bought_json)
        notes_bought.append(int(notes_id))
        notes_bought_json = json.dumps(notes_bought)
        current_user.notes_bought = notes_bought_json
        db.session.commit()

        # Download file from dropbox
        client = dropbox.Dropbox(dropbox_token)
        notes_obj = Notes.query.filter_by(id=int(notes_id)).first()
        path = notes_obj.dropbox_path

        # TODO Check for content hash
        try:
            md, res = client.files_download(path)
        except dropbox.exceptions.HttpError as err:
            print('*** HTTP error', err)
            return None

        data = res.content
        print(len(data), 'bytes; md:', md)
        original_filename = notes_obj.original_filename

        response = make_response(data)
        response.headers["Content-Disposition"] = "attachment; filename={FILENAME}".format(FILENAME=original_filename)
        return response

    book_results = request.args["book_results"]
    note_results = request.args["note_results"]
    return render_template('search_results.html', book_results=json.loads(book_results), note_results=json.loads(note_results))

@app.route("/upload", methods=['GET', 'POST'])
@login_required
def upload():
    print(current_user.email)
    print(current_user)
    if request.method == "POST":
        print("Trying to upload")
        form = request.form
        print(form)
        title = form.get("title")
        description = form.get("description")
        price = form.get("price")
        print(title, price)
        # Get the name of the uploaded file
        file = request.files['file']

        # print(file.filename, title, price)
        # print(file.__dict__)

        client = dropbox.Dropbox(dropbox_token)
        _, ext = os.path.splitext(file.filename)    # splits file's name and extenstion
        dropbox_filename = str(uuid.uuid1()) + ext
        path = '/%s' % (dropbox_filename)
        mode = dropbox.files.WriteMode.add
        data = file.read()
        try:
            res = client.files_upload(
                data, path, mode,
                client_modified=datetime.datetime.now(),
                mute=True)
        except dropbox.exceptions.ApiError as err:
            print('*** API error', err)
            return None

        print(res)
        print(path)
        saved_path = res._path_lower_value
        content_hash = res._content_hash_value    # a hash represents the data in the file. This is useful to check if later the file downloaded from dropbox is corrupt/not

        # create a db entry
        note = Notes(title=title, description=description, original_filename=file.filename, dropbox_path=saved_path,
                     content_hash=content_hash, price=price)
        note.user_id = current_user.id
        # Add to database
        db.session.add(note)
        db.session.commit()


        flash("File uploaded successfully")
        print("File uploaded successfully")
        return redirect("/profile")

    return render_template("upload.html")

@app.route("/book", methods=["GET", "POST"])
@login_required
def book():
    if request.method == "POST":
        form = request.form
        bookname = form.get("bname")
        edition = form.get("bedition")
        author = form.get("Aname")
        price = form.get("srate")

        buk = Books(book_name=bookname, book_edition=edition, author_name=author, price=price)
        buk.user_id = current_user.id

        db.session.add(buk)
        db.session.commit()

        flash("Book added successfully")

        return redirect("/profile")

    return render_template("book.html")


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    pass

@app.route("/logout")
@login_required
def signout():
    logout_user()
    return redirect("/")

@app.route("/select", methods=["GET", "POST"])
@login_required
def select():
    if request.method == "POST":
        print(request.form)
        search_text = request.form.get('search')
        book_results = Books.query.whoosh_search(search_text).all()
        note_results = Notes.query.whoosh_search(search_text).all()
        book_names = [item.book_name for item in book_results]
        note_names = [{"id": item.id, "title": item.title, "description": item.description, "price": item.price*100} for item in note_results]
        print(book_names)
        print(note_names)
        return redirect(url_for("search_results", book_results=json.dumps(book_names),
                                note_results=json.dumps(note_names)))

    return render_template("select.html")


if __name__ == "__main__":
    app.run(debug=True)