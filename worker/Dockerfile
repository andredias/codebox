FROM ubuntu:latest
MAINTAINER André Felipe Dias <andref.dias@gmail.com>

RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y ruby nodejs npm golang
RUN ln -s /usr/bin/nodejs /usr/bin/node  # http://stackoverflow.com/questions/26320901/cannot-install-nodejs-usr-bin-env-node-no-such-file-or-directory

# pacotes
RUN pip3 install sh flake8 pep8-naming pylint radon
RUN gem install rubocop
RUN npm install -g sloc
RUN npm install -g complexity-report

RUN adduser --disabled-password --gecos '' --uid 1000 user

ENV PYTHONIOENCODING utf-8

WORKDIR /codebox
ADD *.py /codebox/
ADD flint++ /codebox/
RUN chmod -R 700 /codebox
ENTRYPOINT ["/usr/bin/python3", "worker.py"]
