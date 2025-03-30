FROM python:3.13-alpine

RUN rm -rf /opt/venv
RUN python -m venv /opt/venv
RUN source /opt/venv/bin/activate

COPY ./src/requirements.txt .
COPY ./src/ .

RUN pip install -r requirements.txt

EXPOSE 3012

CMD ["python3.13", "./run.py"]