import datetime
from dateutil import parser
import influxdb
import pytz


DEFAULT_NUM_INTERVALS = 10  # default number of intervals when returning an aggregated query
DEFAULT_QUERY_DAY_SPAN = 10  # default time interval length for query/aggregated query
DEFAULT_PER_PAGE = 25

# TODO: this could be omitted if we encoded query as JSON in the GET parameters
QUERY_KEYWORDS = ['num_intervals', 'page', 'per_page', 'time__lte', 'time__gte']


class InfluxDBStorage:
    @staticmethod
    def get_client(host='influxdb',
                   port=8086,
                   user='root',
                   password='root',
                   dbname='logsink'):
        client = influxdb.InfluxDBClient(
            host,
            port,
            user,
            password,
            dbname
        )
        databases = client.get_list_database()
        if dbname not in (db['name'] for db in databases):
            client.create_database(dbname)

        return client

    def __init__(self, test_mode=False):
        self.test_mode = test_mode
        if test_mode:
            self.client = self.get_client(dbname='logsink-test')
        else:
            self.client = self.get_client()

    def insert(self, message, **kwargs):
        if set(QUERY_KEYWORDS).intersection(kwargs):
            raise ValueError(
                "%s are keywords reserved for querying, you cannot use them as tags." % ', '.join(QUERY_KEYWORDS)
            )

        time = kwargs.pop('time', _utcnow().isoformat())

        self.client.write_points([
            {
                'measurement': 'logs',
                'tags': kwargs,
                'time': time,
                'fields': {
                    'message': message,
                },
            },
        ])

    def query(self, **kwargs):
        where = _where_filter(**kwargs)
        limit = _limit(**kwargs)

        return self.client.query(
            'SELECT * FROM logs WHERE %s %s;' % (where, limit)
        ).get_points()

    def aggregated(self, **kwargs):
        num_intervals = kwargs.pop('num_intervals', DEFAULT_NUM_INTERVALS)

        time__lte, time__gte = _time_range(**kwargs)
        span = (time__gte - time__lte).total_seconds()
        diff = int(span/num_intervals)

        where = _where_filter(**kwargs)

        return self.client.query(
            'SELECT COUNT(*) FROM logs WHERE %s GROUP BY time(%ss);' % (where, diff)
        ).get_points()

    def clear(self, **kwargs):
        if 'time__lte' not in kwargs and 'time__gte' not in kwargs:
            # Clear all time intervals (don't apply the DEFAULT_QUERY_DAY_SPAN)
            where = _where_tag_filter(**kwargs)
        else:
            where = _where_filter(**kwargs)

        # where can be empty
        if where:
            where = ' WHERE %s' % where

        return self.client.query(
            'DELETE FROM logs %s;' % where
        )


# Utility functions
def _utcnow():
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


def _time_range(**kwargs):
    # By default, show last 10 days of data
    time__lte = _utcnow()
    if 'time__lte' in kwargs:
        time__lte = parser.parse(kwargs['time__lte'])
    if 'time__gte' in kwargs:
        time__gte = parser.parse(kwargs['time__gte'])
    else:
        time__gte = time__lte - datetime.timedelta(days=DEFAULT_QUERY_DAY_SPAN)
    if time__lte < time__gte:
        raise ValueError('Invalid time range.')

    return time__gte, time__lte


# InfluxDB-specific
def _where_filter(**kwargs):
    time__gte, time__lte = _time_range(**kwargs)

    query = [
        "time >= '%s'" % time__gte.isoformat(timespec='seconds'),
        "time <= '%s'" % time__lte.isoformat(timespec='seconds'),
    ]

    if 'message' in kwargs:
        # Message regex filtering
        message = kwargs['message']
        query.append(
            '"message" =~ /%s/' % message
        )

    tag_filter = _where_tag_filter(**kwargs)
    if tag_filter:
        query.append(tag_filter)

    return ' AND '.join(query)


def _where_tag_filter(**kwargs):
    # TODO: this is very simple with no SQL-injection protection whatsoever

    query = []

    # Other tags are filtered by exact value
    for tag, value in kwargs.items():
        if tag in QUERY_KEYWORDS or tag == 'message':
            continue

        query.append(
            '"%s" = \'%s\'' % (tag, value),
        )

    return ' AND '.join(query)


def _limit(**kwargs):
    page = int(kwargs.get('page', 1))
    per_page = int(kwargs.get('per_page', DEFAULT_PER_PAGE))
    offset = (page - 1)*per_page

    return 'LIMIT %d OFFSET %d' % (per_page, offset)
