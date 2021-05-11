PWD := $(shell pwd)

run: build
	docker run -it --rm --init --privileged -p 8000:8000 --name codebox codebox

dev:
	docker run -it --rm --init --privileged -p 8000:8000 \
		-v $(PWD)/app:/codebox/app --name codebox codebox

lint:
	@echo
	isort --diff -c --skip-glob '*.venv' .
	@echo
	blue --check --diff --color .
	@echo
	mypy .
	@echo
	flake8 --config flake8.ini .

format_code:
	isort .
	blue .

build:
	docker build -t codebox .

test: lint test_container

test_container: build
	pytest -svx
