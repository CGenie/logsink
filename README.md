# Logsink
This is an implementation of a server which collects log messages from arbitrary sources and stores them.
The server can then be queried with optional filters by time, log message and tags.
Also, a Python client library is included for easy interaction with the server.

## Client library
For more info, see `logsink/README.md`.


## Server
For more info, see `server/README.md`.


## How it works
The DB backend we use is [InfluxDB](https://www.influxdata.com/). This is a time-series
database, suitable for creating event aggregations and log storage we implement here fits
this nicely.

An alternative is [Prometheus](https://prometheus.io) however it doesn't allow for
tags aggregation with each event
(<https://prometheus.io/docs/introduction/comparison/#prometheus-vs.-influxdb>).
This saves space but makes tracking of tags really difficult. And since we want
to persist the logs for short amount of time, disk space usage shouldn't be of
a big issue.

InfluxDB tags, on the other hand, allow us to make arbitrary queries about the log data.

InfluxDB supports aggregation out of the box:
<https://docs.influxdata.com/influxdb/v1.1/query_language/data_exploration/#group-by-time-intervals-and-fill>

For text search in log message we use the regexp query funcitonality:
<https://docs.influxdata.com/influxdb/v1.1/query_language/data_exploration/#regular-expressions-in-queries>

```
SELECT /<regular_expression_field_key>/ FROM /<regular_expression_measurement>/ WHERE [<tag_key> <operator> /<regular_expression_tag_value>/ | <field_key> <operator> /<regular_expression_field_value>/]
```

TODO:
* server-side API
* write in README:
** how to implement search by querystring argument?
