import datetime
import influxdb


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
            'time': datetime.datetime.now().isoformat(),
            'fields': {
                'message': message,
            },
        },
    ])


def query(**kwargs):
    client = get_client()

    return client.query('SELECT * FROM logs;')

