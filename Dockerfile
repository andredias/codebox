FROM python:3.9-slim
MAINTAINER André Felipe Dias <andre.dias@pronus.io>

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y --no-install-recommends build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN python -m venv /venv
ENV PATH=/venv/bin:${PATH}
RUN pip install --upgrade pip && pip install dumb-init

# pacotes
# RUN gem install rubocop
# RUN npm install -g sloc
# RUN npm install -g complexity-report
# RUN pip3 install -U mercurial

WORKDIR /codebox
COPY app/requirements.txt .
RUN pip install -r requirements.txt
COPY app/ .

USER nobody

ENTRYPOINT ["dumb-init", "--"]
CMD ["/usr/bin/python", "codebox.py"]
