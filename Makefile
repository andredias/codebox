SHELL := /usr/bin/env bash -O globstar
PWD := $(shell pwd)

run:
	docker run -it --rm --init -p 8000:8000 \
		-v $(PWD)/codebox:/app/codebox \
		--ipc=none  \
		--privileged  \
		--name codebox codebox \
		hypercorn --reload --config=hypercorn.toml "codebox.main:app"

# use dev to manually run tests in the container
dev:
	docker run -it --rm --init -e ENV=testing -p 8000:8000 \
		-v $(PWD)/codebox:/app/codebox \
		-v $(PWD)/tests:/app/tests \
		--ipc=none  \
		--privileged  \
		--name codebox codebox bash


 lint:
	@echo
	ruff check --diff .
	@echo
	ruff format --diff .
	@echo
	mypy .


format:
	ruff --silent --exit-zero --fix .
	ruff format .


audit:
	pip-audit


build:
	docker build -t codebox .


test:
	docker run --rm --init -e ENV=testing -p 8000:8000 \
		-v $(PWD)/codebox:/app/codebox \
		-v $(PWD)/tests:/app/tests \
		--ipc=none  \
		--privileged  \
		--name codebox codebox \
		pytest -x --cov-report term-missing \
		   --cov-report html --cov-branch --cov codebox/

install_hooks:
	@ scripts/install_hooks.sh
