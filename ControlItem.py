#####################################################
#                                                   #
# Título do trabalho: Trabalho de Sockets           #
#         Disciplina: Redes de Computadores PPComp  #
#                                                   #
#####################################################

from Config import *
import queue

# Dicionário com os ambientes catalogados
global roomDict
roomDict = {}
# Dicionário com os tipos catalogados
global typeDict
typeDict = {}


# Objeto que mantém os dados de um ambiente
class RoomItem():
	roomID = ''    # ID do ambiente
	roomName = ''  # Nome do ambiente
	lampQueueList = {}
	#runningStatus = False  # Possui thread monitorando?
	#thread = None          # Objeto da thread
	#eventObject = None     # Objeto de evento para cancelar o timeout

	# Inicializa com ID e Nome do ambiente
	def __init__(self, roomID, roomName):
		self.roomID = roomID
		self.roomName = roomName
		self.lampQueueList = {}
		self.fanQueueList = {}
		self.currentTemperature = 0.0
		self.currentPresence = PRESENCA_NAO_DETECTADA

	# Gerar a lista de lâmpadas do ambiente em formato texto
	def LampListToString(self):
		deviceList = []
		for deviceID in self.lampQueueList.keys():
			deviceList.append(f'{deviceID}')
		return ', '.join(deviceList)

	# Lista de lâmpadas do ambiente
	def toString(self):
		if len(self.lampQueueList) > 0:
			threadList = 'Lâmpadas> ' + self.LampListToString()
			return f'[{self.roomID}] {self.roomName} => {threadList}'
		return None

	# Incluir nova lâmpada na lista
	def AddLamp(self, deviceID, lampQueue):
		print(f'Adicionando a lâmpada ID={deviceID} no ambiente {self.roomName}')
		self.lampQueueList.update({deviceID: lampQueue})

	# Remover uma lâmpada da lista
	def DelLamp(self, deviceID):
		print(f'Removendo a lâmpada ID={deviceID} do ambiente {self.roomName}')
		self.lampQueueList.pop(deviceID)
		return len(self.lampQueueList)

	# Se um sensor foi acionado, interrompe o timeout
	def Sensor(self, command):
		for deviceID, lampQueue in self.lampQueueList.items():
			lampQueue.put(int(command))

	def AddFan(self, deviceID, fanQueue):
		print(f'Adicionando ventilador ID={deviceID} no ambiente {self.roomName}')
		self.fanQueueList.update({deviceID: fanQueue})

	def DelFan(self, deviceID):
		print(f'Removendo ventilador ID={deviceID} do ambiente {self.roomName}')
		if deviceID in self.fanQueueList:
			self.fanQueueList.pop(deviceID)

	def CheckFan(self):
		if self.currentPresence == PRESENCA_DETECTADA and self.currentTemperature > 25.0:
			speed = VENTILADOR_VELOCIDADE_1
			if self.currentTemperature > 30.0:
				speed = VENTILADOR_VELOCIDADE_3
			elif self.currentTemperature > 27.0:
				speed = VENTILADOR_VELOCIDADE_2
			for deviceID, fanQueue in self.fanQueueList.items():
				fanQueue.put(speed)
		else:
			for deviceID, fanQueue in self.fanQueueList.items():
				fanQueue.put(VENTILADOR_DESLIGADO)


# Objeto contendo os tipos catalogados
class TypeItem():
	typeID = ''    # ID do tipo
	typeCode = ''  # Código do tipo 'L' Lâmpada, 'S' Sensor de presença e 'T' Temperatura
	typeName = ''  # Nome do dispositivo

	def __init__(self, typeID, typeCode, typeName):
		self.typeID = typeID
		self.typeCode = typeCode
		self.typeName = typeName

# Formato da mensagem enviada pela fila para o controle geral
class MonitorItem():
	deviceID = None			# ID do dispositivo
	deviceTypeCode = None	# Código 'L' Lâmpada ou 'S' Sensor de Presença
	roomID = None			# ID do ambiente
	command = None			# Comando
							# Lâmpada:
							#	INCLUIR_LAMPADA / EXCLUIR_LAMPADA
							# Sensor de presença:
							#	PRESENCA_NAO_DETECTADA / PRESENCA_DETECTADA
	lampQueue = None		# Fila para comunicação com a lâmpada

	def __init__(self, deviceID, deviceTypeCode, roomID, command, lampQueue):
		self.deviceID = deviceID
		self.deviceTypeCode = deviceTypeCode
		self.roomID = roomID
		self.command = command
		self.lampQueue = lampQueue

# Incluir um tipo no dicionário
def AddTypeItem(typeItem):
	global typeDict
	typeDict.update({ f'{typeItem.typeID}': typeItem})

# Obter um objeto de tipo pelo ID
def GetTypeItem(typeID):
	global typeDict
	if typeID in typeDict:
		return typeDict[typeID]
	return None

# Obter todo o dicionário de tipos
def GetTypeDict():
	global typeDict
	return typeDict

# Incluir um ambiente no dicionário
def AddRoomItem(roomItem):
	global roomDict
	roomDict.update({ f'{roomItem.roomID}': roomItem})

# Obter um objeto de ambiente pelo ID
def GetRoomItem(roomID):
	global roomDict
	if roomID in roomDict:
		return roomDict[roomID]
	return None

# Obter todo o dicionário de ambientes
def GetRoomDict():
	global roomDict
	return roomDict
