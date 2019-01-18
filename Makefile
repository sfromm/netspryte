NAME = 'netspryte'
PYTHON=python
EPEP8 = "E501,E201,E202,E203,E221,E241,E302,E303"
VERSION := $(shell grep __version lib/$(NAME)/__init__.py | sed -e 's|^.*= ||' -e "s|'||g" )
BRANCH ?= $(shell git rev-parse --abbrev-ref HEAD)
ifeq ($(BRANCH),master)
	IMAGE_TAG = latest
else
	IMAGE_TAG = $(BRANCH)
endif

VENV_ROOT ?= venv
VAR_FILE ?= netspryte.params
HOST_VAR_FILE ?= netspryte.params.$(HOSTNAME)
DOCKER_COMPOSE ?= docker-compose.yml
COLLECTOR_INTERVAL ?= 1m
DISCOVER_INTERVAL ?= 1h

# Include the default parameters file.
# And optionally include a host-specific parameters file to override defaults.
include $(VAR_FILE)
-include $(HOST_VAR_FILE)

RUN_OPTIONS = IMAGE_TAG=$(IMAGE_TAG)
# Get the branch information from git
ifneq ($(shell which git),)
GIT_DATE := $(shell git log -n 1 --format="%ai")
endif

test: clean
	PYTHONPATH=lib \
		NETSPRYTE_CONFIG=tests/netspryte.cfg \
		NETSPRYTE_INFLUXDB_DATABASE="netspryte-test" \
		nosetests -s -v --with-coverage \
		--cover-erase --cover-package=netspryte

clean:
	@echo "Cleaning distutils leftovers"
	rm -rf build
	rm -rf dist
	@echo "Cleaning up byte compiled python files"
	find . -type f -regex ".*\.py[co]$$" -delete
	@echo "Cleaning up RPM build files"
	rm -rf MANIFEST rpm-build

pep8:
	@echo "Running PEP8 compliance tests"
	-flake8 --ignore=$(EPEP8) lib/

python:
	$(PYTHON) setup.py build

install:
	$(PYTHON) setup.py install

venv:
	python3 -mvenv $(VENV_ROOT)

venv-install: venv
	$(VENV_ROOT)/bin/pip3 install -I $(PWD)

sdist: clean
	$(PYTHON) setup.py sdist

build-collector:
	@echo "build netspryte collector container"
	docker build -f $(COLLECTOR_CONTAINER_DIR)/Dockerfile -t $(COLLECTOR_IMAGE_NAME):$(IMAGE_TAG) .

build-web:
	@echo "build netspryte web container"
	docker build -f $(WEB_CONTAINER_DIR)/Dockerfile -t $(WEB_IMAGE_NAME):$(IMAGE_TAG) .

build: build-collector build-web
	@echo "Build collector and web containers"

push-collector:
	docker push $(COLLECTOR_IMAGE_NAME)

push-web:
	docker push $(WEB_IMAGE_NAME)

push: push-collector push-web
	@echo "Push images to docker hub"

down:
	@echo "Using docker compose file $(DOCKER_COMPOSE)"
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_COMPOSE) down

stop:
	@echo "Using docker compose file $(DOCKER_COMPOSE)"
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_COMPOSE) stop

stop-db:
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_COMPOSE) stop database

stop-web:
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_COMPOSE) stop web

stop-collector:
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_COMPOSE) stop collector

start:
	@echo "Using docker compose file $(DOCKER_COMPOSE)"
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_COMPOSE) up -d

start-db:
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_COMPOSE) up -d database

start-web:
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_COMPOSE) up -d web

start-collector:
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_COMPOSE) up -d collector


status:
	@echo "Using docker compose file $(DOCKER_COMPOSE)"
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_COMPOSE) ps

restart: restart-db restart-web restart-collector

restart-db:
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_COMPOSE) restart database

restart-web:
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_COMPOSE) restart web

restart-collector:
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_COMPOSE) restart collector

update:
	@echo "Update netspryte and container images"
	git pull
	docker pull $(COLLECTOR_IMAGE_NAME):$(IMAGE_TAG)
	docker pull $(WEB_IMAGE_NAME):$(IMAGE_TAG)
	docker pull $(DB_IMAGE_NAME):$(DB_IMAGE_TAG)

ps: status

cli:
	docker exec -it $(COLLECTOR_CONTAINER_NAME) /bin/bash

cron-show:
	docker exec -it $(COLLECTOR_CONTAINER_NAME) $(CONTAINER_EXEC_PATH)/netspryte-janitor -v cron -a show -j all

cron-add:
	docker exec -it $(COLLECTOR_CONTAINER_NAME) \
		$(CONTAINER_EXEC_PATH)/netspryte-janitor -v cron -a add \
		-I $(COLLECTOR_INTERVAL) -j "netspryte-collect-snmp -v"
	docker exec -it $(COLLECTOR_CONTAINER_NAME) \
		$(CONTAINER_EXEC_PATH)/netspryte-janitor -v cron -a add \
		-I $(DISCOVER_INTERVAL) -j "netspryte-discover -v"

cron-delete:
	docker exec -it $(COLLECTOR_CONTAINER_NAME) \
		$(CONTAINER_EXEC_PATH)/netspryte-janitor -v cron -a delete \
		-I $(COLLECTOR_INTERVAL) -j "netspryte-collect-snmp -v"
	docker exec -it $(COLLECTOR_CONTAINER_NAME) \
		$(CONTAINER_EXEC_PATH)/netspryte-janitor -v cron -a delete \
		-I $(DISCOVER_INTERVAL) -j "netspryte-discover -v"

initdb:
	docker exec -it $(COLLECTOR_CONTAINER_NAME) $(CONTAINER_EXEC_PATH)/netspryte-janitor initdb

.PHONY: venv
