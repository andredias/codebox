FROM ubuntu:latest
MAINTAINER André Felipe Dias <andre.dias@pronus.io>

RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:git-core/ppa
RUN apt-get update

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-pip \
    ruby nodejs npm golang sqlite3 git subversion python python-pip python-dev build-essential \
    locales

# http://stackoverflow.com/questions/26320901/cannot-install-nodejs-usr-bin-env-node-no-such-file-or-directory
RUN ln -s /usr/bin/nodejs /usr/bin/node

# pacotes
RUN pip3 install flake8 pep8-naming pylint radon
RUN gem install rubocop
RUN npm install -g sloc
RUN npm install -g complexity-report
RUN pip install -U mercurial

RUN adduser --disabled-password --gecos '' --uid 1000 user
RUN locale-gen pt_BR.UTF-8
ENV LANG pt_BR.UTF-8
ENV LC_ALL pt_BR.UTF-8
ENV PYTHONIOENCODING utf-8

WORKDIR /codebox
ADD *.py /codebox/
ADD metrics /codebox/metrics/
# ADD requirements.txt /codebox/
# RUN pip3 install -r requirements.txt
RUN chmod -R 700 /codebox
ENTRYPOINT ["/usr/bin/python3", "codebox.py"]
