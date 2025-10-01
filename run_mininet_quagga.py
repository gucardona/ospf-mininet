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
        r.cmd(f'/usr/lib/quagga/zebra -d -f {config_dir}/zebra.conf -z /tmp/zebra_{r.name}.api -i /tmp/zebra_{r.name}.pid')
        time.sleep(1)

        # Inicia o daemon OSPF
        r.cmd(f'/usr/lib/quagga/ospfd -d -f {config_dir}/ospfd.conf -z /tmp/zebra_{r.name}.api -i /tmp/ospfd_{r.name}.pid')

    print("\n*** Rede pronta com Quagga OSPF. Daemons estão convergindo.")
    print("*** Verifique /tmp/rX-*.log nos roteadores para a saída dos daemons.")
    print("*** Use a CLI. Tente 'pc1 ping pc2' ou 'pingall' após ~30 segundos.")
    CLI(net)

    print("*** Parando os daemons Quagga")
    for r in routers:
        r.cmd("killall zebra")
        r.cmd("killall ospfd")

    net.stop()

if __name__ == "__main__":
    setLogLevel("info")
    start_network()