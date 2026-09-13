#####################################################
#                                                   #
# Título do trabalho: Trabalho de Sockets           #
#         Disciplina: Redes de Computadores PPComp  #
#                                                   #
#####################################################

# SERVIDOR
from Config import *
from GeneralControl import *
from DeviceThread import *
from os.path import exists
import socket
import threading
import queue

# Carrega uma tabela em formato texto e retorna em forma de lista
def LoadTable(fileName):
	print('----------------------------------------------')
	print('Carregando tabela do sistema: ' + fileName)
	print('----------------------------------------------')
	result = []
	if not exists(fileName):
		print('Arquivo não encontrado na pasta')
		exit()
	else:
		FILE = open(fileName, 'r', encoding='UTF-8')
		for line in FILE:
			line = line.strip()
			if line[:1] != '#':
				if fileName == ARQUIVO_AMBIENTES:
					roomID, roomName = line.split(',')
					print(roomID, roomName)
					result.append( { 'roomID': roomID, 'roomName': roomName} )
				elif fileName == ARQUIVO_TIPOS_DISPOSITIVOS:
					typeID, typeCode, typeName = line.split(',')
					print(typeID, typeName)
					result.append( { 'typeID': typeID, 'typeCode': typeCode, 'typeName': typeName} )
	print('----------------------------------------------\n')
	return result

####################
# Inicializando... #
####################
if __name__ == '__main__':
	print('Inicializando o servidor')

	print('Carregando tabelas...')

	# Carregar a lista de ambientes da casa (ID e Nome)
	roomsList = LoadTable(ARQUIVO_AMBIENTES)

	# Carregar a lista de dispositivos suportados (ID e Nome)
	typesList = LoadTable(ARQUIVO_TIPOS_DISPOSITIVOS)

	# Colocando a porta em LISTEN
	tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	tcp.bind((SERVIDOR, PORTA))
	tcp.listen(1)

	# Iniciando o controle geral
	print('Iniciando o controle.')
	controlQueue = queue.Queue()
	# Iniciando a thread de controle
	threading.Thread(target=GeneralControl, args=(controlQueue, roomsList, typesList)).start()
	print('+--------------------------------------------+')
	print('|  Trabalho 01 - Sockets                     |')
	print('|  Disciplina: Redes de Computadores PPComp  |')
	print('+--------------------------------------------+')
	print('Servidor inicializado.')
	print('Aguardando conexões dos dispositivos...')
	try:
		while True:
			# Aceita a conexão
			connection, clientIP = tcp.accept()
			print('Cliente conectado:', clientIP)
			# Inicia uma thread para atender o dispositivo
			threading.Thread(target=DeviceThread, args=(connection, clientIP, controlQueue,)).start()
	except KeyboardInterrupt:
		print('Finalizando servidor...')
		# finalizando
		tcp.close()
		pass
	finally:
		# finalizando
		tcp.close()
	print('Servidor desligado')
