from flask import Flask, render_template, request, redirect, url_for, flash

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import dropbox
import os
import uuid
import datetime
# from werkzeug import secure_filename

app = Flask(__name__)
app.config['STATIC_FOLDER'] = 'static'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///datastore.db')    # /// is for relative path
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

## For each table in the DB, create a seperate class

# Table-1: User table template
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True)    # also serves as username
    name = db.Column(db.String(100))
    department = db.Column(db.String(100))
    password = db.Column(db.String(50))
    books = db.relationship('Books', backref='users', lazy='dynamic')
    notes = db.relationship('Notes', backref='users', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % self.email

#Table-2: book details
class Books(db.Model):
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
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(254))
    original_filename = db.Column(db.String(512))
    dropbox_path = db.Column(db.Text())
    content_hash = db.Column(db.String(254))
    price = db.Column(db.Integer())

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Notes %r>' % self.title

# Adding table views to admin panel
admin.add_view(ModelView(Users, db.session))
admin.add_view(ModelView(Books, db.session))
admin.add_view(ModelView(Notes, db.session))

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

    return render_template("home1.html")

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        return redirect("/upload")
    return render_template("userpro.html")

@app.route("/upload", methods=['GET', 'POST'])
@login_required
def upload():
    print(current_user.email)
    print(current_user)
    if request.method == "POST":
        print("Trying to upload")
        form = request.form
        title = form.get("title")
        price = form.get("price")

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
        note = Notes(title=title, original_filename=file.filename, dropbox_path=saved_path,
                     content_hash=content_hash, price=price)
        note.user_id = current_user.id
        # Add to database
        db.session.add(note)
        db.session.commit()

        flash("File uploaded successfully")

    return render_template("upload.html")

@app.route("/book")
@login_required
def book():
    return  render_template("book.html")

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
        new_user = Users(name=name, email=email, department=department, password=password)    # create a Users table record (row)
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