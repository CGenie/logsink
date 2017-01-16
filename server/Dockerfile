FROM python:3-alpine

VOLUME ["/logsink_server"]

COPY requirements.txt /logsink_server/requirements.txt

WORKDIR /logsink_server

RUN set -x; \
    pip install -U -r requirements.txt