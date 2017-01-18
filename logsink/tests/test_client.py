import os
import unittest
import unittest.mock as mock


import logsink


TEST_TOKEN = os.environ['TEST_TOKEN']


class TestClient(unittest.TestCase):
    def setUp(self):
        self.client = logsink.Client('test-client', token=TEST_TOKEN)

    @mock.patch('requests.post')
    def test_log_request(self, requests_post):
        message = 'test message'
        self.client.log(
            message,
            tag1='value1',
            tag2='value2'
        )
        self.assertTrue(requests_post.called)
        call = requests_post.mock_calls[0]
        args = call[1]
        kwargs = call[2]
        url = args[0]
        params = kwargs.get('json')
        headers = kwargs.get('headers')
        self.assertTrue(url.endswith('/logs'))
        self.assertIsNotNone(params)
        self.assertIsNotNone(headers)
        self.assertEqual(params.get('message'), message)
        self.assertEqual(
            params.get('tags'),
            {
                'client_name': self.client.client_name,
                'tag1': 'value1',
                'tag2': 'value2',
            }
        )
        self.assertEqual(headers.get('Content-Type'), 'application/json')
        self.assertEqual(headers.get('X-Auth-Token'), TEST_TOKEN)

    @mock.patch('requests.get')
    def test_log_request(self, requests_get):
        self.client.query(message='test message', tag1='value1')
        self.assertTrue(requests_get.called)
        call = requests_get.mock_calls[0]
        args = call[1]
        kwargs = call[2]
        url = args[0]
        params = kwargs.get('params')
        self.assertIsNotNone(params)
        self.assertEqual(params.get('message'), 'test message')
        self.assertEqual(params.get('tag1'), 'value1')
