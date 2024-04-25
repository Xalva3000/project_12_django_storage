FROM python:3.11.9-alpine3.19

RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./storage /storage

WORKDIR /storage

EXPOSE 8000
EXPOSE 80
EXPOSE 5555


COPY ./entrypoint.sh /
ENTRYPOINT ["sh", "/entrypoint.sh"]
