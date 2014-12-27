FROM ubuntu:latest
MAINTAINER André Felipe Dias <andref.dias@gmail.com>

RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN pip3 install sh flake8 pep8-naming pylint radon
RUN apt-get install -y ruby nodejs golang
RUN apt-get install -y clang
RUN adduser --disabled-password --gecos '' --uid 1000 user

ENV PYTHONIOENCODING utf-8

WORKDIR /codebox
ADD worker.py /codebox/
RUN chmod -R 700 /codebox
ENTRYPOINT ["/usr/bin/python3", "worker.py"]
