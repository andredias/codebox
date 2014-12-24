FROM ubuntu:latest
MAINTAINER André Felipe Dias <andref.dias@gmail.com>

RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN pip3 install sh
RUN pip3 install flake8
RUN pip3 install pylint
RUN pip3 install radon
RUN apt-get install -y clang ruby nodejs golang
RUN adduser --disabled-password --gecos '' worker && \
    adduser worker sudo && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

ENV PYTHONIOENCODING utf-8

USER worker
WORKDIR /home/worker

ADD worker.py /home/worker/
ENTRYPOINT ["/usr/bin/python3", "worker.py"]
