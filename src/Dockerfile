FROM python:3.13-alpine

RUN apk add --no-cache make bash && \
    mkdir -p /app && \
    rm -rf /opt/venv

WORKDIR /app

COPY ./src/ ./src/
COPY Makefile .

RUN make init-venv

CMD ["make", "start"]