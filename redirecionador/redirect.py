import os
import redis
from flask import Flask, redirect, request
import requests
import logging
import time

app = Flask(__name__)

#conexão com o armazenador
conn = redis.Redis('192.168.56.105')

def redis_consult(ip):
	#consultando o IP no status
    return conn.get(ip)

def redis_insert(ip, dicionario):
    conn.set("%s" % ip, "0_%s_%s" % (dicionario["id"], time.time()))
    return "ok"

count = {"control":0}
# data_ok e data_nok sao diferentes no hard_timeout. O data_nok deixa o fluxo na tabela por 60 segundos. Pode ser utilizado em um futuro para a aplicacao de Threat Intelligence no sistema.
# o hard_timeout pode ser variavel dependendo do peso do IP em funcao de requisições pregressas.
# nesse trabalho e utilizado para caso o fluxo nao seja confirmado pela aplicacao web, o mesmo some sozinho da tabela sem a necessidade de remocao pelo sistema posteriormente.
data_ok = {
    "dpid":"",
    "cookie":1,
    "table_id":0,
    "idle_timeout":0,
    "hard_timeout":0,
    "priority":65000,
    "flags":0,
    "match": {"nw_src":"", "nw_dst":"", "dl_type":2048},
    "actions":[{"type":"OUTPUT", "port":"normal"}]
}

data_nok = {
    "dpid":"",
    "cookie":1,
    "table_id":0,
    "idle_timeout":0,
    "hard_timeout":60,
    "priority":65000,
    "flags":0,
    "match": {"nw_src":"", "nw_dst":"", "dl_type":2048},
    "actions":[{"type":"OUTPUT", "port":"normal"}]
}

#lista com os ips das aplicacoes dos outros ASs e do sistema local
lista_app = ["x", "192.168.0.70", "192.168.0.200", "x", "192.168.0.201", "192.168.0.202","192.168.0.203","192.168.0.204", "192.168.0.205"]
#lista com os ips dos controladores de cada AS e do SL
lista_controladores_vpn = ["x", "192.168.56.102", "192.168.56.106", "x", "192.168.56.108", "192.168.56.109", "192.168.56.117", "192.168.56.121", "192.168.56.119"]

@app.route('/')
def start():
    ip = request.remote_addr
    resultado = redis_consult(ip)
    if resultado == None:
        dicionario = {"id":"", "ip_app":""}
        if count["control"] == 0:
            dicionario= {"id":1, "ip_app":"192.168.0.70"}
            # para simular com o sistema sem colaboracao basta fixar count["control"] = 0
            count["control"] = 1
        elif count["control"] == 1:
            dicionario = {"id":2, "ip_app":"192.168.0.200"}
            count["control"] = 2
        elif count["control"] == 2:
            dicionario = {"id":4, "ip_app":"192.168.0.201"}
            count["control"] = 3
        elif count["control"] == 3:
            dicionario = {"id":5, "ip_app":"192.168.0.202"}
            count["control"] = 4
        elif count["control"] == 4:
            dicionario = {"id":6, "ip_app":"192.168.0.203"}
            count["control"] = 5
        elif count["control"] == 5:
            dicionario = {"id":7, "ip_app":"192.168.0.204"}
            count["control"] = 6
        else:
            dicionario = {"id":8, "ip_app":"192.168.0.205"}
            count["control"] = 0
        doc = redis_insert(ip, dicionario)
        data_nok["dpid"] = dicionario["id"]
        data_nok["match"]["nw_src"] = ip
        data_nok["match"]["nw_dst"] = lista_app[dicionario["id"]]
        req = requests.post('http://%s:8080/stats/flowentry/add' % lista_controladores_vpn[dicionario["id"]], json=data_nok)
        if req.status_code == 200:
            return redirect("http://%s/?client=%s" % (lista_app[dicionario["id"]],ip), code=302)
    else:
	if resultado != "2":
        	return redirect("http://%s/?client=%s" % (lista_app[int(resultado.split("_")[1])], ip), code=302)
    return "fim"
            

if __name__ == '__main__':
	logging.basicConfig(filename='redir.log', level=logging.DEBUG)
	port = int(os.environ.get('PORT', 80))
	app.run(host='0.0.0.0', port=port, debug=True)
