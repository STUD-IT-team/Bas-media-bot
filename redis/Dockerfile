FROM redis:alpine3.20

WORKDIR /usr/redis-stuff/

COPY . /usr/redis-stuff/

RUN chmod +x /usr/redis-stuff/entrypoint.sh
ENTRYPOINT [ "/usr/redis-stuff/entrypoint.sh" ]
