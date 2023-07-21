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
	ruff .
	@echo
	blue --check --diff --color .
	@echo
	mypy .
	@echo
	pip-audit


format:
	ruff --silent --exit-zero --fix .
	blue .


build:
	docker build -t codebox .

test:
	docker run --rm --init -e ENV=testing -p 8000:8000 \
		-v $(PWD)/app:/codebox/app \
		-v $(PWD)/tests:/codebox/tests \
		--ipc=none  \
		--privileged  \
		--name codebox codebox \
		pytest -svx --cov-report term-missing \
		   --cov-report html --cov-branch --cov app/

install_hooks:
	@ scripts/install_hooks.sh
