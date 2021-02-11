PWD := $(shell pwd)

check:
	@echo
	isort --diff -c --skip-glob '*.venv' .
	@echo
	yapf -vv --diff --recursive --style yapf.ini --exclude '*.venv' .
	@echo
	mypy fastapi_api
	mypy quart_api
	@echo
	flake8 --config flake8.ini .

test: test_in_container

test_in_container:
	docker build -t codebox .
	docker build -t codebox-test -f Dockerfile.test .
	docker run -it --rm  \
	           -v $(PWD)/app:/app \
	           -v $(PWD)/tests/:/tests \
			   codebox-test pytest -svx
