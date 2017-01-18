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
class which in turns switches the database to a test one.
If we used Redis as a backend, [fakeredis](https://github.com/guilleiguaran/fakeredis)
would be sufficient but with InfluxDB we need to do it on some database.

## Things to do
### Authentication
The server has 1 predefined token for authentication (under the `ROOT_TOKEN` env variable).
The token is sent via the `X-Auth-Token` header. This scheme can be extended easily to
support users with multiple tokens. See the `token_required` function in `server/api.py`.

### Scheduled removal of data
https://docs.influxdata.com/influxdb/v0.9/query_language/database_management/#retention-policy-management

### Test token
Currently we have `test_mode` switch implemented. This makes tests special in the whole
API. If we implemented users & their tokens, tests would just run as a test user.
Then the test framework could set up the test user itself, run the tests, and clean
up afterwards. The API would treat him as a regular user and there would no need to insert
test tokens in the API code anymore.
