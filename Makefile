PWD := $(shell pwd)

run: build
	docker run -it --rm --init --privileged -p 8000:8000 --name codebox codebox

dev:
	docker run -it --rm --init -e ENV=development --privileged -p 8000:8000 \
		-v $(PWD)/app:/codebox/app --name codebox-dev codebox \
		hypercorn --reload --config=hypercorn.toml "app.main:app"

lint:
	@echo
	isort --diff -c --skip-glob '*.venv' .
	@echo
	blue --check --diff --color .
	@echo
	flakehell lint .
	@echo
	mypy .

format_code:
	isort .
	blue .

build:
	docker build -t codebox .

test: lint build test_only

test_only:
	pytest -svx
