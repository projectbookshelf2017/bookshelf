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

How to serve static files?
==========================

1. import `send_from_directory` from flask

```
from flask import send_from_directory
```