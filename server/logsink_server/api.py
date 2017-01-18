import flask
from flask_cors import CORS
from flask_restful import Resource, reqparse  # Api is from swagger
from flask_restful_swagger_2 import Api, swagger
from functools import wraps
import os

from logsink_server import storage


root_token = os.environ['ROOT_TOKEN']


def token_required(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        token = flask.request.headers.get('X-Auth-Token')
        # TODO: Simple authentication -- only 1 predefined token
        if token != root_token:
            return {'error': 'Token incorrect'}, 403

        return method(*args, **kwargs)
    return wrapper


app = flask.Flask(__name__)
CORS(app)
api = Api(app, api_version='1.0', api_spec_url='/api/swagger')


log_parser = reqparse.RequestParser()
log_parser.add_argument('message', required=True)
log_parser.add_argument('tags', type=dict, required=True)


class Logs(Resource):
    @swagger.doc({
        'tags': ['logs'],
        'description': 'Queries the logs database',
        'parameters': [
            {
                'name': 'message',
                'description': 'Query part of the message',
                'in': 'path',
                'type': 'string',
            }
        ],
        'responses': {
            '200': {
                'description': 'Query',
            },
        },
    })
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

        storage.insert(log['message'], **log['tags'])

        return log, 201


class AggregatedLogs(Resource):
    @token_required
    def get(self):
        return [
            row for row in storage.aggregated(
                # Force convert to dict
                **{arg: value for arg, value in flask.request.args.items()}
            )
        ]


api.add_resource(Logs, '/logs')
api.add_resource(AggregatedLogs, '/logs/aggregated')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6789, debug=True)
