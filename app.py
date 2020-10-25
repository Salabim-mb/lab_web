from flask import Flask, render_template
import os

TEMPLATE_DIR = os.path.abspath("./templates")
STATIC_DIR = os.path.abspath("./static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)


@app.route('/')
def render_main():
    return render_template("index.html")


@app.route('/sender/register')
def render_sign_up():
    return render_template("register.html")


if __name__ == '__main__':
    app.run()
