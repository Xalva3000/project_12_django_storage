FROM python:3.11.9-alpine3.19

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    libc-dev \
    make \
    git \
    redis

RUN mkdir /usr/src/storage

ENV PYTHONUNBUFFERED 1
WORKDIR /storage
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
COPY ./storage /storage/

EXPOSE 8000
EXPOSE 80

RUN useradd -m --disabled-password alex && \
    usermod -aG sudo alex \

USER alex
