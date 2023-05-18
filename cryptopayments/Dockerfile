FROM python:3.9.16-slim


RUN apt-get update && \
    apt-get -y install build-essential libssl-dev python-dev python3-dev libgmp3-dev

WORKDIR /app

COPY requirements.txt .


RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir --upgrade -r requirements.txt
