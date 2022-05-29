PWD := $(shell pwd)

run: build
	docker run -it --rm --init  -p 8000:8000 \
	--privileged -v /sys/fs/cgroup:/sys/fs/cgroup \
	--name codebox codebox

dev:
	docker run -it --rm --init -e ENV=development -p 8000:8000 \
		-v $(PWD)/app:/codebox/app \
		--privileged  \
		--name codebox codebox \
		hypercorn --reload --config=hypercorn.toml "app.main:app"

lint:
	@echo
	isort --diff -c --skip-glob '*.venv' .
	@echo
	blue --check --diff --color .
	@echo
	flake8 .
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
