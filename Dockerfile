FROM python:3.11-slim-buster as nsjail-builder

RUN apt -y update \
    && apt install -y \
    bison=2:3.3.* \
    flex=2.6.* \
    g++=4:8.3.* \
    gcc=4:8.3.* \
    git=1:2.20.* \
    libprotobuf-dev=3.6.* \
    libnl-route-3-dev=3.4.* \
    make=4.2.* \
    pkg-config=0.29-6 \
    protobuf-compiler=3.6.*

WORKDIR /nsjail
ARG NSJAIL_VERSION=3.1
RUN git clone -b $NSJAIL_VERSION --single-branch --depth 1 \
    https://github.com/google/nsjail.git .
RUN make
RUN chmod +x nsjail


# ---------------------------------------------------------

FROM python:3.11-slim-buster as builder
LABEL maintainer="André Felipe Dias <andre.dias@pronus.io>"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN DEBIAN_FRONTEND=noninteractive apt update && \
    DEBIAN_FRONTEND=noninteractive apt -y upgrade && \
    apt install -y --no-install-recommends build-essential curl && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

# Build Codebox
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV POETRY_VERSION=1.5.1
RUN curl https://install.python-poetry.org | python -

RUN python -m venv /venv
ENV PATH=/venv/bin:/root/.local/bin:${PATH}

WORKDIR /codebox
COPY pyproject.toml poetry.lock ./

RUN . /venv/bin/activate; \
    poetry install --no-interaction

# ---------------------------------------------------------

FROM python:3.11-slim-buster as final-no-rust

RUN apt -y update && apt install -y --no-install-recommends \
    # nsjail needs these
    libnl-route-3-200=3.4.* \
    libprotobuf17=3.6.* \
    # sqlite3
    sqlite3 \
    # clean up
    && apt autoclean -y \
    && rm -rf /var/lib/apt/lists/*

# help debugging
RUN echo 'alias ll="ls -lahF --color"' >> $HOME/.bashrc

# Codebox configuration

COPY --from=builder /venv /venv
COPY --from=nsjail-builder /nsjail/nsjail /usr/sbin
ENV PATH=/venv/bin:${PATH}

# Install Codebox
WORKDIR /codebox
COPY hypercorn.toml .
COPY app/ ./app

CMD ["hypercorn", "--config=hypercorn.toml", "app.main:app"]


# ---------------------------------------------------------

FROM python:3.11-slim-buster as final

RUN apt -y update && apt install -y --no-install-recommends \
    # nsjail needs these
    libnl-route-3-200=3.4.* \
    libprotobuf17=3.6.* \
    # sqlite3
    sqlite3 \
    # clean up
    && apt autoclean -y \
    && rm -rf /var/lib/apt/lists/*

# Rust installation
ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    PATH=/usr/local/cargo/bin:$PATH

RUN set -eux; \
    apt -y update; \
    apt install -y --no-install-recommends \
    ca-certificates \
    gcc \
    libc6-dev \
    curl \
    ; \
    curl https://sh.rustup.rs -sSf |  \
    sh -s -- --no-modify-path --profile minimal --default-host  \
    x86_64-unknown-linux-gnu  \
    --default-toolchain stable -y; \
    chmod -R a+w $RUSTUP_HOME $CARGO_HOME; \
    rustup --version; \
    cargo --version; \
    rustc --version; \
    apt remove -y --auto-remove; \
    rm -rf /var/lib/apt/lists/*;

# help debugging
RUN echo 'alias ll="ls -lahF --color"' >> $HOME/.bashrc

# Codebox configuration

COPY --from=builder /venv /venv
COPY --from=nsjail-builder /nsjail/nsjail /usr/sbin
ENV PATH=/venv/bin:${PATH}

# Install Codebox
WORKDIR /codebox
COPY hypercorn.toml .
COPY app/ ./app

CMD ["hypercorn", "--config=hypercorn.toml", "app.main:app"]
