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

VENV_ROOT ?= /usr/local/netspryte
VAR_FILE ?= netspryte.params
DOCKER_COMPOSE ?= docker-compose.yml
TIME ?= 1m

.PHONY: venv

include $(VAR_FILE)

RUN_OPTIONS = IMAGE_TAG=$(IMAGE_TAG)
# Get the branch information from git
ifneq ($(shell which git),)
GIT_DATE := $(shell git log -n 1 --format="%ai")
endif

test: clean
	PYTHONPATH=lib \
		NETSPRYTE_CONFIG=tests/netspryte.cfg \
		NETSPRYTE_SNMP_HOST="localhost" \
		NETSPRYTE_INFLUXDB_DATABASE="netspryte-test" \
		nosetests -s -d -v --with-coverage \
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
	-pep8 -r --ignore=$(EPEP8) lib/ 

python:
	$(PYTHON) setup.py build

install:
	$(PYTHON) setup.py install

venv:
	virtualenv $(VENV_ROOT)

venv-install: venv
	$(VENV_ROOT)/bin/pip install -I $(PWD)

sdist: clean
	$(PYTHON) setup.py sdist

build-collector:
	@echo "build netspryte collector container"
	docker build -f $(COLLECTOR_CONTAINER_DIR)/Dockerfile -t $(COLLECTOR_IMAGE_NAME):$(IMAGE_TAG) .

build-web:
	@echo "build netspryte web container"
	docker build -f $(WEB_CONTAINER_DIR)/Dockerfile -t $(WEB_IMAGE_NAME):$(IMAGE_TAG) .

push-collector:
	docker push $(COLLECTOR_IMAGE_NAME)

push-web:
	docker push $(WEB_IMAGE_NAME)

push: push-web push-collector
	@echo "Pushing images to docker hub"

stop:
	@echo "Using docker compose file $(DOCKER_COMPOSE)"
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_COMPOSE) down

start:
	@echo "Using docker compose file $(DOCKER_COMPOSE)"
	$(RUN_OPTIONS) docker-compose -f $(DOCKER_COMPOSE) up -d

cron-show:
	docker exec -it $(MAIN_CONTAINER_NAME) /usr/bin/netspryte-janitor cron -a show -c "/usr/bin/netspryte-collect-snmp -v -M"

cron-add:
	docker exec -it $(MAIN_CONTAINER_NAME) /usr/bin/netspryte-janitor cron -a add -c "/usr/bin/netspryte-collect-snmp -v -M" -t $(TIME)

cron-delete:
	docker exec -it $(MAIN_CONTAINER_NAME) /usr/bin/netspryte-janitor cron -a delete -c "/usr/bin/netspryte-collect-snmp -v -M" -t $(TIME)

