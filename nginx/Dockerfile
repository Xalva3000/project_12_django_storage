FROM  nginx:1.19.0-alpine

COPY /etc/letsencrypt/live/storage-monitor.ru/fullchain.pem /etc/nginx/ssl/
COPY /etc/letsencrypt/live/storage-monitor.ru/privkey.pem /etc/nginx/ssl/

COPY ./default.conf /etc/nginx/conf.d/default.conf
