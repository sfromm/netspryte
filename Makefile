NAME = 'snmpryte'
PYTHON=python
EPEP8 = "E501,E201,E202,E203,E221,E241,E302,E303"

test: clean
	PYTHONPATH=lib \
		SNMPRYTE_CONFIG=tests/snmpryte.cfg \
		SNMPRYTE_SNMP_HOST="localhost" \
		nosetests -d -v --with-coverage \
		--cover-erase --cover-package=snmpryte -s

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
