import requests


class Client:
    def __init__(
            self,
            client_name,
            host='localhost',
            port=6789,
            token=None,
            protocol='http'):
        self.client_name = client_name
        self.protocol = protocol
        self.host = host
        self.port = port
        self.token = token

    @property
    def url(self):
        return '%s://%s:%s' % (self.protocol, self.host, self.port)

    @property
    def headers(self):
        return {
            'Content-Type': 'application/json',
            'X-Auth-Token': self.token,
        }

    def log(self, message, **kwargs):
        data = {
            'message': message,
            'tags': {
                'client_name': self.client_name,
            },
        }
        data['tags'].update(kwargs)

        return requests.post(
            '%s/logs' % self.url,
            json=data,
            headers=self.headers
        )

    def query(self, **params):
        return requests.get(
            '%s/logs' % self.url,
            params=params,
            headers=self.headers
        ).json()

    def clear(self, **params):
        return requests.delete(
            '%s/logs' % self.url,
            params=params,
            headers=self.headers
        )

    def agg_query(self, **params):
        return requests.get(
            '%s/logs/aggregated' % self.url,
            params=params,
            headers=self.headers
        ).json()
