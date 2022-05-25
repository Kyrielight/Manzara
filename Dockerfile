FROM python:3.8.6-alpine

LABEL MAINTAINER="kyrielight@best.moe"

RUN apk update && apk upgrade && \
    apk add --no-cache git

COPY requirements.txt /opt/requirements.txt
RUN pip3 install --no-cache-dir -r /opt/requirements.txt && rm /opt/requirements.txt

COPY commands /usagi12/commands
COPY src /usagi12/src
COPY usagi12.py /usagi12/

WORKDIR /usagi12
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8080", "usagi12:app"]
