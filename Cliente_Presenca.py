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
	print('Inicializando cliente: Sensor de Presença...')
	try:
		connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		destination = (SERVIDOR, PORTA)
		connection.connect(destination)
	except:
		print(f'Falha ao tentar se conectar com o servidor {SERVIDOR} porta {PORTA}')
		exit()
	device = Device(connection, NUM_SENSOR_PRESENCA)
	roomDict = ClientRegister(device)
	if roomDict != None:
		deviceID, roomID, roomName = SelectRoom(device, roomDict)
		if deviceID != None:
			while True:
				print(f'\n==> Ambiente [{roomID}] {roomName}')
				print('Para sair use CTRL+X')
				print('0) para indicar que o sensor não detectou ninguém')
				print('1) para indicar uma presença detectada')
				sensorValue = input('Selecione:')
				if sensorValue == '\x18': break
				msg = MessageSensor()
				if sensorValue == '0' or sensorValue == '1':
					print(f'Meu ID={deviceID}')
					if sensorValue == '0':
						print('Status: Presença não detectada')
						connection.send(msg.pack(deviceID, PRESENCA_NAO_DETECTADA))
					if sensorValue == '1':
						print('Status: Presença detectada')
						connection.send(msg.pack(deviceID, PRESENCA_DETECTADA))
					print('Enviando informação ' + msg.toString())
					print('Aguardando confirmação...')
					msg = ReceiveMessage(connection, device)
					if(msg.code == MSG_STATUS and msg.status == LEITURA_RECEBIDA):
						print('Leitura recebida pelo servidor!!!')
					else:
						print(f'Falha, status = {msg.status}')
				else:
					print('Opção inválida')
		connection.close()
