#####################################################
#													#
# Título do trabalho: Trabalho de Sockets			#
#		  Disciplina: Redes de Computadores PPComp	#
#													#
#####################################################

from Config import *
from Message import *
from ClientUtil import *
import socket

deviceID = None

####################
# Inicializando... #
####################
if __name__ == '__main__':
	print('Inicializando cliente: Lâmpada...')
	try:
		connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		destination = (SERVIDOR, PORTA)
		connection.connect(destination)
	except:
		print(f'Falha ao tentar se conectar com o servidor {SERVIDOR} porta {PORTA}')
		exit()
	device = Device(connection, NUM_LAMPADA)
	roomDict = ClientRegister(device)
	if roomDict != None:
		deviceID, roomID, roomName = SelectRoom(device, roomDict)
		if deviceID != None:
			while True:
				print(f'\n==> Ambiente [{roomID}] {roomName}')
				msg = ReceiveMessage(connection, device)
				if(msg.code == MSG_LAMPADA):
					print('Acionamento recebido do servidor!!!')
					print('#####################################')
					if msg.action == LUZ_ACESA:
						print('            LAMPADA LIGADA')
					elif msg.action == LUZ_APAGADA:
						print('           LAMPADA DESLIGADA')
					else:
						print(f'Ação inválida: {msg.action}')
					print('#####################################')
					msg = MessageStatus()
					connection.send(msg.pack(deviceID, ACAO_EXECUTADA))					
				else:
					print('Mensagem inválida code:', msg.code)
		connection.close()
