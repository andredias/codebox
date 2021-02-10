FROM python:3.9-slim
MAINTAINER André Felipe Dias <andre.dias@pronus.io>

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y --no-install-recommends build-essential curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python

RUN python -m venv /venv
ENV PATH=/venv/bin:/root/.poetry/bin:${PATH}
RUN pip install --upgrade pip && pip install dumb-init

# pacotes
# RUN gem install rubocop
# RUN npm install -g sloc
# RUN npm install -g complexity-report
# RUN pip3 install -U mercurial

WORKDIR /codebox
COPY pyproject.toml poetry.lock ./
RUN POETRY_VIRTUALENVS_CREATE=false poetry install --no-dev

COPY app/ ./app

USER nobody

ENTRYPOINT ["dumb-init", "--"]
CMD ["/usr/bin/python", "codebox.py"]
