import datetime
from dateutil import parser
import influxdb
import pytz


def utcnow():
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


def get_client():
    client = influxdb.InfluxDBClient(
        'influxdb',
        8086,
        'root',
        'root',
        'logsink'
    )
    client.create_database('logsink')

    return client


def insert(message, **kwargs):
    client = get_client()

    client.write_points([
        {
            'measurement': 'logs',
            'tags': kwargs,
            'time': utcnow().isoformat(),
            'fields': {
                'message': message,
            },
        },
    ])


def query(**kwargs):
    # By default, show last 10 days of data
    time__gte = utcnow() - datetime.timedelta(days=10)
    time__lte = utcnow()
    if time__gte in kwargs:
        time__gte = parser.parse(kwargs.pop('time__gte'))
    if time__lte in kwargs:
        time__lte = parser.parse(kwargs.pop('time__lte'))
    if time__lte < time__gte:
        raise ValueError('Invalid time range.')

    query = [
        "time >= '%s'" % time__gte.isoformat(timespec='seconds'),
        "time <= '%s'" % time__lte.isoformat(timespec='seconds'),
    ]

    if 'message' in kwargs:
        # Message regex filtering
        message = kwargs.pop('message')
        query.append(
            '"message" =~ /%s/' % message
        )

    # Other tags are filtered by exact value
    for tag, value in kwargs.items():
        query.append(
            '"%s" = "%s"' % (tag, value),
        )

    client = get_client()

    query = ' AND '.join(query)

    return client.query('SELECT * FROM logs WHERE %s;' % query)

