import os

from flask import Flask, render_template, send_from_directory

app = Flask(__name__, static_url_path="/static")


@app.route('/')
def render_main():
    return render_template("index.html")


@app.route('/sender/register')
def render_sign_up():
    return render_template("register.html")


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run()
