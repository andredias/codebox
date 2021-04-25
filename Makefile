PWD := $(shell pwd)

lint:
	@echo
	isort --diff -c --skip-glob '*.venv' .
	@echo
	blue --check --diff --color .
	@echo
	mypy .
	@echo
	flake8 --config flake8.ini .

test: lint test_in_container

test_in_container:
	docker build -t codebox .
	docker build -t codebox-test -f Dockerfile.test .
	docker run -it --rm --init \
	           -v $(PWD)/app:/app \
	           -v $(PWD)/tests/:/tests \
			   codebox-test pytest -svx
