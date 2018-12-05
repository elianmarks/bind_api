# -*- coding: utf-8 -*-
#Elliann Marks
#elian.markes@gmail.com
#

#Bibliotecas
import types
import users
from flask import Flask, request, jsonify
from functools import wraps
from cli.config import APP_DEBUG
from cli.moduleLog import logError

app = Flask(__name__)
app.debug = APP_DEBUG
users.connect()

def resp_success_info(data):
    message = {
        'ok': data[1],
        'data': data[0],
        'available': data[2],
    }
    return jsonify(message)

def resp_success(data):
    message = {
        'ok': data[1],
        'data': data[0],
    }
    return jsonify(message)

def resp_error(code, error, headers=None):
    message = {
        'ok': False,
        'data': error
    }
    resp = jsonify(message)
    resp.status_code = code
    if headers:
        for k, v in headers.items():
            resp.headers[k] = v
    return resp

def run_and_response(func, args):
    try:
        return resp_success(func(*args))
    except Exception as e:
        return resp_error(200, str(e).strip())

def run_and_response_info(func, args):
    try:
        return resp_success_info(func(*args))
    except Exception as e:
        return resp_error(200, str(e).strip())

def get_post_data(key, default_value=None):
    if key in request.form:
        val = request.form[key]
    else:
        val = default_value
    return val

@app.errorhandler(404)
def not_found(error):
    return resp_error(404, str(error))

@app.errorhandler(403)
def forbidden(error):
    return resp_error(403, str(error))

@app.errorhandler(405)
def notsupported(error):
    return resp_error(405, str(error))

def authenticate_error():
    """Sends a 401 response that enables basic auth"""
    return resp_error(
        401,
        'Forbidden',
        headers={'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(groups=[]):
    def requires_auth_decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth = request.authorization
            if not auth or not users.authenticate(auth.username, auth.password, groups):
                return authenticate_error()
            return f(*args, **kwargs)
        return decorated
    return requires_auth_decorator

def getUser():
    return str(request.authorization.username)
    