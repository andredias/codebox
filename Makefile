PWD := $(shell pwd)

run:
	docker run -it --rm --init -e ENV=development -p 8000:8000 \
		-v $(PWD)/app:/codebox/app \
		--ipc=none  \
		--privileged  \
		--name codebox codebox \
		hypercorn --reload --config=hypercorn.toml "app.main:app"

# use dev to manually run tests in the container
dev:
	docker run -it --rm --init -e ENV=testing -p 8000:8000 \
		-v $(PWD)/app:/codebox/app \
		-v $(PWD)/tests:/codebox/tests \
		--ipc=none  \
		--privileged  \
		--name codebox codebox bash

lint:
	@echo
	isort --diff -c .
	@echo
	blue --check --diff --color .
	@echo
	flake8 .
	@echo
	mypy .
	@echo
	bandit -qr codebox/
	@echo
	pip-audit

format:
	isort .
	blue .
	pyupgrade --py310-plus **/*.py

build:
	docker build -t codebox .

test:
	docker run --rm --init -e ENV=testing -p 8000:8000 \
		-v $(PWD)/app:/codebox/app \
		-v $(PWD)/tests:/codebox/tests \
		--ipc=none  \
		--privileged  \
		--name codebox codebox \
		pytest -sv --cov-report term-missing \
		   --cov-report html --cov-branch --cov app/

install_hooks:
	@ scripts/install_hooks.sh
