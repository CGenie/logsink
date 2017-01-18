import flask
from flask_cors import CORS
from flask_restful import Resource, reqparse  # Api is from swagger
from flask_restful_swagger_2 import Api, swagger, Schema
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
api = Api(
    app,
    api_version='1.0',
    api_spec_url='/api/swagger',
    security_definitions={
        'auth-token': {
            'type': 'apiKey',
            'name': 'X-Auth-Token',
            'in': 'header',
        },
    }
)


log_parser = reqparse.RequestParser()
log_parser.add_argument('message', required=True)
log_parser.add_argument('tags', type=dict, required=True)


class LogMessageModel(Schema):
    type = 'object'
    properties = {
        'message': {
            'type': 'string',
            'description': 'Message of the log.',
        },
        'tags': {
            'type': 'object',
            'description': 'Any additional tags for the log.',
        },
    }
    required = ['message', 'tags']


class Logs(Resource):
    @swagger.doc({
        'tags': ['logs'],
        'description': 'Queries the logs database',
        'parameters': [
            {
                'name': 'message',
                'description': 'Query part of the message. Will to a regex search.',
                'in': 'path',
                'type': 'string',
            },
            {
                'name': 'time__gte',
                'description': 'Timestamp must be greater than this value. By default this is now() - 10 days. String isoformat representation of datetime.',
                'in': 'path',
                'type': 'string',
            },
            {
                'name': 'time__lte',
                'description': 'Timestamp must be less than this value. By default this is now(). String isoformat representation of datetime.',
                'in': 'path',
                'type': 'string',
            },
            {
                'name': 'page',
                'description': 'Page number.',
                'in': 'path',
                'type': 'integer',
            },
            {
                'name': 'per_page',
                'description': 'Items per page.',
                'in': 'path',
                'type': 'integer',
            },
        ],
        'security': {
            'auth-token': [],
        },
        'responses': {
            '200': {
                'description': 'Query',
            },
        },
    })
    @token_required
    def get(self):
        # Force convert to dict
        args = {arg: value for arg, value in flask.request.args.items()}

        return [
            row for row in storage.query(**args)
        ]

    @swagger.doc({
        'tags': ['logs'],
        'description': 'Store log data.',
        'parameters': [
            {
                'name': 'body',
                'description': 'The log message you want to store',
                'in': 'body',
                'schema': LogMessageModel,
                'required': True,
            },
        ],
        'security': {
            'auth-token': [],
        },
        'responses': {
            '201': {
                'description': 'Log Message',
                'schema': LogMessageModel,
                'examples': {
                    'application/json': {
                        'message': 'test message',
                        'tags': {
                            'tag1': 'value1',
                            'tag2': 'value2',
                        },
                    },
                },
            },
        },
    })
    @token_required
    def post(self):
        log = log_parser.parse_args()
        app.logger.debug('Log: %r', log)

        storage.insert(log['message'], **log['tags'])

        return log, 201


class AggregatedLogs(Resource):
    @swagger.doc({
        'tags': ['logs'],
        'description': 'Returns an aggregated query of logs in database. This is suitable if you want to represent histogram data.',
        'parameters': [
            {
                'name': 'message',
                'description': 'Query part of the message',
                'in': 'path',
                'type': 'string',
            },
            {
                'name': 'time__gte',
                'description': 'Timestamp must be greater than this value. By default this is now() - 10 days. String isoformat representation of datetime.',
                'in': 'path',
                'type': 'string',
                'format': 'date-time',
            },
            {
                'name': 'time__lte',
                'description': 'Timestamp must be less than this value. By default this is now(). String isoformat representation of datetime.',
                'in': 'path',
                'type': 'string',
                'format': 'date-time',
            },
        ],
        'security': {
            'auth-token': [],
        },
        'responses': {
            '200': {
                'description': 'Aggregated Query',
            },
        },
    })
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
