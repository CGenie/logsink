# Log-sink server
This is the API server for the log-sink project.
It is based on [Flask](http://flask.pocoo.org/) with the
[Flask-RESTful](https://flask-restful.readthedocs.io/en/0.3.5/) extension.

To run you need Docker and `docker-compose`:
```bash
docker-compose up
```

Swagger-UI container is included so you can inspect the docs by going to <http://localhost:6788>.
You need to click on 'Authorize' button and type in the sample token `logsink-token`.

## Testing
Install [tox](https://tox.readthedocs.io/en/latest/). Start the server as described above.
Then run

```bash
tox
```

The tests are done using the `TEST_TOKEN` which turns on test mode in the `storage.py`
class which in turns switches the database to a test one. Token <-> DB mapping is
done by a simple `auth.py` Authentication module. It can be further extended to include
arbitrary users with something like Redis as a backend.

If we used Redis as a backend for log storage,
[fakeredis](https://github.com/guilleiguaran/fakeredis)
would be sufficient for testing normally (provided we didn't use advanced Redis functionality
like Lua scripting for example). But with InfluxDB we need to do it on some database.

## Storage
The storage chosen for this project is InfluxDB. It can be switched to any other storage
suitable for the job provided couple of methods are implemented. See
`storage.py -> ABCStorage` abstract class to see what's required.

## Things to do
### Restriction on tags
This is a prototype so simple `**kwargs` passing in functions is used. This has the drawback
that if you define tags using some restricted keywords like `time__lte` or `page`, you
won't be able to query by them. Solution would be to wrap all tags in a JSON string
under the `tags` key and pass that to the GET request when filtering.

### Authentication
The server has 1 predefined token for authentication (under the `ROOT_TOKEN` env variable).
The token is sent via the `X-Auth-Token` header. This scheme can be extended easily to
support users with multiple tokens. See the `token_required` function in `server/api.py`.

### Scheduled removal of data
For pre-defined deprecation of messages in the store, we can use InfluxDB's retention policies:
<https://docs.influxdata.com/influxdb/v1.1/query_language/database_management/#create-retention-policies-with-create-retention-policy>. They operate on database level. If something more
granular is needed, then the simplest thing to do is add some cron job (Celery Scheduler
+ Worker) that will clean up the database periodically. Current API already supports
clearing with filtering (see `test_server.py -> TestServer.test_clear`).

### Tests use `time.sleep` function
InfluxDB is not transactional -- if you insert a row and then immediately query for it,
see <https://docs.influxdata.com/influxdb/v1.1/concepts/insights_tradeoffs/>:

```
V. Scale is critical. The database must be able to handle a high volume of reads and writes.
Pro: The database can handle a high volume of reads and writes
Con: The InfluxDB development team was forced to make tradeoffs to increase performance
```

The tests use the simple `time.sleep` function to wait a while after an insert is
made. We should add some method to check a query predicate continously against the
API before proceeding with the test. So something like:

```python
self.client.log('message')

self.wait_for_new_data(expected_length=1)
```

### SQL injection
Currently we glue the query strings by hand. This is error-prone. Some simple ORM
for InfluxDB would be of great help.
