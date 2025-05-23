FROM alpine:3.17.0

WORKDIR /usr/migrations-stuff/

RUN set -eux \
    && apk add --no-cache curl \
    && (curl -fsSL https://raw.githubusercontent.com/pressly/goose/master/install.sh | sh) \
    && apk del curl \
    && rm -rf /var/cache/apk/*

COPY . /usr/migrations-stuff/

RUN chmod +x /usr/migrations-stuff/entrypoint.sh
ENTRYPOINT ["/usr/migrations-stuff/entrypoint.sh"]
