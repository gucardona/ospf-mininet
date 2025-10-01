# ospf_mininet/Dockerfile

FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Instala as dependências básicas, Mininet e Quagga
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  git \
  python3 \
  ca-certificates \
  sudo \
  lsb-release \
  iputils-ping \
  traceroute \
  quagga \
  quagga-doc \
  nano && \
  rm -rf /var/lib/apt/lists/*

# Instala o Mininet
RUN git clone https://github.com/mininet/mininet /tmp/mininet && \
  /tmp/mininet/util/install.sh -a && \
  rm -rf /tmp/mininet

ENV SHELL /bin/bash

WORKDIR /app
COPY . .

# Comando padrão para iniciar a simulação Quagga
CMD ["python3", "run_mininet_quagga.py"]
