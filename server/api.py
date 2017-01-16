import flask
from flask_restful import Resource, Api, reqparse
from functools import wraps
import os

from . import storage


root_token = os.environ['ROOT_TOKEN']


def token_required(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        token = flask.request.headers.get('X-Auth-Token')
        # Simple authentication
        if token != root_token:
            return {'error': 'Token incorrect'}, 403

        return method(*args, **kwargs)
    return wrapper


app = flask.Flask(__name__)
api = Api(app)


log_parser = reqparse.RequestParser()
log_parser.add_argument('message', required=True)
log_parser.add_argument('params', type=dict, required=True)


class Logs(Resource):
    @token_required
    def get(self):
        return [
            row for row in storage.query(
                # Force convert to dict
                **{arg: value for arg, value in flask.request.args.items()}
            )
        ]

    @token_required
    def post(self):
        log = log_parser.parse_args()
        app.logger.debug('Log: %r', log)

        storage.insert(log['message'], **log['params'])

        return log, 201


api.add_resource(Logs, '/logs')


if __name__ == '__main__':
    app.run()
