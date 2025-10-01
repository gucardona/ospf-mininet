Com certeza\! Baseado nos arquivos do repositório `gucardona/ospf-mininet`, aqui está uma versão atualizada e mais completa do arquivo `README.md`. Ele agora inclui detalhes sobre as métricas de avaliação que foram adicionadas ao projeto.

-----

# OSPF - Mininet / Quagga

## [English](#english) | [Português](#português)


## Português

### Visão Geral

Este projeto utiliza o **Mininet** para emular uma topologia de rede e o **Quagga** para configurar o roteamento dinâmico com o protocolo **OSPF (Open Shortest Path First)**. O ambiente é totalmente containerizado com o Docker, facilitando a configuração, a execução e a avaliação de desempenho da rede.

O objetivo é demonstrar como os roteadores em uma rede trocam informações de topologia para construir tabelas de roteamento, estabelecer conectividade e analisar o desempenho do protocolo OSPF padrão em um ambiente controlado.

### Características

  - **Simulação de Rede com Mininet**: Cria uma topologia virtual com 5 roteadores e 2 PCs.
  - **Roteamento Dinâmico com Quagga**: Cada roteador executa os daemons `zebra` e `ospfd` para participar do processo OSPF.
  - **Ambiente Dockerizado**: O `Dockerfile` prepara um ambiente Ubuntu 20.04 com todas as dependências necessárias (Mininet, Quagga).
  - **Fácil Execução**: Um script `run.sh` automatiza o processo de build da imagem Docker e execução do contêiner.
  - **Avaliação de Desempenho**: O script de simulação coleta e exibe automaticamente métricas de desempenho da rede.

### Topologia da Rede

A topologia da rede consiste em 5 roteadores (r1 a r5) e 2 computadores (pc1, pc2), conectados da seguinte forma:

```
      (pc1)
        |
        r1 -------- r2
        |  \        |  \
        |   \       |   \
        r3   \      |    r5 -- (pc2)
        |     \     |   /
        |      \    |  /
        r4 ---------+/
```

**Características dos Enlaces:**

| Link | Sub-rede | Delay | Largura de Banda |
| :--- | :--- | :--- | :--- |
| r1-r2 | `10.0.12.0/24` | 5ms | 100 Mbps |
| r1-r3 | `10.0.13.0/24` | 2ms | 10 Mbps |
| r2-r3 | `10.0.23.0/24` | 5ms | 50 Mbps |
| r2-r5 | `10.0.25.0/24` | 7ms | 80 Mbps |
| r3-r4 | `10.0.34.0/24` | 1ms | 200 Mbps |
| r4-r5 | `10.0.45.0/24` | 3ms | 150 Mbps |
| pc1-r1| `172.16.1.0/24` | - | - |
| pc2-r5| `172.16.5.0/24` | - | - |

### Como Executar

#### Pré-requisitos

  - Docker instalado no seu sistema.

#### Início Rápido

1.  **Clone o repositório** (se ainda não o fez).

2.  **Execute o script de inicialização**:
    O script `run.sh` irá construir a imagem Docker e iniciar o contêiner com os privilégios necessários para o Mininet.

    ```bash
    chmod +x run.sh
    ./run.sh
    ```

3.  **Acompanhe a Simulação**:
    O script iniciará a rede, e as métricas de desempenho serão exibidas no console. Após a coleta de métricas, você será levado ao prompt de comando (CLI) do Mininet. **Aguarde cerca de 30 segundos** para que o OSPF convirja.

4.  **Interaja com a rede**:

    ```bash
    # Testar a conectividade entre todos os nós
    mininet> pingall

    # Verificar a tabela de roteamento de um roteador (ex: r1)
    mininet> r1 route -n

    # Executar um traceroute de pc1 para pc2
    mininet> pc1 traceroute 172.16.5.10
    ```

5.  **Sair da simulação**:

    ```bash
    mininet> exit
    ```

### Métricas e Avaliação

O script `run_mininet_quagga.py` coleta e exibe automaticamente as seguintes métricas de desempenho:

  - **Tempo de Convergência**: Mede o tempo desde a inicialização da rede até que todos os nós consigam se comunicar entre si (`pingall`).
  - **QoS (iperf)**: Realiza um teste de vazão entre `pc1` e `pc2` para medir a largura de banda e o volume de dados transferidos.
  - **Tamanho da Tabela de Roteamento**: Conta o número de rotas instaladas em cada roteador, indicando o consumo de memória do protocolo.
  - **Análise de Caminho (traceroute)**: Exibe o caminho completo que os pacotes percorrem de `pc1` a `pc2`, mostrando os saltos intermediários.
  - **Overhead do Protocolo**: Analisa os logs do Quagga para contar o número de LSAs (Link-State Advertisements) gerados, uma medida do tráfego de controle do OSPF.

### Monitoramento e Debug

Cada roteador gera logs para os daemons do Quagga no diretório `/tmp/` dentro do contêiner. Você pode inspecioná-los a partir da CLI do Mininet para verificar o status da vizinhança OSPF.

```bash
# Verificar o log do daemon OSPF no roteador r1
mininet> r1 cat /tmp/r1-ospfd.log

# Verificar o log do daemon Zebra (tabela de roteamento) no r1
mininet> r1 cat /tmp/r1-zebra.log
```

-----

## English

### Overview

This project uses **Mininet** to emulate a network topology and **Quagga** to configure dynamic routing with the **OSPF (Open Shortest Path First)** protocol. The environment is fully containerized with Docker, simplifying setup, execution, and network performance evaluation.

The goal is to demonstrate how routers in a network exchange topology information to build routing tables, establish connectivity, and analyze the performance of the standard OSPF protocol in a controlled environment.

### Features

  - **Network Simulation with Mininet**: Creates a virtual topology with 5 routers and 2 PCs.
  - **Dynamic Routing with Quagga**: Each router runs the `zebra` and `ospfd` daemons to participate in the OSPF process.
  - **Dockerized Environment**: The `Dockerfile` sets up an Ubuntu 20.04 environment with all necessary dependencies (Mininet, Quagga).
  - **Easy Execution**: A `run.sh` script automates the Docker image build and container execution process.
  - **Performance Evaluation**: The simulation script automatically collects and displays network performance metrics.

### Network Topology

The network topology consists of 5 routers (r1 to r5) and 2 computers (pc1, pc2), connected as follows:

```
      (pc1)
        |
        r1 -------- r2
        |  \        |  \
        |   \       |   \
        r3   \      |    r5 -- (pc2)
        |     \     |   /
        |      \    |  /
        r4 ---------+/
```

**Link Characteristics:**

| Link | Subnet | Delay | Bandwidth |
| :--- | :--- | :--- | :--- |
| r1-r2 | `10.0.12.0/24` | 5ms | 100 Mbps |
| r1-r3 | `10.0.13.0/24` | 2ms | 10 Mbps |
| r2-r3 | `10.0.23.0/24` | 5ms | 50 Mbps |
| r2-r5 | `10.0.25.0/24` | 7ms | 80 Mbps |
| r3-r4 | `10.0.34.0/24` | 1ms | 200 Mbps |
| r4-r5 | `10.0.45.0/24` | 3ms | 150 Mbps |
| pc1-r1| `172.16.1.0/24` | - | - |
| pc2-r5| `172.16.5.0/24` | - | - |

### How to Run

#### Prerequisites

  - Docker installed on your system.

#### Quick Start

1.  **Clone the repository** (if you haven't already).

2.  **Execute the startup script**:
    The `run.sh` script will build the Docker image and start the container with the necessary privileges for Mininet.

    ```bash
    chmod +x run.sh
    ./run.sh
    ```

3.  **Follow the Simulation**:
    The script will start the network, and performance metrics will be displayed on the console. After the metrics are collected, you will be dropped into the Mininet command-line interface (CLI). **Wait for about 30 seconds** for OSPF to converge.

4.  **Interact with the network**:

    ```bash
    # Test connectivity between all nodes
    mininet> pingall

    # Check the routing table of a router (e.g., r1)
    mininet> r1 route -n

    # Run a traceroute from pc1 to pc2
    mininet> pc1 traceroute 172.16.5.10
    ```

5.  **Exit the simulation**:

    ```bash
    mininet> exit
    ```

### Metrics and Evaluation

The `run_mininet_quagga.py` script automatically collects and displays the following performance metrics:

  - **Convergence Time**: Measures the time from network startup until all nodes can communicate with each other (`pingall`).
  - **QoS (iperf)**: Performs a throughput test between `pc1` and `pc2` to measure bandwidth and the volume of data transferred.
  - **Routing Table Size**: Counts the number of routes installed in each router, indicating the protocol's memory overhead.
  - **Path Analysis (traceroute)**: Displays the full path that packets take from `pc1` to `pc2`, showing the intermediate hops.
  - **Protocol Overhead**: Analyzes Quagga logs to count the number of LSAs (Link-State Advertisements) generated, a measure of OSPF's control plane traffic.

### Monitoring and Debugging

Each router generates logs for the Quagga daemons in the `/tmp/` directory inside the container. You can inspect them from the Mininet CLI to check the OSPF neighborhood status.

```bash
# Check the OSPF daemon log on router r1
mininet> r1 cat /tmp/r1-ospfd.log

# Check the Zebra daemon log (routing table) on r1
mininet> r1 cat /tmp/r1-zebra.log
```
