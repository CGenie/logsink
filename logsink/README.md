# Logsink client library
This is a library for easy interaction with the Log sink server.

## Installation
```bash
python setup.py install
```

## Testing
Install [tox](https://tox.readthedocs.io/en/latest/). Then run

```bash
tox
```

## Usage
Initialize the client with server address data:

```python
import logsink

client = logsink.Client(
    'my-client',
    host='localhost',
    port=6789,
    token='logsink-token'
)

# Insert some log data
client.log(
    'some message',
    tag1='tag-1-value',
    tag2='tag-2-value',
)

# Query the data (returns individual log messages)
client.query(
    client_name='my-client',
    tag1='tag-1-value',
    time__gte='2017-01-01',
    time__lte='2018-01-01'
)

# Results are paginated
client.query(
    client_name='my-client',
    tag1='tag-1-value',
    time__gte='2017-01-01',
    time__lte='2018-01-01',
    page=2,
    per_page=25
)

# Aggregate query -- returns counts of specific log messages
# satisfying the query, grouped into time slices
client.agg_query(
    client_name='my-client',
    tag1='tag-1-value',
    time__gte='2017-01-01',
    time__lte='2018-01-01',
    num_intervals=10
)
```

