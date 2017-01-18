FROM python:3-alpine

VOLUME ["/logsink_server"]

#COPY requirements.txt /logsink_server/requirements.txt
COPY setup.py /logsink_server/setup.py
COPY logsink_server /logsink_server

WORKDIR /logsink_server

#RUN set -x; \
#    pip install -U -r requirements.txt

RUN pip install --editable .