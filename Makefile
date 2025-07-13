SHELL:=/bin/bash

DOCKER:=docker
COMPOSE_DEV:=deployment/docker-compose.dev.yaml
COMPOSE_PROD:=deployment/docker-compose.yaml
CONTAINERS:=db-bas migrator-bas redis-bas

REQUIREMENTS:=./src/requirements.txt
VENVDIR:=./venv
APPENV:=./deployment/bot.env

define compose_file
	$(if $(findstring dev-,$(1)),$(COMPOSE_DEV),$(COMPOSE_PROD))
endef

start:
	source $(VENVDIR)/bin/activate && \
	python3 ./src/run.py --env-file $(APPENV)

init-venv:
	python3 -m venv $(VENVDIR)
	$(VENVDIR)/bin/pip install -r $(REQUIREMENTS)

%up:
	$(DOCKER) compose  -f $(call compose_file,$@) up -d $(CONTAINERS)

%upd:
	$(DOCKER) compose  -f $(call compose_file,$@) up -d --build $(CONTAINERS)

%upda: 
	$(DOCKER) compose  -f $(call compose_file,$@) up --build $(CONTAINERS)

%down:
	$(DOCKER) compose  -f $(call compose_file,$@) down 

.PHONY: example

.PHONY: requirements
requirements:
	$(VENVDIR)/bin/pip freeze > $(REQUIREMENTS)

example:
	python3 ./scripts/exampler.py --dirs ./deployments . \
    --extensions .yaml .env \
    --suffix .example \
    --exclude docker-compose \
    --override