# Simple authentication module
import os


ROOT_TOKEN = os.environ['ROOT_TOKEN']
TEST_TOKEN = os.environ['TEST_TOKEN']  # A token for testing the API from external calls


# This is our auth database -- to each token we map an InfluxDB
# This way we can differentiate between two simple cases -- production and test env
# For a more robust use case, we could add users along with their tokens
# and respective databases in InfluxDB but the core would remain more or less the same
# (with something like Redis as token backend)
TOKEN_DBS = {
    ROOT_TOKEN: 'logsink',
    TEST_TOKEN: 'logsink-test',
}


def get_token(request):
    return request.headers.get('X-Auth-Token')


def is_authenticated(request):
    token = get_token(request)
    return token in TOKEN_DBS


def token_dbname(request):
    token = get_token(request)
    return TOKEN_DBS[token]
