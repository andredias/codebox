FROM python:3.10-slim-buster as nsjail-builder

RUN apt-get -y update \
    && apt-get install -y \
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
RUN git clone -b master --single-branch https://github.com/google/nsjail.git . \
    && git checkout dccf911fd2659e7b08ce9507c25b2b38ec2c5800
RUN make
RUN chmod +x nsjail



# ---------------------------------------------------------

FROM python:3.10-slim as builder
LABEL maintainer="André Felipe Dias <andre.dias@pronus.io>"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get -y upgrade && \
    apt-get install -y --no-install-recommends build-essential curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Build Codebox
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -

RUN python -m venv /venv
ENV PATH=/venv/bin:/root/.local/bin:${PATH}
RUN pip install --upgrade pip

WORKDIR /codebox
COPY pyproject.toml poetry.lock ./
RUN . /venv/bin/activate; \
    poetry install --no-dev


# ---------------------------------------------------------

FROM python:3.10-slim-buster as final

RUN apt-get -y update && apt-get install -y --no-install-recommends \
    # nsjail needs these
    libnl-route-3-200=3.4.* \
    libprotobuf17=3.6.* \
    && apt autoclean -y \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /venv /venv
COPY --from=nsjail-builder /nsjail/nsjail /usr/sbin
ENV PATH=/venv/bin:${PATH}

WORKDIR /codebox
COPY hypercorn.toml .
COPY app/ ./app

CMD ["hypercorn", "--config=hypercorn.toml", "app.main:app"]
