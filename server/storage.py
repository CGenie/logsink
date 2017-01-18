import datetime
from dateutil import parser
import influxdb
import pytz


DEFAULT_NUM_INTERVALS = 10  # default number of intervals when returning an aggregated query
DEFAULT_QUERY_DAY_SPAN = 10  # default time interval length for query/aggregated query


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
    client.create_database(dbname)

    return client


def insert(message, **kwargs):
    client = get_client()

    client.write_points([
        {
            'measurement': 'logs',
            'tags': kwargs,
            'time': _utcnow().isoformat(),
            'fields': {
                'message': message,
            },
        },
    ])


def query(**kwargs):
    where = _where_filter(**kwargs)

    client = get_client()

    return client.query('SELECT * FROM logs WHERE %s;' % where)


def aggregated(**kwargs):
    num_intervals = kwargs.pop('num_intervals', DEFAULT_NUM_INTERVALS)

    time__lte, time__gte = _time_range(**kwargs)
    span = (time__gte - time__lte).total_seconds()
    diff = int(span/num_intervals)

    where = _where_filter(**kwargs)

    client = get_client()

    return client.query('SELECT COUNT(*) FROM logs WHERE %s GROUP BY time(%ss);' % (where, diff))


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

    # Other tags are filtered by exact value
    for tag, value in kwargs.items():
        if tag in ['message', 'time__lte', 'time__gte']:
            continue

        query.append(
            '"%s" = "%s"' % (tag, value),
        )

    return ' AND '.join(query)
