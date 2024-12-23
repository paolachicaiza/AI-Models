import os
from functools import wraps
from flask import request, make_response

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get('Authorization') != f"Bearer {os.environ['AUTH_TOKEN']}":
          return make_response('Forbidden', 403)
        return f(*args, **kwargs)
    return decorated_function
