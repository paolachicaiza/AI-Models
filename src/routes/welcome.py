
from __main__ import app
from flask import render_template

@app.route("/")
def welcome():
    return render_template("welcome.html")