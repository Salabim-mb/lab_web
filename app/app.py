from flask import Flask, render_template
import os

TEMPLATE_DIR = os.path.relpath("templates/", ".")
STATIC_DIR = os.path.abspath("/static")

app = Flask(__name__, static_url_path="/static")


@app.route('/')
def render_main():
    return render_template("index.html")


@app.route('/sender/register')
def render_sign_up():
    return render_template("register.html")


if __name__ == '__main__':
    app.run()
