import os
from datetime import datetime, timedelta
from flask import Flask, render_template, send_from_directory, session, request, make_response, jsonify, flash, url_for, \
    redirect, g
from dotenv import load_dotenv
import uuid
from flask_session import Session
from redis import StrictRedis
import json
from bcrypt import checkpw, hashpw, gensalt
from flask_hal import HAL, document
from flask_hal.link import Link
from flask_hal.document import Document, Embedded
from flask_cors import CORS
import jwt


load_dotenv()
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PASS = os.getenv("REDIS_PASS")
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_EXP_TIME = os.getenv("JWT_EXP_TIME")
db = StrictRedis(REDIS_HOST, db=21, password=REDIS_PASS)

SESSION_COOKIE_SECURE = True
SESSION_TYPE = "redis"
SESSION_REDIS = db
app = Flask(__name__, static_url_path="/static")
app.config.from_object(__name__)
app.secret_key = os.getenv("SECRET_KEY")
# sess = Session(app)
salt = gensalt(12)
HAL(app)

# url_whitelist = ['https://parcelexpress.herokuapp.com', 'http://localhost:3000', 'https://localhost:5000']


def get_jwt_payload(login, role):
    try:
        return jwt.encode({
            'login': login,
            'last_login': datetime.now().isoformat(),
            'role': role,
            'exp': int( (datetime.now() + timedelta(seconds=int(JWT_EXP_TIME))).timestamp() )
        }, JWT_SECRET, algorithm='HS256')
    except Exception as e:
        print(e)
        return e


def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algoritm='HS256')
        return payload
    except Exception as e:
        print(f'Something went wrong. Error: {e}')
        return {}


def check_auth(current_request):
    try:
        token = current_request.headers.get('Authorization').replace('Token ', '')
    except Exception:
        token = current_request.cookies['token']
    decoded = decode_jwt_token(token)
    if decoded != {}:
        return decoded
    else:
        return {}


def check_username_available(login):
    try:
        return db.hexists(f'user:{login}', "data") is not None
    except Exception as e:
        print(e)
        return False


def save_user(firstname, lastname, email, password, login, address):
    try:
        password = password.encode()
        print(password)
        hashed = hashpw(password, salt)
        db.hset(f'user:{login}', "data", json.dumps({
            'firstname': firstname,
            'lastname': lastname,
            'email': email,
            'password': hashed.decode(),
            'address': address
        }))
        print('registered')
        return True
    except Exception as e:
        print(e)
        return False


def verify_user(login, password):
    password = password.encode()
    try:
        hashed = json.loads(db.hget(f'user:{login}', 'data'))['password']
        if not hashed:
            return False
        return checkpw(password, hashed.encode())
    except Exception as e:
        print(e)
        return False


# API #
@app.route('/courier/packages')
def get_package_list():
    if g.user is None:
        print("cześć")
###


@app.route('/')
def render_main():
    return render_template("index.html")


@app.route('/sender/register', methods=['GET'])
def render_sign_up():
    return render_template("register.html")


@app.route('/sender/login', methods=['GET'])
def render_sign_in():
    return render_template("login.html")


@app.route('/check/<username>', methods=['GET'])
def check_available(username):
    if not check_username_available(username):
        return jsonify(available="nope")
    return jsonify(available="available")


@app.route('/sender/register', methods=['POST'])
def sign_up():
    data = request.get_json()
    firstname = data.get("firstname")
    lastname = data.get("lastname")
    login = data.get("login")
    password = data.get("password")
    rep_password = data.get("rep_password")
    email = data.get("email")
    address = data.get("address")

    if None in [firstname, lastname, login, password, email, address]:
        return make_response(jsonify({
            'status': 'fail',
            "message": 'Invalid data -- some fields are empty.'
        }), 400)

    if password != rep_password:
        return make_response(jsonify({
            'status': 'fail',
            "message": "Passwords don't match."
        }), 400)

    if not check_username_available(login):
        return make_response(jsonify({
            'status': 'fail',
            'message': 'Login taken, silly :)'
        }), 400)

    if save_user(firstname, lastname, email, password, login, address):
        response = make_response(jsonify({
            'status': 'success',
            'message': 'Successfully registered. Now please log in.'
        }), 201)
    else:
        response = make_response(jsonify({
            'status': 'fail',
            'message': 'Did not register, unknown error happened o_O'
        }), 400)

    return response


@app.route('/sender/login', methods=['POST'])
def sign_in():
    data = request.get_json()
    login = data.get('login')
    password = data.get('password')
    if None in [login, password] or verify_user(login, password) is False:
        return make_response(jsonify({
            'status': 'fail',
            'message': 'Invalid credentials',
            'data': data
        }), 400)
    encoded_jwt = get_jwt_payload(login, 'sender')
    return make_response(jsonify({
        'status': 'success',
        'message': 'Logged in sucessfully!',
        'token': encoded_jwt.decode()
    }), 200)


@app.route('/sender/logout', methods=['GET'])
def log_out():
    g.user = check_auth(request)
    if g.user is not {}:
        res = make_response(jsonify({
            'status': 'success',
            'message': 'Logged out successfully'
        }), 301)
        res.headers['Location'] = "/"
    else:
        res = make_response(jsonify({
            'status': 'success?',
            'message': 'You don\'t exist already lol'
        }), 301)
        res.headers['Location'] = "/"
    return res


@app.route('/sender/dashboard', methods=["GET", "POST", "DELETE"])
def manage_parcels():
    g.user = check_auth(request)
    if g.user is not {}:
        login = g.user['login']
        if request.method == 'DELETE':
            parcel_id = request.headers.get("Parcel")
            try:
                db.hdel(f"user:{login}:parcel", f"parcel_{parcel_id}")
                return make_response(jsonify({
                    "status": "success",
                    "message": "parcel deleted successfully"
                }), 200)
            except Exception:
                return make_response("Oops, no package found!", 400)

        elif request.method == 'POST':
            data = request.get_json()
            size = data.get('size')
            receiver = data.get('receiver')
            custom_label = data.get('custom_label')
            if None in [size, receiver, custom_label]:
                return make_response(jsonify({
                    "status": "fail",
                    "message": "Missing some arguments :("
                }), 400)
            parcel_id = uuid.uuid4()
            parcel = {
                "size": size,
                "receiver": receiver,
                "custom_label": custom_label,
                "id": str(parcel_id),
                "status": "Not assigned"
            }
            try:
                db.hset(f"user:{login}:parcel", f"parcel_{parcel_id}", json.dumps(parcel))
                res = make_response("", 301)
                res.headers['Location'] = "/sender/dashboard"
                return res
            except Exception:
                return make_response("Oops, something went really, really wrong.", 500)

        else:
            try:
                user_parcels = db.hgetall(f"user:{login}:parcel")
                decoded_parcels = []
                for parcel in user_parcels:
                    decoded_parcels.append(json.loads(user_parcels[parcel].decode("UTF-8")))
                return render_template("dashboard.html", parcels=decoded_parcels)
            except Exception:
                return make_response(jsonify({
                    "status": "fail",
                    "message": "Oops, did not find page 'Dashboard' :O"
                }), 500)
    else:
        flash("You have no access to this site")
        return redirect("/")


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':

    app.debug = True
    app.run(ssl_context='adhoc', host="0.0.0.0", port=5000)
