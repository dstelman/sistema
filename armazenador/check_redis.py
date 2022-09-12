import os
import redis
from flask import Flask, redirect, request
import requests
import logging
import time

app = Flask(__name__)

conn = redis.Redis('127.0.0.1')

def redis_consult(ip):
	#Querying the IP in the status
    return conn.get(ip)

def redis_insert(ip, id_control):
    tempo = time.time()
    conn.set("%s" % ip, "1_%s" % id_control)
    return "ok"

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

lista_app = ["x", "192.168.0.70", "192.168.0.200", "x", "192.168.0.201", "192.168.0.202","192.168.0.203","192.168.0.204", "192.168.0.205"]

lista_controladores_vpn = ["x", "192.168.56.102", "192.168.56.106", "x", "192.168.56.108", "192.168.56.109", "192.168.56.117", "192.168.56.121", "192.168.56.119"]

# receives the information from the application web and updates the desired ovs with a definitive flow.
@app.route('/<ip>')
def start(ip):
    resultado = redis_consult(ip)
    id_control = resultado.split("_")[1]    
    doc = redis_insert(ip, id_control)
    data_ok["dpid"] = int(id_control)
    data_ok["match"]["nw_src"] = ip
    data_ok["match"]["nw_dst"] = lista_app[int(id_control)]
    req = requests.post('http://%s:8080/stats/flowentry/add' % lista_controladores_vpn[int(id_control)], json=data_ok)
    if req.status_code == 200:
        return "fim"
    else:
        return "fluxo para %s nao atualizado." % s
            

if __name__ == '__main__':
	logging.basicConfig(filename='redir.log', level=logging.DEBUG)
	port = int(os.environ.get('PORT', 80))
	app.run(host='0.0.0.0', port=port, debug=True)
