import json
from src.utils import get_app_version, get_uptime
from src.redis_client import redis
from __main__ import app


@app.route('/health-check', methods=['GET'])
def check():
    try:
        redis_keys = [x.decode('utf-8') for x in redis().keys('*')]
        data = {
            "status": 200,
            "version": get_app_version(),
            "uptime": get_uptime(),
            "redis_keys": redis_keys
        }

        response = app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
        return response
    except Exception as e:
        response = app.response_class(
            response="Exception: {}".format(type(e).__name__),
            status=500,
            mimetype='application/json'
        )
        return response