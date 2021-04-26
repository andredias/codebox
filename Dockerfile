FROM python:3.9-slim as builder
LABEL maintainer="André Felipe Dias <andre.dias@pronus.io>"

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
RUN pip install --upgrade pip

WORKDIR /codebox
COPY pyproject.toml poetry.lock ./
RUN POETRY_VIRTUALENVS_CREATE=false poetry install --no-dev

# ----

FROM python:3.9-slim as final

COPY --from=builder /venv /venv
ENV PATH=/venv/bin:${PATH}

WORKDIR /codebox
COPY main.py .
COPY app/ ./app

USER nobody

CMD ["/venv/bin/python", "main.py"]
