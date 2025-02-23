FROM redis:alpine3.20

RUN mkdir /startup
WORKDIR /startup

COPY . .
RUN chmod +x /startup/entrypoint.sh

CMD [ "/startup/entrypoint.sh" ] 