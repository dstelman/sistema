import requests
import psutil
import time

arquivo = open('dados.txt', 'w')
tempo = time.time()

def ttt(t):
	return t - tempo

while True:
	print ttt(time.time())
	arquivo.writelines("%s %s\n" % (psutil.cpu_percent(interval=1), ttt(time.time())))

