#####################################################
#                                                   #
# Título do trabalho: Trabalho de Sockets           #
#         Disciplina: Redes de Computadores PPComp  #
#                                                   #
#####################################################

from Config import *
from ControlItem import *
from Device import *
from datetime import datetime
import struct
import ctypes

def unixTimeStamp():
	return datetime.timestamp(datetime.now())

#[datahora_unpacked] = struct.unpack('!d', datahora_packed)
#datahora = datetime.datetime.fromtimestamp(datahora_unpacked)	

# Estrutura compartilhada por todas as mensagens
class Message():
	code = None		# 1 byte - unsigned char 
	dateTime = None	# 8 bytes - double - Timestamp da mensagem
	subject = None	# Descrição do tipo de mensagem
	mask = ''		# Máscara usada para obter os dados da mensagem

	def __init__(self):
		self.code = 0
		self.dateTime = 0.0
		self.subject = ''
		self.mask = ''

	def size(self):
		return struct.calcsize(self.mask)

	def toString(self):
		dateTime = datetime.fromtimestamp(self.dateTime)
		dateTimeStr = dateTime.strftime("%m/%d/%Y, %H:%M:%S")
		return f"[{dateTimeStr}] {self.code}: {self.subject}, " + self.toStringMsg()

	def toStringMsg(self):
		pass

	def pack(self):
		pass

	def unpack(self):
		pass

class MessageStatus(Message):

	# Campos da mensagem
	deviceID = None	# 4 bytes - unsigned int
	status = None	# 2 bytes - unsigned short
	strStatus = [	'[1] Dispositivo foi registrado',
					'[2] Valor de leitura recebido',
					'[3] Ação executada',
					'[4] Dispositivo ainda não registrado',
					'[5] Tipo de dispositivo não suportado',
					'[6] Formato de mensagem inválida',
					'[7] Ambiente selecionado inválido',
					'[8] ID de dispositivo inválido',
					'[9] Ação não suportada',
					'[10] Mensagem não esperada',
					'[11] Falha de rede'
				]

	def __init__(self):
		self.code = MSG_STATUS
		self.mask = '!BdIH'
		self.subject = 'Status'

	def toStringMsg(self):
		if(self.deviceID != None and self.status != None):
			return f"Dispositivo: {self.deviceID}, Status: " + self.strStatus[self.status-1]
		else:
			return 'Mensagem não inicializada'

	# ! network (= big-endian)
	# B unsigned char (codigo)
	# d double (datahora)
	# I unsigned int
	# H unsigned short
	# Funcao de empacotamento de mensagem
	def pack(self, deviceID, status):
		self.dateTime = unixTimeStamp()
		self.deviceID = deviceID
		self.status = status
		return struct.pack(self.mask, self.code, self.dateTime, self.deviceID, self.status)

	def unpack(self, msg):
		code, self.dateTime, self.deviceID, self.status = struct.unpack(self.mask, msg)

class MessageRegister(Message):

	# Campos da mensagem
	deviceType = None	# 1 byte - unsigned char
						# 1 = Lâmpada
						# 2 = Sensor de Presença
						# 3 = Termômetro

	def __init__(self):
		self.code = MSG_REGISTRO
		self.mask = '!BdB'
		self.subject = 'Registro'

	def toStringMsg(self):
		if(self.deviceType != None):
			return f"Tipo de dispositivo: {self.deviceType}"
		else:
			return 'Mensagem não inicializada'

	# ! network (= big-endian)
	# B unsigned char (codigo)
	# d double (datahora)
	# B unsigned char (devTipo)
	# Funcao de empacotamento de mensagem
	def pack(self, deviceType):
		self.dateTime = unixTimeStamp()
		self.deviceType = deviceType
		return  struct.pack(self.mask, self.code, self.dateTime, self.deviceType)

	def unpack(self, msg):
		code, self.dateTime, self.deviceType = struct.unpack(self.mask, msg)

class MessageList(Message):
	# Campos da mensagem
	countRooms = None	# 2 bytes - unsigned shot
	roomDict = {}

	def __init__(self):
		self.code = MSG_LISTA_AMBIENTES
		self.mask = '!BdH'
		self.maskRoom = '!H20s'
		self.subject = 'Lista de Ambientes'

	def toStringMsg(self):
		if(self.countRooms != None):
			strRooms = '/'
			for roomID, roomItem in self.roomDict.items():
				strRooms.join(f'{roomItem.roomID}: {roomItem.roomName}/')
			return f"Ambientes: [{self.countRooms}] {strRooms}"
		else:
			return "Mensagem não inicializada"

	# ! network (= big-endian)
	# B unsigned char (codigo)
	# d double (datahora)
	# H unsigned short (numAmbientes)
	# H unsigned short (numAmbiente[1])
	# 10s string (nomeAmbiente[1]
	# ...
	# H unsigned short (numAmbiente[N])
	# 10s string (nomeAmbiente[N]
	# Funcao de empacotamento de mensagem
	def pack(self, roomDict):
		self.dateTime = unixTimeStamp()
		self.countRooms = len(roomDict)
		self.roomDict = roomDict
		size = self.size() + self.countRooms * struct.calcsize(self.maskRoom)
		listBuffer = ctypes.create_string_buffer(size)
		struct.pack_into(self.mask, listBuffer, 0, self.code, self.dateTime, self.countRooms)
		offset = self.size()
		for roomID, roomItem in roomDict.items():
			intRoomID = int(roomID)
			struct.pack_into(self.maskRoom, listBuffer, offset, intRoomID, roomItem.roomName.encode('UTF-8'))
			offset += struct.calcsize(self.maskRoom)
		return listBuffer[:]

	def unpack(self, msg):
		code, self.dateTime, self.countRooms = struct.unpack(self.mask, msg[:self.size()])
		self.roomDict = {}
		sizeItem = struct.calcsize(self.maskRoom)
		msg = msg[self.size():]
		tmp = msg[:sizeItem]
		for cont in range(self.countRooms):
			roomID, roomName = struct.unpack(self.maskRoom, tmp)
			roomName = roomName.decode('UTF-8')
			msg = msg[sizeItem:]
			tmp = msg[:sizeItem]
			roomItem = RoomItem(roomID, roomName)
			self.roomDict.update( { f'{roomID}': roomItem } )

class MessageSelect(Message):

	# Campos da mensagem
	roomID = None	# 2 bytes - unsigned short

	def __init__(self):
		self.code = MSG_SELECIONA_AMBIENTE
		self.mask = '!BdH'
		self.subject = 'Seleciona Ambiente'

	def toStringMsg(self):
		if(self.roomID != None):
			return f"Ambiente selecionado: {self.roomID}"
		else:
			return 'Mensagem não inicializada'

	# ! network (= big-endian)
	# B unsigned char (codigo)
	# d double (datahora)
	# H unsigned short (ambID)
	# Funcao de empacotamento de mensagem
	def pack(self, roomID):
		self.dateTime = unixTimeStamp()
		self.roomID = roomID
		return  struct.pack(self.mask, self.code, self.dateTime, self.roomID)

	def unpack(self, msg):
		code, self.dateTime, self.roomID = struct.unpack(self.mask, msg)

class MessageSensor(Message):

	# Campos da mensagem
	deviceID = None	# 4 bytes - unsigned int
	value = None	# 4 bytes - float

	def __init__(self):
		self.code = MSG_SENSOR
		self.mask = '!BdIf'
		self.subject = 'Leitura'

	def toStringMsg(self):
		if(self.deviceID != None and self.value != None):
			return f"Dispositivo: {self.deviceID}, Valor do sensor: {self.value}"
		else:
			return 'Mensagem não inicializada'

	# ! network (= big-endian)
	# B unsigned char (codigo)
	# d double (datahora)
	# I unsigned int (devID)
	# f float (valor)
	# Funcao de empacotamento de mensagem
	def pack(self, deviceID, value):
		self.dateTime = unixTimeStamp()
		self.deviceID = deviceID
		self.value = value
		return struct.pack(self.mask, self.code, self.dateTime, self.deviceID, self.value)

	def unpack(self, msg):
		code, self.dateTime, self.deviceID, self.value = struct.unpack(self.mask, msg)

class MessageLamp(Message):

	# Campos da mensagem
	deviceID = None	# 4 bytes - unsigned int
	action = None		# 1 byte - unsigned char
						# 0 = Desligar
						# 1 = Ligar

	def __init__(self):
		self.code = MSG_LAMPADA
		self.mask = '!BdIB'
		self.subject = 'Atuador'

	def toStringMsg(self):
		if(self.deviceID != None and self.action != None):
			if self.action == LUZ_APAGADA:
				return f"Ação: {self.action} (Apagar Luz)"
			if self.action == LUZ_ACESA:
				return f"Ação: {self.action} (Acender Luz)"
			else:
				return f"Ação: {self.action} (Desconhecida)"
		else:
			return 'Mensagem não inicializada'

	# ! network (= big-endian)
	# B unsigned char (codigo)
	# d double (datahora)
	# I unsigned int (devID)
	# B unsigned char (acao)
	# Funcao de empacotamento de mensagem
	def pack(self, deviceID, action):
		self.dateTime = unixTimeStamp()
		self.deviceID = deviceID
		self.action = action
		return struct.pack(self.mask, self.code, self.dateTime, self.deviceID, self.action)

	def unpack(self, msg):
		code, self.dateTime, self.deviceID, self.action = struct.unpack(self.mask, msg)

# cria um objeto contendo a primeira mensagem do buffer
# retorna (1) None se não existir uma mensagem completa ou buffer vazio
#         (2) o que restou no buffer após retirar a primeira mensagem
def getMessage(buffer):
	msg = None
	#O código está no primeiro byte
	codeBin = buffer[:1]
	if len(codeBin) == 1:
		code, = struct.unpack('!B', codeBin)
		if code >= 1 and code <= 6:
			# tamanho de cada tipo de mensagem
			msgsSize = [15,10,11,11,17,14]
			msgSize = msgsSize[code-1]
			# caso especial, mensagem com a lista possui tamanho variável
			if code == MSG_LISTA_AMBIENTES:
				cod,dat,countRooms = struct.unpack('!BdH', buffer[:11])
				msgSize += countRooms * 22
			# Se o buffer não contém uma mensagem inteira, retorna None e o buffer
			if len(buffer) < msgSize:
				return None, buffer
			# copia a mensagem do buffer
			msgData = buffer[:msgSize]
			# remove do buffer a mensagem que foi copiada
			buffer = buffer[msgSize:]
			# cria o objeto de acordo com o código da mensagem
			if code == MSG_STATUS:
				msg = MessageStatus()
			if code == MSG_REGISTRO:
				msg = MessageRegister()
			if code == MSG_LISTA_AMBIENTES:
				msg = MessageList()
			if code == MSG_SELECIONA_AMBIENTE:
				msg = MessageSelect()
			if code == MSG_SENSOR:
				msg = MessageSensor()
			if code == MSG_LAMPADA:
				msg = MessageLamp()
			# decodifica a mensagem recebida
			msg.unpack(msgData)
		else:
			# remove o código inválido
			buffer = buffer[1:]
		print('retornando mensagem codigo>', msg.code)
	return msg, buffer

# Recebe uma mensagem e retorna o objeto com os dados
def ReceiveMessage(connection, device):
	print('>>> Aguardando mensagem')
	msg = None
	# se o buffer ainda está vazio, aguarda chegada de dados
	if not device.buffer or len(device.buffer) == 0:
		device.buffer = connection.recv(TAM_BUFFER)
	while True:
		# msg = uma mensagem ou None quando não existem mais mensagens no buffer
		# buffer = o que sobrou no buffer após remover a mensagem recebida
		print('>>> Decodificando mensagem...')
		if device.buffer and len(device.buffer) > 0:
			msg, device.buffer = getMessage(device.buffer)
		# Se chegou uma mensagem, retorna o objeto
		if msg != None:
			return msg
		# a mensagem estava imcompleta ou o buffer vazio
		dataBin = connection.recv(TAM_BUFFER)
		if not dataBin:
			connection.close()
			break
		# adiciona novos dados ao buffer
		device.buffer = device.buffer + dataBin
	return None
