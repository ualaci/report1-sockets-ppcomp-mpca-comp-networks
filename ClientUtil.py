#####################################################
#                                                   #
# Título do trabalho: Trabalho de Sockets           #
#         Disciplina: Redes de Computadores PPComp  #
#                                                   #
#####################################################

from Config import *
from Message import *
import socket

class Device():
	buffer = ''
	connection = None
	deviceType = ''
	def __init__(self, connection, deviceType):
		self.connection = connection
		self.deviceType = deviceType

def ClientRegister(device):
	msg = MessageRegister()
	device.connection.send(msg.pack(device.deviceType))
	msg = ReceiveMessage(device.connection, device)
	if msg != None and msg.code == MSG_LISTA_AMBIENTES:
		print('Dispositivo registrado')
		print('---------------------------------')
		print('Selecione o ambiente')
		for roomID, roomItem in msg.roomDict.items():
			print(f'{roomID}: {roomItem.roomName}')
		print('---------------------------------')
		return msg.roomDict
	else:
		print(msg)
		print('Falha no registro')
		return None

def SelectRoom(device, roomDict):
	roomImput = input('ID do ambiente: ')
	while True:
		try:
			roomID = int(roomImput)
			if roomID == 0:
				return False
			if f'{roomID}' in roomDict:
				break
			print('ID do ambiente inválido, selecione da lista')
			print('---------------------------------')
			for roomID, roomItem in roomDict.items():
				print(f'{roomID}: {roomItem.roomName}')
			print('---------------------------------')
			roomImput = input('ID do ambiente: ')
		except:
			print('Falha ao ler o ID do ambiente')
	roomName = roomDict[f'{roomID}'].roomName
	msg = MessageSelect()
	device.connection.send(msg.pack(roomID))
	msg = ReceiveMessage(device.connection, device)
	if msg.code == MSG_STATUS and msg.status == DISPOSITIVO_REGISTRADO:
		ID = msg.deviceID
		print(f'Dispositivo registrado: ID = {ID}')
		return ID, roomID, roomName
	print('Resposta inválida do servidor.')
	return None