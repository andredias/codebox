PWD := $(shell pwd)

test: test_in_container

test_in_container:
	docker build -t codebox-test -f Dockerfile.test .
	docker run -it --rm  \
	           -v $(PWD)/app:/app \
	           -v $(PWD)/tests/:/tests \
			   codebox-test pytest -svx
