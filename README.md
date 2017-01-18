# Log sink
This is an implementation of a server which collects log messages from arbitrary sources and stores them.
The server can then be queried with optional filters by time, log message and tags.
Also, a Python client library is included for easy interaction with the server.

## Client library
For more info, see `lib/README.md`.


## Server
For more info, see `server/README.md`.

InfluxDB aggregation:
https://docs.influxdata.com/influxdb/v1.1/query_language/data_exploration/#group-by-time-intervals-and-fill

Regexp query (https://docs.influxdata.com/influxdb/v1.1/query_language/data_exploration/#regular-expressions-in-queries):
SELECT /<regular_expression_field_key>/ FROM /<regular_expression_measurement>/ WHERE [<tag_key> <operator> /<regular_expression_tag_value>/ | <field_key> <operator> /<regular_expression_field_value>/]

TODO:
* client-side library
* server-side API
** fields: time, message, arbitrary tags
* storage: time, log facility, log message, additional data (request headers, user id, user email)
* server should provide aggregated information
* write in README:
** how to implement search by querystring argument?
** automatically remove messages after specific time
* info that storage.py has abstract 'insert/query/aggregated' interface and we can also use
  Prometheus or Redis
