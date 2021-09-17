FROM ubuntu:20.10 as nsjail-builder

RUN apt-get -y update && apt-get install -y \
    autoconf \
    bison \
    flex \
    gcc \
    g++ \
    git \
    libprotobuf-dev \
    libnl-route-3-dev \
    libtool \
    make \
    pkg-config \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

RUN latest_tag=$(git ls-remote --tags --exit-code --refs https://github.com/google/nsjail.git \
    | sed -E 's/^[[:xdigit:]]+[[:space:]]+refs\/tags\/(.+)/\1/g' | tail -n1); \
    git clone \
    -b "$latest_tag" \
    --single-branch \
    --depth 1 \
    https://github.com/google/nsjail.git /nsjail
WORKDIR /nsjail
RUN make
RUN chmod +x nsjail


# ---------------------------------------------------------

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

# Install languages

# Install rust
ENV CARGO_HOME=/venv/rust
ENV RUSTUP_HOME=/venv/rust
RUN curl https://sh.rustup.rs -sSf |  \
    sh -s -- --profile minimal --default-host x86_64-unknown-linux-gnu \
    --default-toolchain stable -y

# ---------------------------------------------------------

FROM python:3.9-slim as final

RUN apt update -y && \
    apt install -y --no-install-recommends \
    # rust needs build-essential
    build-essential \
    # nsjail needs these
    libnl-route-3-200 \
    libprotobuf-dev \
    && apt autoclean -y \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /venv /venv
COPY --from=nsjail-builder /nsjail/nsjail /usr/sbin
ENV PATH=/venv/bin:/venv/rust/bin:${PATH}

WORKDIR /codebox
COPY hypercorn.toml .
COPY app/ ./app

CMD ["hypercorn", "--config=hypercorn.toml", "app.main:app"]
