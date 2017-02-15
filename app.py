from flask import Flask, render_template

app = Flask(__name__)
app.config['STATIC_FOLDER'] = 'static'

@app.route("/")
def home():
    return render_template("home1.html")

@app.route("/profile")
def profile():
    return render_template("userpro.html")

if __name__ == "__main__":
    app.run(debug=True)