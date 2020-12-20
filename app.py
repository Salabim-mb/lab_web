import os, re
from datetime import datetime, timedelta
from flask import Flask, render_template, send_from_directory, request, make_response, jsonify, flash, url_for, \
    redirect, g
from dotenv import load_dotenv
import uuid
from redis import StrictRedis
import json
from bcrypt import checkpw, hashpw, gensalt
from flask_hal import HAL
from flask_hal.link import Link
from flask_hal.document import Document
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


def send_allowed(methods):
    if 'OPTIONS' not in methods:
        methods.append("OPTIONS")
    response = make_response(Document().to_json(), 204)
    response.headers['Allow'] = ', '.join(methods)

    return response


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


@app.before_request
def check_auth():
    try:
        try:
            token = request.headers.get('Authorization').replace('Token ', '')
        except Exception:
            token = request.cookies['token']
        decoded = decode_jwt_token(token)
        if decoded != {}:
            g.user = decoded  # correctly read token
        else:
            g.user = {}  # token parsed, but not recognized
    except Exception as e:  # not logged in
        g.user = {}


@app.after_request
def apply_cors_enabled(response):
    response.headers['Access-Control-Allow-Origin'] = "*"
    return response


def check_username_available(login, role='user'):
    try:
        return db.hexists(f'{role}:{login}', "data") is not None
    except Exception as e:
        print(e)
        return False


def save_courier(login, email, company, phone, password):
    try:
        password = password.encode()
        hashed = hashpw(password, salt)
        db.hset(f'courier:{login}', "data", json.dumps({
            'phone': phone,
            'company': company,
            'email': email,
            'password': hashed.decode()
        }))
        return True
    except Exception as e:
        print(e)
        return False


def save_user(firstname, lastname, email, password, login, address):
    try:
        password = password.encode()
        hashed = hashpw(password, salt)
        db.hset(f'user:{login}', "data", json.dumps({
            'firstname': firstname,
            'lastname': lastname,
            'email': email,
            'password': hashed.decode(),
            'address': address
        }))
        return True
    except Exception as e:
        print(e)
        return False


def verify_user(login, password, role='user'):
    password = password.encode()
    try:
        hashed = json.loads(db.hget(f'{role}:{login}', 'data'))['password']
        if not hashed:
            return False
        return checkpw(password, hashed.encode())
    except Exception as e:
        print(e)
        return False


# API #
@app.route("/courier/parcel/<parcel_id>", methods=["PUT", "OPTIONS"])
def update_parcel_status(parcel_id):
    try:
        if g.user is not {} and g.user['role'] == 'courier':
            if request.method == 'OPTIONS':
                return send_allowed(['PUT'])
            else:
                parent_link = Link('parcel:parent', '/courier/parcels')
                data = request.get_json()
                sender_login = data['sender']
                user_entry = db.lpop(f"user:{sender_login}:parcel")
                current_parcel = user_entry[f"parcel_{parcel_id}".encode()]
                if current_parcel is not None:
                    current_parcel = current_parcel.decode()
                    current_parcel['status'] = data['status']
                    db.lpush(f"user:{sender_login}:parcel", f"parcel_{parcel_id}", json.dumps(current_parcel))
                    return make_response(Document(data={
                        'status': 'success',
                        'message': 'Parcel updated successfully'
                    }, links=parent_link).to_json(), 200)
                else:
                    return make_response(Document(data={
                        'status': 'fail',
                        'message': 'Requested package not found.'
                    }, links=parent_link).to_json(), 400)
        else:
            return make_response(Document(data={
                'status': 'fail',
                'message': 'You\'re not allowed to view this page.'
            }).to_json(), 401)
    except Exception as e:
        print(e)
        return make_response(Document(data={
            'status': 'fail',
            'message': 'You\'re not allowed to view this page.'
        }).to_json(), 401)


@app.route("/courier/register", methods=["POST", "OPTIONS"])
def register_courier():
    if request.method == 'OPTIONS':
        return send_allowed(['POST'])
    else:
        data = request.get_json()
        email = data['email']
        company = data['company']
        phone = data['phone']
        password = data['password']
        password_rep = data['password_rep']
        login = data['login']

        if None in [email, company, phone, password, login]:
            return make_response(Document(data={
               'status': 'fail',
               'message': 'Some arguments are missing :('
            }).to_json(), 400)

        if password != password_rep:
            return make_response(Document(data={
                'status': 'fail',
                'message': 'Passwords don\'t match :('
            }).to_json(), 400)

        save_courier(login, email, company, phone, password)

        correct_data = {
            'status': 'success',
            'message': 'Registered successfully, now please log in'
        }
        return make_response(Document(data=correct_data).to_json(), 201)


@app.route("/courier/login", methods=["POST", "OPTIONS"])
def login_courier():
    if request.method == 'OPTIONS':
        return send_allowed(['POST'])
    else:
        data = request.get_json()
        login = data['login']
        password = data['password']

        if None in [login, password] or "" in [login, password]:
            return make_response(Document(data={
                'status': 'fail',
                'message': 'Some arguments are missing :('
            }).to_json(), 400)

        if verify_user(login, password, 'courier'):
            res_correct = {
                'status': 'success',
                'message': 'Logged in correctly',
                'token': get_jwt_payload(login, 'courier').decode()
            }
            return make_response(Document(data=res_correct).to_json(), 200)
        else:
            return make_response(Document(data={
                'status': 'fail',
                'message': 'Invalid credentials :('
            }).to_json(), 400)


@app.route('/courier/parcels', methods=["GET", "OPTIONS"])
def get_package_list():
    try:
        if g.user is not {} and g.user['role'] == 'courier':
            if request.method == 'OPTIONS':
                return send_allowed(['GET'])
            else:
                parcel_keys = db.keys("user:*:parcel")
                decoded_parcels = []
                links = []
                for parcel_key in parcel_keys:
                    parcel_key = parcel_key.decode()
                    parcel_list = db.hgetall(parcel_key)
                    for parcel in parcel_list:
                        decoded_parcel = json.loads(parcel_list[parcel].decode("UTF-8"))
                        sender = parcel_key.replace('user:', '')  # strip beginning
                        sender = sender.replace(':parcel', '')  # strip end
                        decoded_parcel['sender'] = sender
                        decoded_parcels.append(decoded_parcel)
                        links.append(Link(f'parcel:{decoded_parcel["id"]}', f"/courier/package/{decoded_parcel['id']}"))
                return make_response(Document(data={
                    'status': 'success',
                    'parcels': decoded_parcels
                }, links=links).to_json(), 200)
        else:
            return make_response(Document(data={
                'status': 'fail',
                'message': 'You\'re not allowed to view this page.'
            }).to_json(), 401)
    except Exception as e:
        print(e)
        return make_response(Document(data={
            'status': 'fail',
            'message': 'You\'re not allowed to view this page.'
        }).to_json(), 401)


@app.route('/courier/logout', methods=["GET", "OPTIONS"])
def log_courier_out():
    if request.method == 'OPTIONS':
        return send_allowed(['GET'])
    else:
        if g.user is not {}:
            res = {
                'status': 'success',
                'message': 'Logged out successfully'
            }
        else:
            res = {
                'status': 'success?',
                'message': 'You don\'t exist already lol'
            }
        return make_response(Document(data=res).to_json(), 200)
###


@app.route('/', methods=["GET", "OPTIONS"])
def render_main():
    if request.method == "OPTIONS":
        return send_allowed(['GET'])
    else:
        return render_template("index.html", user=g.user)


@app.route('/check/<username>', methods=['GET', "OPTIONS"])
def check_available(username):
    if not check_username_available(username):
        return jsonify(available="nope")
    return jsonify(available="available")


@app.route('/sender/register', methods=['POST', "GET", "OPTIONS"])
def sign_up():
    if request.method == "OPTIONS":
        return send_allowed(['GET', 'POST'])
    elif request.method == "GET":
        return render_template("register.html", user=g.user)
    else:
        data = request.get_json()
        firstname = data.get("firstname")
        lastname = data.get("lastname")
        login = data.get("login")
        password = data.get("password")
        rep_password = data.get("rep_password")
        email = data.get("email")
        address = data.get("address")

        if None in [firstname, lastname, login, password, email, address]:
            return make_response(Document(data={
                'status': 'fail',
                "message": 'Invalid data -- some fields are empty.'
            }).to_json(), 400)

        if password != rep_password:
            return make_response(Document(data={
                'status': 'fail',
                "message": "Passwords don't match."
            }).to_json(), 400)

        if not check_username_available(login):
            return make_response(Document(data={
                'status': 'fail',
                'message': 'Login taken, silly :)'
            }).to_json(), 400)

        if save_user(firstname, lastname, email, password, login, address):
            response = make_response(Document(data={
                'status': 'success',
                'message': 'Successfully registered. Now please log in.'
            }).to_json(), 201)
        else:
            response = make_response(Document(data={
                'status': 'fail',
                'message': 'Did not register, unknown error happened o_O'
            }).to_json(), 400)

        return response


@app.route('/sender/login', methods=['POST', "GET", "OPTIONS"])
def sign_in():
    if request.method == "OPTIONS":
        return send_allowed(['GET', 'POST'])
    elif request.method == "GET":
        return render_template("login.html", user=g.user)
    else:
        data = request.get_json()
        login = data.get('login')
        password = data.get('password')
        if None in [login, password] or verify_user(login, password) is False:
            return make_response(Document(data={
                'status': 'fail',
                'message': 'Invalid credentials',
                'data': data
            }).to_json(), 400)
        encoded_jwt = get_jwt_payload(login, 'sender')
        return make_response(Document(data={
            'status': 'success',
            'message': 'Logged in sucessfully!',
            'token': encoded_jwt.decode()
        }).to_json(), 200)


@app.route('/sender/logout', methods=['GET', "OPTIONS"])
def log_out():
    if request.method == "OPTIONS":
        return send_allowed(['GET'])
    else:
        if g.user is not {}:
            res = make_response(Document(data={
                'status': 'success',
                'message': 'Logged out successfully'
            }).to_json(), 301)
            res.headers['Location'] = "/"
        else:
            res = make_response(Document(data={
                'status': 'success?',
                'message': 'You don\'t exist already lol'
            }).to_json(), 301)
            res.headers['Location'] = "/"
        return res


@app.route('/sender/dashboard', methods=["GET", "POST", "DELETE", "OPTIONS"])
def manage_parcels():
    if request.method == "OPTIONS":
        return send_allowed(['GET', 'POST', 'DELETE'])
    else:
        try:
            if g.user is not {} and g.user['role'] == 'sender':
                login = g.user['login']
                if request.method == 'DELETE':
                    parcel_id = request.headers.get("Parcel")
                    try:
                        db.hdel(f"user:{login}:parcel", f"parcel_{parcel_id}")
                        return make_response(Document(data={
                            "status": "success",
                            "message": "parcel deleted successfully"
                        }).to_json(), 200)
                    except Exception:
                        return make_response(Document(data={
                            'status': 'fail',
                            'message': "Oops, no package found!"
                        }).to_json(), 400)

                elif request.method == 'POST':
                    data = request.get_json()
                    size = data.get('size')
                    receiver = data.get('receiver')
                    custom_label = data.get('custom_label')
                    if None in [size, receiver, custom_label]:
                        return make_response(Document(data={
                            "status": "fail",
                            "message": "Missing some arguments :("
                        }).to_json(), 400)
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
                        return make_response(Document(data={
                            'status': 'fail',
                            'message': "Oops, something went really, really wrong."
                        }).to_json(), 500)

                else:
                    try:
                        user_parcels = db.hgetall(f"user:{login}:parcel")
                        decoded_parcels = []
                        for parcel in user_parcels:
                            decoded_parcels.append(json.loads(user_parcels[parcel].decode("UTF-8")))
                        return render_template("dashboard.html", parcels=decoded_parcels, user=g.user)
                    except Exception:
                        return make_response(Document(data={
                            "status": "fail",
                            "message": "Oops, did not find page 'Dashboard' :O"
                        }).to_json(), 500)
            else:
                flash("You have no access to this site")
                return redirect("/")
        except Exception as e:
            print(e)
            flash("You have no access to this site")
            return redirect("/")


@app.route('/favicon.ico')  # dummy route only to get render favicon -- no options method here (not sure if correct tho)
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':

    app.debug = True
    app.run(ssl_context='adhoc', host="0.0.0.0", port=5000)
