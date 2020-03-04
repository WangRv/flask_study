from flask import (
    Flask,
    redirect,
    url_for,
    session,
    request)

app = Flask(__name__)

app.secret_key = "haha"


@app.route('/')  # index html
def hello_world():
    print(session)
    return 'Hello World!'


@app.route("/back/<int:year>")
def back(year):
    return f"This is your {year}"


@app.route("/test")
def test():
    return redirect(url_for("hello_world"))


@app.route("/login")
def login():
    session["logged_in"] = True
    return redirect(url_for("hello_world"))


# start run flask subject
if __name__ == '__main__':
    app.run(debug=True)
