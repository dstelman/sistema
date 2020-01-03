import os
import redis
from flask import Flask, redirect, request
import requests
import logging
import time

# o redis esta instalado localmente
conn = redis.Redis('127.0.0.1')

lista_app = ["x", "192.168.0.70", "192.168.0.200", "x", "192.168.0.201", "192.168.0.202","192.168.0.203","192.168.0.204", "192.168.0.205"]

lista_controladores_vpn = ["x", "192.168.56.102", "192.168.56.106", "x", "192.168.56.108", "192.168.56.109", "192.168.56.117", "192.168.56.121", "192.168.56.119"]

data_block = {
    "dpid": 1,
    "cookie": 1,
    "table_id": 0,
    "idle_timeout": 0,
    "hard_timeout": 0,
    "priority": 65200,
    "flags": 0,
    "match": {"nw_src":"", "nw_dst":"", "dl_type":2048},
    "actions":[]
}

data_delete = {
    "dpid": 1,
    "cookie": 1,
    "table_id": 0,
    "idle_timeout": 0,
    "hard_timeout": 0,
    "priority": 65000,
    "flags": 0,
    "match": {"nw_src":"", "nw_dst":"", "dl_type":2048},
    "actions":[]
}

def deleta_fluxo(ip, ctrl):
    data_delete["match"]["nw_src"] = ip
    ctrl_id = ctrl.split("_")[1]
    data_delete["dpid"] = int(ctrl_id)
    data_delete["match"]["nw_dst"] = lista_app[int(ctrl_id)]
    req = requests.post('http://%s:8080/stats/flowentry/delete_strict' % lista_controladores_vpn[int(ctrl_id)], json=data_delete)
    return "OK"
    
def bloqueia_em_todos(ip):
    data_block["match"]["nw_src"] = ip
    # esse for controla quantos controladores sao usados. Utilizado apenas para bloquear o acesso para o ovs de entrada. Os outros OVSs apenas nao terao o fluxo por conta do hard_timeout = 60 sem confirmacao.
    # funcao ja preparada para trabalhar com todos os ovs caso necessario.
    for x in [1]:
        if x == 1:
            data_block["match"]["nw_dst"] = "192.168.0.58"
            req = requests.post('http://%s:8080/stats/flowentry/add' % lista_controladores_vpn[x]  , json=data_block)
            data_block["match"]["nw_dst"] = lista_app[x]
            req = requests.post('http://%s:8080/stats/flowentry/add' % lista_controladores_vpn[x]  , json=data_block)
        else:
            data_block["dpid"] = x
            data_block["match"]["nw_dst"] = lista_app[x]
            req = requests.post('http://%s:8080/stats/flowentry/add' % lista_controladores_vpn[x]  , json=data_block)
    return "OK"

while True:
    #os registros morrem em 30 segundos no redis.
    time.sleep(10)
    keys = conn.keys()
    values = conn.mget(keys)
    kv = zip(keys, values)
    for x in kv:
        tempo = int(time.time())
        if len(x[1].split("_")) == 3:
	    old = str(x[1].split("_")[2])
            delta = tempo - float(old) 
            if delta > 20:
                #deletando no controlador escrito previamente
                out = deleta_fluxo(x[0],x[1])
                conn.set(x[0],'2') # Ja alterando o status
                #bloqueando em todos os controladores
                out = bloqueia_em_todos(x[0])
        else:
            continue
