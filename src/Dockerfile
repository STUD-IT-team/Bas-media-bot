FROM python:3.13-alpine

WORKDIR /usr/bot-stuff/

COPY ./requirements.txt /usr/bot-stuff/requirements.txt

RUN set -eux \
    && rm -rf /opt/venv \
    && python -m venv /opt/venv \
    && source /opt/venv/bin/activate \
    && pip install --upgrade pip setuptools wheel \
    && pip install -r /usr/bot-stuff/requirements.txt \
    && rm -rf /root/.cache/pip

COPY . /usr/bot-stuff/

EXPOSE 3012

RUN chmod +x /usr/bot-stuff/entrypoint.sh
ENTRYPOINT ["/usr/bot-stuff/entrypoint.sh"]
