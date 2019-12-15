#!usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController, OVSSwitch
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf, Link
from subprocess import call
import os

def myNetwork():

    net = Mininet( topo=None, build=False, ipBase='10.0.0.0/8', link=TCLink)

    info( '*** Adding controller\n' )
    c1=net.addController(name='c1', controller=RemoteController, ip='192.168.56.102', protocol='tcp', port=6633)
    c2=net.addController(name='c2', controller=RemoteController, ip='192.168.56.106', protocol='tcp', port=6633)
    c3=net.addController(name='c3', controller=RemoteController, ip='192.168.56.107', protocol='tcp', port=6633)    
    c4=net.addController(name='c4', controller=RemoteController, ip='192.168.56.108', protocol='tcp', port=6633)
    c5=net.addController(name='c5', controller=RemoteController, ip='192.168.56.109', protocol='tcp', port=6633)

    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch)    
    s4 = net.addSwitch('s4', cls=OVSKernelSwitch)
    s5 = net.addSwitch('s5', cls=OVSKernelSwitch)

    info( '*** Add hosts\n')
    h1 = net.addHost('h1', ip='192.168.0.200', mac='00:00:00:00:00:01')
    h3 = net.addHost('h3', ip='192.168.0.201', mac='00:00:00:00:00:03')
    h4 = net.addHost('h4', ip='192.168.0.202', mac='00:00:00:00:00:04')

    for x in range(5,51):
	if x >= 10:
		exec("h%s = net.addHost('h%s', ip='0.0.0.0', mac='00:00:00:00:00:%s')" % (x,x,x))
	else:
		exec("h%s = net.addHost('h%s', ip='0.0.0.0', mac='00:00:00:00:00:0%s')" % (x,x,x))
	exec("h%s.cmd('sysctl -w net.ipv4.ip_forward=1')" % x)
    
    info( '*** Add links\in')
    Link(h1, s2, intfName1='h1-eth0')
    exec("net.addLink(s3, h1, bw=100, delay='1ms', loss=0, use_htb=True)")
    h1.cmd('ifconfig h1-eth1 0.0.0.0 netmask 0.0.0.0.0')
    h1.cmd('iptables -t nat -A PREROUTING -d 192.168.0.200 -j DNAT --to-destination 10.0.0.5')
    h1.cmd('iptables -t nat -A POSTROUTING -o h1-eth1 -j SNAT --to-source 10.0.0.82')
    h1.cmd('sysctl -w net.ipv4.ip_forward=1')

    Link(h3, s4, intfName1='h3-eth0')
    exec("net.addLink(s3, h3, bw=100, delay='1ms', loss=0, use_htb=True)")    
    h3.cmd('ifconfig h3-eth1 0.0.0.0 netmask 0.0.0.0')
    h3.cmd('iptables -t nat -A PREROUTING -d 192.168.0.201 -j DNAT --to-destination 10.0.0.5')
    h3.cmd('iptables -t nat -A POSTROUTING -o h3-eth1 -j SNAT --to-source 10.0.0.83')
    h3.cmd('sysctl -w net.ipv4.ip_forward=1')

    Link(h4, s5, intfName1='h4-eth0')
    exec("net.addLink(s3, h4, bw=100, delay='1ms', loss=0, use_htb=True)")
    h4.cmd('ifconfig h4-eth1 0.0.0.0 netmask 0.0.0.0')
    h4.cmd('iptables -t nat -A PREROUTING -d 192.168.0.202 -j DNAT --to-destination 10.0.0.5')
    h4.cmd('iptables -t nat -A POSTROUTING -o h4-eth1 -j SNAT --to-source 10.0.0.84')
    h4.cmd('sysctl -w net.ipv4.ip_forward=1')

    net.addLink(s1, s2)
    net.addLink(s1, s4)
    net.addLink(s1, s5)
    net.addLink(s1, s3)

    for x in range(5,51):
	exec("net.addLink(s1, h%s, bw=100, delay='1ms', loss=0, use_htb=True)" % x)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s1').start([c1])
    net.get('s2').start([c2])    
    net.get('s3').start([c3])
    net.get('s4').start([c4])
    net.get('s5').start([c5])
   
    info( '*** Post configure switches and hosts\n')
    os.popen('ovs-vsctl add-port s3 enp0s10')
    exec("h1.cmdPrint('dhclient h1-eth1')")
    exec("h3.cmdPrint('dhclient h3-eth1')")
    exec("h4.cmdPrint('dhclient h4-eth1')")
    
    h1.cmd("ifconfig h1-eth1 10.0.0.82")
    h3.cmd("ifconfig h3-eht1 10.0.0.83")
    h4.cmd("ifconfig h4-eth1 10.0.0.84")

    os.popen('ovs-vsctl add-port s1 enp0s9')
    for x in range(5,51):
	exec("h%s.cmdPrint('dhclient '+h%s.defaultIntf().name)" % (x,x))
    
    s1.cmd('ovs-ofctl add-flow s1 ip,priority=65000,nw_src=192.168.0.58/32,actions=NORMAL')
    s1.cmd('ovs-ofctl add-flow s1 ip,priority=65000,nw_dst=192.168.0.58/32,actions=NORMAL')
    #Esses fluxos permissivos sao para simular a internet. O cara chega no h1 mas s2 que dira se passa ou nao.
    s1.cmd('ovs-ofctl add-flow s1 ip,priority=65000,nw_dst=192.168.0.200/32,actions=NORMAL')
    s1.cmd('ovs-ofctl add-flow s1 ip,priority=65000,nw_src=192.168.0.200/32,actions=NORMAL')
    s1.cmd('ovs-ofctl add-flow s1 ip,priority=65000,nw_src=192.168.0.201/32,actions=NORMAL')
    s1.cmd('ovs-ofctl add-flow s1 ip,priority=65000,nw_dst=192.168.0.201/32,actions=NORMAL')
    s1.cmd('ovs-ofctl add-flow s1 ip,priority=65000,nw_src=192.168.0.202/32,actions=NORMAL')
    s1.cmd('ovs-ofctl add-flow s1 ip,priority=65000,nw_dst=192.168.0.202/32,actions=NORMAL')
    # Fluxo para a app falar com o banco
    s1.cmd('ovs-ofctl add-flow s1 ip,priority=65000,nw_src=192.168.0.70/32,nw_dst=192.168.0.6/32,actions=NORMAL')
    s1.cmd('ovs-ofctl add-flow s1 ip,priority=65000,nw_src=192.168.0.6/32,nw_dst=192.168.0.70/32,actions=NORMAL')
    #Fluxo para resposta da Aplicacao web
    s1.cmd('ovs-ofctl add-flow s1 ip,priority=65000,nw_src=192.168.0.70/32,actions=NORMAL')
    s1.cmd('ovs-ofctl add-flow s1 arp,priority=1000,actions=NORMAL')
    s1.cmd('ovs-ofctl add-flow s1 ip,priority=100,actions=DROP')
    ### S2
    s2.cmd('ovs-ofctl add-flow s2 arp,priority=1000,actions=NORMAL')
    s2.cmd('ovs-ofctl add-flow s2 ip,priority=65000,nw_src=192.168.0.58/32,actions=NORMAL')
    s2.cmd('ovs-ofctl add-flow s2 ip,priority=65000,nw_dst=192.168.0.58/32,actions=NORMAL')
    s2.cmd('ovs-ofctl add-flow s2 ip,priority=65000,nw_src=192.168.0.200/32,actions=NORMAL')
    s2.cmd('ovs-ofctl add-flow s2 ip,priority=100,actions=DROP')
    ###S3
    s3.cmd('ovs-ofctl add-flow s3 ip,priority=65000,nw_src=10.0.0.0/24,nw_dst=10.0.0.0/24,actions=NORMAL')
    s3.cmd('ovs-ofctl add-flow s3 arp,priority=1000,actions=NORMAL')
    s3.cmd('ovs-ofctl add-flow s3 ip,priority=100,actions=DROP')
    ####S4
    s4.cmd('ovs-ofctl add-flow s4 ip,priority=65000,nw_src=192.168.0.58/32,actions=NORMAL')
    s4.cmd('ovs-ofctl add-flow s4 ip,priority=65000,nw_dst=192.168.0.58/32,actions=NORMAL')
    s4.cmd('ovs-ofctl add-flow s4 ip,priority=65000,nw_src=192.168.0.201/32,actions=NORMAL')
    s4.cmd('ovs-ofctl add-flow s4 arp,priority=1000,actions=NORMAL')
    s4.cmd('ovs-ofctl add-flow s4 ip,priority=100,actions=DROP')
    ###S5
    s5.cmd('ovs-ofctl add-flow s5 ip,priority=65000,nw_src=192.168.0.58/32,actions=NORMAL')
    s5.cmd('ovs-ofctl add-flow s5 ip,priority=65000,nw_dst=192.168.0.58/32,actions=NORMAL')
    s5.cmd('ovs-ofctl add-flow s5 ip,priority=65000,nw_src=192.168.0.202/32,actions=NORMAL')
    s5.cmd('ovs-ofctl add-flow s5 arp,priority=1000,actions=NORMAL')
    s5.cmd('ovs-ofctl add-flow s5 ip,priority=100,actions=DROP')
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()


