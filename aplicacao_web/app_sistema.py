from flask import Flask, redirect, request
import requests
import os
import logging
import random

app = Flask(__name__)

@app.route('/')
def hello():
    # If it is necessary to test the application without communicating with the store (without the system), just comment on lines 12 and 13.
	ip = request.args.get('client')
	out = requests.get("http://192.168.0.6/%s" % ip)
    # The random function was used to avoid some kind of system cache. Every request will receive a different response but with the same size.
	valor = random.randrange(100000,1100000)
	return (9000 * ("%s" % valor))

if __name__ == '__main__':
    logging.basicConfig(filename='app.log', level=logging.DEBUG)
    port = int(os.environ.get('PORT', 80)) 
    app.run(host='0.0.0.0', port=port, debug=True)

