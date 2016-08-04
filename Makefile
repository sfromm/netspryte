NAME = 'netspryte'
PYTHON=python
EPEP8 = "E501,E201,E202,E203,E221,E241,E302,E303"
VERSION := $(shell grep __version lib/$(NAME)/__init__.py | sed -e 's|^.*= ||' -e "s|'||g" )

# Get the branch information from git
ifneq ($(shell which git),)
GIT_DATE := $(shell git log -n 1 --format="%ai")
endif

ifeq ($(OS), FreeBSD)
DATE := $(shell date -j -f "%Y-%m-%d %H:%M:%s"  "$(GIT_DATE)" +%Y%m%d%H%M)
else
ifeq ($(OS), Darwin)
DATE := $(shell date -j -f "%Y-%m-%d %H:%M:%S"  "$(GIT_DATE)" +%Y%m%d%H%M)
else
DATE := $(shell date --utc --date="$(GIT_DATE)" +%Y%m%d%H%M)
endif
endif

# RPM build parameters
RPMSPECDIR = packaging/rpm
RPMSPEC = $(RPMSPECDIR)/$(NAME).spec
RPMDIST = $(shell rpm --eval '%dist')
RPMRELEASE = 1
ifeq ($(OFFICIAL),)
RPMRELEASE = 0.git$(DATE)
endif
RPMNVR = "$(NAME)-$(VERSION)-$(RPMRELEASE)$(RPMDIST)"

test: clean
	PYTHONPATH=lib \
		NETSPRYTE_CONFIG=tests/netspryte.cfg \
		NETSPRYTE_SNMP_HOST="localhost" \
		NETSPRYTE_INFLUXDB_DATABASE="testdb" \
		nosetests -d -v --with-coverage \
		--cover-erase --cover-package=netspryte -s

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

sdist: clean
	$(PYTHON) setup.py sdist

rpmcommon: sdist
	@echo "make rpmcommon"
	@mkdir -p rpm-build
	@cp dist/*.gz rpm-build/
	@echo '$(VERSION)'
	@sed -e 's/^Version:.*/Version: $(VERSION)/' \
		-e 's/^Release:.*/Release: $(RPMRELEASE)%{?dist}/' \
		$(RPMSPEC) > rpm-build/$(NAME).spec

srpm: rpmcommon
	@echo make srpm
	@rpmbuild --define "_topdir %(pwd)/rpm-build" \
		--define "_builddir %{_topdir}" \
		--define "_rpmdir %{_topdir}" \
		--define "_srcrpmdir %{_topdir}" \
		--define "_specdir $(RPMSPECDIR)" \
		--define "_sourcedir %{_topdir}" \
		-bs rpm-build/$(NAME).spec
	@rm -f rpm-build/$(NAME).spec
	@echo "$(NAME) SRPM is built:"
	@echo "    rpm-build/$(RPMNVR).src.rpm"

rpm: rpmcommon
	@rpmbuild --define "_topdir %(pwd)/rpm-build" \
		--define "_builddir %{_topdir}" \
		--define "_rpmdir %{_topdir}" \
		--define "_srcrpmdir %{_topdir}" \
		--define "_specdir $(RPMSPECDIR)" \
		--define "_sourcedir %{_topdir}" \
		-ba rpm-build/$(NAME).spec
	@rm -f rpm-build/$(NAME).spec
	@echo "$(NAME) RPM is built:"
	@echo "    rpm-build/noarch/$(RPMNVR).noarch.rpm"
