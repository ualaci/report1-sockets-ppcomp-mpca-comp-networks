#####################################################
#                                                   #
# Título do trabalho: Trabalho de Sockets           #
#         Disciplina: Redes de Computadores PPComp  #
#                                                   #
#####################################################

from Config import *
from ControlItem import *
import queue
import threading

def GeneralControl(controlQueue, roomsList, typesList):
	# Dicionário contendo todos os ambientes cadastrados
	# Usamos a lista de ambientes que foi carregada do arquivo de configuração para popular o nosso dicionário de objetos com informações dos ambientes
	for item in roomsList:
		roomID = item['roomID']
		roomName = item['roomName']
		AddRoomItem(RoomItem(roomID, roomName))
	# Dicionário com os tipos carregados da tabela de configuração
	for item in typesList:
		typeID = item['typeID']
		typeCode = item['typeCode']
		typeName = item['typeName']
		AddTypeItem(TypeItem(typeID, typeCode, typeName))
	while True:
		# Aguarda a chegada de um comando na fila
		monitorItem = controlQueue.get()
		print(f'Comando chegando na fila do controle do ambiente {monitorItem.roomID}')
		roomItem = GetRoomItem(monitorItem.roomID)
		# Se encontrou o ambiente na lista, executa o comando
		if roomItem != None:
			# Atende o comando de acordo com o tipo de dispositivo
			# LAMPADA <- Registrar ou desregistrar no sistema
			if monitorItem.deviceTypeCode == COD_LAMPADA:
				# Registrar a lâmpada
				if monitorItem.command == INCLUIR_LAMPADA:
					# Registra a nova lâmpada
					roomItem.AddLamp(monitorItem.deviceID, monitorItem.lampQueue)
				# Desregistrar a lâmpada
				if monitorItem.command == EXCLUIR_LAMPADA:
					# Remove a lâmpada do registro
					roomItem.DelLamp(monitorItem.deviceID)
			# SENSOR DE PRESENÇA <- Indica que o sinal foi recebido, acionar as lâmpadas
			if monitorItem.deviceTypeCode == COD_SENSOR_PRESENCA:
				# envia o comando para apagar
				roomItem.Sensor(monitorItem.command)
		lst = '------------------------------------------------------\n'
		for roomID, roomItem in GetRoomDict().items():
			roomLampList = roomItem.toString()
			if roomLampList != None:
				lst = lst + roomLampList + '\n'
		lst = lst + '------------------------------------------------------\n'
		print(lst)
