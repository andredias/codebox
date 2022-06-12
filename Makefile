PWD := $(shell pwd)

run: build
	docker run -d --rm --init -p 8000:8000 \
	--ipc=none --privileged \
	--name codebox codebox

dev:
	docker run -it --rm --init -e ENV=development -p 8000:8000 \
		-v $(PWD)/app:/codebox/app \
		--ipc=none  \
		--privileged  \
		--name codebox codebox \
		hypercorn --reload --config=hypercorn.toml "app.main:app"

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
	pytest -sv --cov-report term-missing --cov-report html --cov-branch \
	       --cov app/

install_hooks:
	@ scripts/install_hooks.sh
