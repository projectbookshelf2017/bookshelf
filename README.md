Introduction
============



============
Python version: Py27
IDE: Pycharm Community Edition
Version control: Git

How to use Git Version control?
================================

1. Initialize a repo as a git repo

```
# in a bash/terminal/cmd prompt
cd /path/to/local/repo
git init
```

2. Stage files to be commited

```
git add filename
```

3. Commit file and give a message about your commit

```
git commit -m "I made these changes"
```

4. Whenever you want to know the status of your git repo, do

```
git status
```

Installing python libraries
===========================

Pip installer is used to install libraries in general.

```
pip install lib-name
```

1. Install virtual enviroment for the project

```
pip install virtualenv
```

1.a create a new virtualenv

```
virtualenv flaskenv
```

1.b load that env (You will use this env's python pip etc after loading)

```
# for git bash only
source flaskenv/Scripts/activate
```

2. Flask

```
pip install flask
```

A basic 10line website
======================
```
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello Sooraj"

@app.route("/login")
def login():
    assert False
    return "User enters login info here"

if __name__ == "__main__":
    app.run(debug=True)
```

Using request
=============

1.
```
from flask import request
```



Database - Flask-SQLAlchemy
==========================

1. Install

```
pip install flask_sqlalchemy
```

2. assign URI for the db file

```
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///datastore.db'    # /// is for relative path
```
3. Create classes for each table. example:

```
# Table-1: User table template
class User(db.Model):
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
```

3. Create a new database:
   a. open python command prompt
   b. Create empty db file. do this every time you change Model/Table. !!!Deletes all info!!!
      ```
      >>> from app import db
      >>> db.create_all()
      ```

Login Manager
=============

1. `pip install flask-login`
2. create login manager instance
```
login_manager = LoginManager()
login_manager.init_app(app)
```
3. A `UserMixin` class needs to be imported from flask_login. This is linked to our User table and it exposes
methods like `is_authentiated`, `is_ananymous` etc which are needed to handle login

This is a required code:


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

refer Flask-Login docs for more details

4. Add a decorater `@login_required` to each of theroutes that needs to be protected


Uploading files
================

1. Ref: http://code.runnable.com/UiPcaBXaxGNYAAAL/how-to-upload-a-file-to-the-server-in-flask-for-python
2. Ref for dropbox: https://github.com/playpauseandstop/Flask-Dropbox

Project GMail
==============

emailid: projectbookshelf2017@gmail.com
password: G680y7%4

Paytm/godaddy account
=============

emailid: projectbookshelf2017@gmail.com
pass: project@2017
mobile: 7904458605 
Dropbox secrets
===============

app key: d7vcyguscijcpdw
app secret: uvjjh2xkyz9qhbj

temporary access token: A5RdmUqkkXAAAAAAAAAACvYfU28rObYWB_hs60GCleXmTVjc2lYMa1JnwKvXxnWV

Github
======

1. Add the remote location to your local git management

```
git remote add origin https://github.com/projectbookshelf2017/bookshelf.git
```

2. Push local code to remote location

```
git push -u origin master
```

3. You can also pull remote changes locally using the command

```
git pull origin master
```

Heroku
======

1. Create an account
2. To understand how to host a python app (flask app) on heroku, follow this tutorial

https://devcenter.heroku.com/articles/getting-started-with-python#introduction

Changes from the above doc:
1. `heroku apps:create appname`
2. If deploy fails check if you have `Procfile` and `requirements.txt`
3. to create requirements.txt use `pip freeze > requirements.txt`
4. after freezing the requirements, add `gunicorn==19.6.0` to requirements.txt

Install PostGRES SQL on Heroku cloud
====================================

1. Goto you heroku account, click on your app (bookshelf)
2. Go to Resources, add-ons search for `Heroku Postgres`
3. Create a hobby-dev database or run `heroku addons:add heroku-postgresql:dev`
4. secure shell into heroku and create empty database using the command
    `heroku run bash`
5. open a python console there using the command
    `python`
6. init an empty database
    `from app import db`
    `db.create_all()`
7. In future if you want to reinitialize the database, you would have to drop/delete all the information in it using
    `from app import db`
    `db.drop_all()`
    # recreate the database using
    `db.create_all()`
    
Sweet Alert
===========

A nice alert box: http://t4t5.github.io/sweetalert/

Extras:
=======

If you change schema of DB, remember to delete `whoosh_index` files.

