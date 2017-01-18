# Log-sink server
This is the API server for the log-sink project.
It is based on [Flask](http://flask.pocoo.org/) with the
[Flask-RESTful](https://flask-restful.readthedocs.io/en/0.3.5/) extension.

To run you need Docker and `docker-compose`:
```bash
docker-compose up
```

Swagger-UI container is included so you can inspect the docs by going to <http://localhost:6788>.

## Things to do
### Authentication
The server has 1 predefined token for authentication (under the `ROOT_TOKEN` env variable).
The token is sent via the `X-Auth-Token` header. This scheme can be extended easily to
support users with multiple tokens. See the `token_required` function in `server/api.py`.
