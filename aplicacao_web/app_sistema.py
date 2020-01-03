from flask import Flask, redirect, request
import requests
import os
import logging
import random

app = Flask(__name__)

@app.route('/')
def hello():
    # caso seja necessario testar a aplicacao sem a comunicacao com o armazenador (sem sistema), basta comentar as linhas 12 e 13.
	ip = request.args.get('client')
	out = requests.get("http://192.168.0.6/%s" % ip)
    # A funcao random foi utilizada para evitar algum tipo de cache do sistema. Toda requisicao recebera uma resposta diferente porem com o mesmo tamanho.
	valor = random.randrange(100000,1100000)
	return (9000 * ("%s" % valor))

if __name__ == '__main__':
    logging.basicConfig(filename='app.log', level=logging.DEBUG)
    port = int(os.environ.get('PORT', 80)) 
    app.run(host='0.0.0.0', port=port, debug=True)

