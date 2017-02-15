from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.config['STATIC_FOLDER'] = 'static'

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":    # any POST call will be handled by request object
        form = request.form
        email = form["email"]
        password = form["psw"]
        # check if email and corresponding password exists in the database
        # If yes
        return redirect("/profile")
    return render_template("home1.html")

@app.route("/profile")
def profile():
    return render_template("userpro.html")

@app.route("/signup")
def signup():
    if request.method == "POST":
        form = request.form
        name = form["name"]
        department = form["dpt"]
        email = form["email"]
        password = form["pwd1"]
        conpassword = form["pwd2"]

    return render_template("signup.html")

if __name__ == "__main__":
    app.run(debug=True)