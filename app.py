import os
from datetime import datetime
from flask import Flask, render_template, send_from_directory, session, request, make_response, jsonify
from dotenv import load_dotenv
from flask_session import Session
from redis import StrictRedis
from bcrypt import checkpw, hashpw, gensalt

load_dotenv()
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PASS = os.getenv("REDIS_PASS")
db = StrictRedis(REDIS_HOST, db=21, password=REDIS_PASS)

SESSION_TYPE = "redis"
SESSION_REDIS = db
app = Flask(__name__, static_url_path="/static")
app.config.from_object(__name__)
app.secret_key = os.getenv("SECRET_KEY")
sess = Session(app)
salt = gensalt(12)


def check_username_available(login):
    return db.hexists(f'user:{login}', "email") is not None


def save_user(firstname, lastname, email, password, login, address):
    try:
        password = password.encode()
        hashed = hashpw(password, salt)
        db.hset(f'user:{login}', "password", hashed)
        db.hset(f'user:{login}', "email", email)
        db.hset(f'user:{login}', "firstname", firstname)
        db.hset(f'user:{login}', "lastname", lastname)
        db.hset(f'user:{login}', "address", address)
        return True
    except Exception:
        return False


def verify_user(login, password):
    password = password.encode()
    hashed = db.hget(f'user:{login}', 'password')
    if not hashed:
        print(f'Account for {login} does not exist')
        return False
    return checkpw(password, hashed)


# FRONTEND
@app.route('/')
def render_main():
    print(session)
    return render_template("index.html")


@app.route('/sender/register', methods=['GET'])
def render_sign_up():
    return render_template("register.html")


@app.route('/sender/login', methods=['GET'])
def render_sign_in():
    return render_template("login.html")


@app.route('/sender/dashboard', methods=['GET'])
def render_dashboard():
    return render_template("dashboard.html")


# BACKEND
@app.route('/check/<username>', methods=['GET'])
def check_available(username):
    if not check_username_available(username):
        return jsonify(available="nope")
    return jsonify(available="available")


@app.route('/sender/register', methods=['POST'])
def sign_up():
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    login = request.form.get("login")
    password = request.form.get("password")
    rep_password = request.form.get("rep_password")
    email = request.form.get("email")
    address = request.form.get("address")

    if None in [firstname, lastname, login, password, email, address]:
        return make_response('Invalid data -- some fields are empty.', 400)

    if password != rep_password:
        return make_response("Passwords don't match", 400)

    if not check_username_available(login):
        return make_response("Login taken, dummy :)", 400)

    save_user(firstname, lastname, email, password, login, address)

    response = make_response("", 301)
    response.headers["Location"] = "/sender/login"
    return response


@app.route('/sender/login', methods=['POST'])
def sign_in():
    login = request.form.get('login')
    password = request.form.get('password')
    if None in [login, password] or verify_user(login, password) is False:
        return make_response('Invalid credentials', 400)
    session["login"] = login
    session["last_login"] = datetime.now()
    print(session)
    res = make_response("", 301)
    res.headers['Location'] = "/sender/dashboard"
    return res


@app.route('/sender/logout')
def log_out():
    session.clear()
    print(session)
    res = make_response("", 301)
    res.headers['Location'] = "/"
    return res


@app.route('/sender/dashboard/<username>', methods=["GET"])
def get_parcels(username):
    user_parcels = db.hgetall(f"user:{username}", "parcel")
    return jsonify(parcels=user_parcels)


#@app.route('/sender/dashoard/<username>', methods=["POST"])


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':

    app.debug = True
    app.run()
