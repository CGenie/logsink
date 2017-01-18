import os
import unittest
import time

import logsink


TEST_TOKEN = os.environ['TEST_TOKEN']


class TestServer(unittest.TestCase):
    def setUp(self):
        self.client_name = 'test-client'
        self.client = logsink.Client(self.client_name, token=TEST_TOKEN)

    def tearDown(self):
        self.client.clear()

    def _test_insert(self):
        # Empty DB at the beginning
        query_r = self.client.query()
        self.assertEqual(len(query_r), 0)

        message = 'test message'
        log_r = self.client.log(message)
        self.assertEqual(log_r.status_code, 201)

        # NOTE: There is a lag between insert and query -- the underlying
        # database isn't transactional.
        # We can avoid sleeps in code if we keep querying the API
        # continuously until some timeout is reached.
        time.sleep(1)

        query_r = self.client.query()
        self.assertEqual(len(query_r), 1)
        self.assertEqual(query_r[0]['client_name'], self.client_name)
        self.assertEqual(query_r[0]['message'], message)

        message2 = 'test message 2'
        log_r = self.client.log(message2)
        self.assertEqual(log_r.status_code, 201)
        time.sleep(1)
        query_r = self.client.query()
        self.assertEqual(len(query_r), 2)
        self.assertEqual(query_r[1]['message'], message2)

    def test_filtering(self):
        message = 'test message'
        value1 = 'value1'
        value2 = 'value2'
        log_r = self.client.log(message, tag1=value1, tag2=value2)
        self.assertEqual(log_r.status_code, 201)

        # Another log message which doesn't match the previous one exactly
        log_r = self.client.log(message, tag1=value1, tag2='non-value2')
        self.assertEqual(log_r.status_code, 201)

        time.sleep(1)

        query_r = self.client.query(tag1=value1)
        self.assertEqual(len(query_r), 2)

        query_r = self.client.query(tag1=value1, tag2=value2)
        self.assertEqual(len(query_r), 1)

    def test_aggregation(self):
        log_r = self.client.log('test message', time='2017-01-01T01:00:00Z')
        self.assertEqual(log_r.status_code, 201)

        log_r = self.client.log('test message', time='2017-01-02T01:00:00Z')
        self.assertEqual(log_r.status_code, 201)

        log_r = self.client.log('test message', time='2017-01-02T02:00:00Z')
        self.assertEqual(log_r.status_code, 201)

        time.sleep(2)

        query_r = self.client.agg_query(
            time__gte='2017-01-01T00:00:00Z',
            time__lte='2017-01-10T00:00:00Z'
        )
        self.assertEqual(len(query_r), 11)

        self.assertEqual(
            sum(agg['count_message'] for agg in query_r),
            3
        )
        self.assertEqual(
            query_r[0]['count_message'],
            1
        )
        self.assertEqual(
            query_r[1]['count_message'],
            2
        )
