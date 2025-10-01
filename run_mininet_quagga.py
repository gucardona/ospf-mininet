#!/usr/bin/env python3
from mininet.net import Mininet
from mininet.node import Controller, OVSBridge
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel
import os
import time

def start_network():
    """
    Cria e configura a topologia de rede no Mininet para rodar Quagga OSPF.
    A topologia é idêntica à usada pelo ospf-intent-aware.
    """
    net = Mininet(controller=Controller, link=TCLink, switch=OVSBridge)

    print("*** Criando roteadores (hosts Mininet)")
    routers = [net.addHost(f"r{i}", ip=None) for i in range(1, 6)]
    r1, r2, r3, r4, r5 = routers

    print("*** Criando PCs (hosts Mininet)")
    pc1 = net.addHost('pc1', ip='172.16.1.10/24')
    pc2 = net.addHost('pc2', ip='172.16.5.10/24')

    # Configuração dos links entre roteadores
    links_config = [
        (r1, r2, "10.0.12.0/24", "5ms", 100),
        (r1, r3, "10.0.13.0/24", "2ms", 10),
        (r2, r3, "10.0.23.0/24", "5ms", 50),
        (r2, r5, "10.0.25.0/24", "7ms", 80),
        (r3, r4, "10.0.34.0/24", "1ms", 200),
        (r4, r5, "10.0.45.0/24", "3ms", 150),
    ]

    print("*** Criando links entre roteadores")
    for src, dst, subnet, delay, bw in links_config:
        src_ip = subnet.replace("0/24", "1/24")
        dst_ip = subnet.replace("0/24", "2/24")
        net.addLink(src, dst, delay=delay, bw=bw, params1={"ip": src_ip}, params2={"ip": dst_ip})

    # Configuração dos links entre PCs e roteadores
    print("*** Criando links entre PCs e roteadores")
    net.addLink(pc1, r1, params1={'ip': '172.16.1.10/24'}, params2={'ip': '172.16.1.1/24'})
    net.addLink(pc2, r5, params1={'ip': '172.16.5.10/24'}, params2={'ip': '172.16.5.1/24'})

    print("*** Iniciando a rede")
    net.start()

    start_time = time.time()
    print(f"[{start_time}] METRIC_NETWORK_START_TIME")

    # Configura a rota padrão nos PCs
    print("*** Configurando rota padrão nos PCs")
    pc1.cmd('ip route add default via 172.16.1.1')
    pc2.cmd('ip route add default via 172.16.5.1')

    print("*** Habilitando encaminhamento IP e iniciando daemons Quagga")
    for r in routers:
        print(f"--- Configurando {r.name} ---")
        r.cmd("sysctl -w net.ipv4.ip_forward=1")
        # Garanta que o caminho para as configurações está correto
        config_dir = os.path.abspath(f'./quagga_configs/{r.name}')
        
        # Inicia o daemon zebra, responsável pela tabela de roteamento do kernel
        r.cmd(f'/usr/sbin/zebra -d -f {config_dir}/zebra.conf -z /tmp/zebra_{r.name}.api -i /tmp/zebra_{r.name}.pid')
        time.sleep(1)

        # Inicia o daemon OSPF
        r.cmd(f'/usr/sbin/ospfd -d -f {config_dir}/ospfd.conf -z /tmp/zebra_{r.name}.api -i /tmp/ospfd_{r.name}.pid')

    # --- Métricas ---
    convergence_metric(net, start_time)
    qos_metric(pc1, pc2)
    routing_table_metric(routers)
    path_analysis_metric(pc1, pc2)
    quagga_overhead_metric(routers, start_time)
    # ----------------

    print("\n*** Rede pronta com Quagga OSPF. Daemons estão convergindo.")
    print("*** Verifique /tmp/rX-*.log nos roteadores para a saída dos daemons.")
    print("*** Use a CLI. Tente 'pc1 ping pc2' ou 'pingall' após ~30 segundos.")
    CLI(net)

    print("*** Parando os daemons Quagga")
    for r in routers:
        r.cmd("killall zebra")
        r.cmd("killall ospfd")

    net.stop()

def convergence_metric(net, start_time):
    print("\n*** Aguardando conectividade total da rede (pingall com fail-fast)...")

    for _ in range(120):
        if ping_all_fail_fast(net):
            end_time = time.time()
            convergence_time = end_time - start_time
            formatted_result = (
            f"\n"
            f"    Tipo: pingall fail-fast\n"
            f"    Tempo de Convergência: {convergence_time:.4f}sec\n"
            )
            print(f"--- METRIC_CONVERGENCE_START ---\n{formatted_result}\n--- METRIC_CONVERGENCE_END ---")
            break
        time.sleep(0.5) 
    else:
        print("*** AVISO: Timeout! Conectividade total (pingall) não foi estabelecida.")

def ping_all_fail_fast(net):
    """
    Executa um 'pingall', mas para e retorna False na primeira falha.
    Isso evita esperar o timeout de todos os outros pings.
    Retorna True somente se todos os pings forem bem-sucedidos.
    """
    for source in net.hosts:
        for dest in net.hosts:
            if source == dest:
                continue

            # Usa um ping com timeout curto para a verificação
            result = source.cmd(f'ping -c 1 -W 1 {dest.IP()}')

            # Se o ping falhar, informa qual foi e retorna False imediatamente
            if '1 received' not in result:
                return False

    # Se todos os pings do loop foram bem-sucedidos
    print("*** Conectividade total confirmada!")
    return True

def qos_metric(pc1, pc2):
    print("\n*** Realizando teste de desempenho (QoS) com iperf...")

    # Inicia o servidor iperf em pc2 em background
    pc2.cmd('iperf -s &')

    # Aguarda um instante para o servidor iniciar
    time.sleep(1)

    # Executa o cliente iperf em pc1 e captura a saída
    iperf_result = pc1.cmd(f'iperf -c {pc2.IP()} -y C -t 10')

    parts = iperf_result.strip().split(',')
    # Extrai as métricas do formato CSV do iperf para TCP
    interval = parts[6]
    bytes_transferred = int(parts[7])
    bandwidth_bps = float(parts[8])

    megabits_divisor = 1_000_000
    mebibytes_divisor = 1024 * 1024

    # Cria a string formatada para o log (sem jitter/loss)
    formatted_result = (
        f"\n"
        f"    Duração: {interval}sec\n"
        f"    Vazão: {bandwidth_bps / megabits_divisor:.2f} Mbits/sec\n"
        f"    Dados Transferidos: {bytes_transferred / mebibytes_divisor:.2f} MBytes\n"
    )
    print(f"--- METRIC_QOS_START ---\n{formatted_result}\n--- METRIC_QOS_END ---")
    
    # Para o servidor iperf em pc2
    pc2.cmd('kill %iperf')

def routing_table_metric(routers):
    """
    Mede o tamanho da tabela de roteamento de cada roteador e exibe um resumo.
    """
    print("\n*** Coletando métricas de tabela de roteamento...")

    total_routes = 0
    routing_table_details = ""
    for r in routers:
        # O comando 'ip route' lista as rotas, e 'wc -l' conta as linhas.
        route_count_str = r.cmd('ip route | grep -e "link" -e "via" | wc -l').strip()
        
        route_count = int(route_count_str)
        total_routes += route_count
        routing_table_details += f"    - Roteador {r.name}: {route_count} rotas\n"

    # Cria a string formatada para o log
    formatted_result = (
        f"\n"
        f"{routing_table_details}"
        f"    - Total na rede: {total_routes} rotas\n"
    )
    print(f"--- METRIC_ROUTING_TABLE_START ---\n{formatted_result}\n--- METRIC_ROUTING_TABLE_END ---")

def path_analysis_metric(pc1, pc2):
    """
    Executa um traceroute para visualizar o caminho entre dois hosts.
    """
    print("\n*** Analisando a rota de pc1 para pc2 com traceroute...")
    
    # O '-n' evita a resolução de nomes, tornando o comando mais rápido.
    traceroute_output = pc1.cmd(f'traceroute -n {pc2.IP()}')
    
    formatted_result = f"\n{traceroute_output}\n"
    
    print(f"--- METRIC_PATH_ANALYSIS_START ---\n{formatted_result}\n--- METRIC_PATH_ANALYSIS_END ---")

def quagga_overhead_metric(routers, start_time):
    """
    Analisa os logs do Quagga OSPF para resumir o overhead do protocolo.
    """
    print("\n*** Analisando o overhead do protocolo (Quagga OSPF)...")
    
    lsa_originations = 0

    for r in routers:
        # Aponta para o nome do arquivo de log do Quagga
        log_file = f"/tmp/{r.name}-ospfd.log"
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    # Procura pela string que indica a criação de um novo LSA
                    if "scheduling new router-LSA origination" in line:
                        lsa_originations += 1
        except FileNotFoundError:
            print(f"    - AVISO: Arquivo de log {log_file} não encontrado.")

    end_time = time.time()
    time_spent = end_time - start_time

    # Formata o resultado, indicando que os HELLOs não podem ser contados a partir deste log
    formatted_result = (
        f"\n"
        f"      Tempo total: {time_spent:.2f}\n"
        f"      Total gerado de LSA: {lsa_originations}\n"
        f"      Total gerado de HELLO: Não contável pelos logs disponibilizados pelo Quagga\n"
    )
    print(f"--- METRIC_PROTOCOL_OVERHEAD_START ---\n{formatted_result}\n--- METRIC_PROTOCOL_OVERHEAD_END ---")

if __name__ == "__main__":
    setLogLevel("info")
    start_network()