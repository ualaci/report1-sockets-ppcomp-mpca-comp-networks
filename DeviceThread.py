#####################################################
#                                                   #
# Título do trabalho: Trabalho de Sockets           #
#         Disciplina: Redes de Computadores PPComp  #
#                                                   #
#####################################################

from Config import *
from Device import *
from Message import *
from ControlItem import *
from threading import Lock
import queue
import socket

########################################
# Thread para comunicar com um cliente #
########################################

device = None

global DEV_ID
DEV_ID = 0

lock = Lock()

def NewID(lock):
	newID = None
	with lock:
		global DEV_ID
		DEV_ID += 1
		newID = DEV_ID
	return newID

def WorkStart(device, msg):
	# Recebe mensagem de solicitação de registro do dispositivo
	# Validar se o dispositivo é suportado
	typeID = f'{msg.deviceType}'
	typeItem = GetTypeItem(typeID)
	if typeItem != None:
		device.typeID = typeItem.typeID
		device.typeCode = typeItem.typeCode
		device.typeName = typeItem.typeName
		print(f'{device.clientIP}: Dispositivo do tipo {device.typeName} ({device.typeCode}) registrado')
		# Enviar lista de ambientes
		msg = MessageList()
		if SendMessage(device, msg.pack(GetRoomDict())):
			print(device.toString() + ': Lista enviada ao cliente.')
			# Retorna o próximo estado e o tipo informado
			return SM_SELECIONA_AMBIENTE
		else:
			print(device.toString() + ': Falha ao enviar lista de ambientes');
			return SM_DESCONECTAR
		# Próximo estado, aguardar a seleção do ambiente
	else:
		# Falha no registro, envia status
		deviceType = msg.deviceType
		msg = MessageStatus()
		SendMessage(device, msg.pack(0, ERRO_DISPOSITIVO_NAO_SUPORTADO))
		print(device.toString() + ': Dispositivo não suportado código=({deviceType})');
		return SM_DESCONECTAR

def WorkSelectRoom(device, msg, controlQueue):
	# Valida a seleção e atualiza as tabelas
	roomID = f'{msg.roomID}'
	roomItem = GetRoomItem(roomID)
	if roomItem != None:
		# Gerar um novo ID
		deviceID = NewID(lock)
		# Salvar as informações do dispositivo
		device.ID = deviceID
		device.value = 0
		device.roomID = roomID
		device.roomName = roomItem.roomName
		print(device.toString() + ': Ambiente selecionado = [{device.roomID}] {device.roomName}')
		# Enviar o novo ID para o dispositivo
		msg = MessageStatus()
		SendMessage(device, msg.pack(device.ID, DISPOSITIVO_REGISTRADO))
		# Próximo estado, dispositivo conectado
		if device.typeCode == COD_LAMPADA:
			device.lampQueue = queue.Queue()
			print('Enviando mensagem de nova lâmpada para a fila do controle')
			controlQueue.put(MonitorItem(device.ID, device.typeCode, device.roomID, INCLUIR_LAMPADA, device.lampQueue))
			# Iniciar aguardando solicitação do controle na fila, depois recebemos a mensagem
			WaitLampQueue(device)
			return SM_CONECTADO_LAMPADA
		else:
			return SM_CONECTADO_SENSOR
	else:
		# Falha na seleção, envia status
		roomID = f'{msg.roomID}'
		msg = MessageStatus()
		sendMessage(device, msg.pack(0, ERRO_AMBIENTE_INVALIDO))
		print(device.toString() + ': Ambiente inválido (código={roomID})')
		return SM_DESCONECTAR

def WaitLampQueue(device):
	print(f'Aguardando evento, lâmpada {device.ID}')
	while True:
		action = device.lampQueue.get()
		if device.value != action:
			device.value = action
			break
	if action == LUZ_ACESA or action == LUZ_APAGADA:
		if action == LUZ_ACESA:
			print(device.toString() + ': Acender lâmpada')
		else:
			print(device.toString() + ': Apagar lâmpada')
		msg = MessageLamp()
		SendMessage(device, msg.pack(device.ID, action))
	else:
		print(device.toString() + ': Comando inválido para a lâmpada')
		msg = MessageStatus()
		SendMessage(device, msg.pack(device.ID, ERRO_ACAO_NAO_SUPORTADA))

def WorkLamp(device, msg):
	if msg.deviceID != device.ID:
		# ID do dispositivo enviado não é o mesmo que foi registrado
		msg = MessageStatus()
		sendMessage(device, msg.pack(device.ID, ERRO_ID_DE_DISPOSITIVO_INVALIDO))
		print(device.toString() + ': Cliente com ID inválido, esperava {device.ID}, recebi {msg.deviceID}')
		return SM_DESCONECTAR
	# Ao enviar uma solicitação de acionamento recebemos um status de volta
	if msg.code == MSG_STATUS:
		if msg.status == ACAO_EXECUTADA:
			print(device.toString() + ': Ação na lâmpada executada.')
	else:
		print(device.toString() + ': Mensagem não esperada (código={device.code})')
	WaitLampQueue(device)
	return SM_CONECTADO_LAMPADA

def WorkSensor(device, msg, controlQueue):
	if msg.deviceID != device.ID:
		# ID do dispositivo enviado não é o mesmo que foi registrado
		msg = MessageStatus()
		sendMessage(device, msg.pack(device.ID, ERRO_ID_DE_DISPOSITIVO_INVALIDO))
		print(device.toString() + ': Cliente com ID inválido, esperava {device.ID}, recebi {msg.deviceID}')
		return SM_DESCONECTAR
	# Atualizando os valores recebidos
	device.value = msg.value
	print(device.toString() + ': VALOR LIDO DO SENSOR =', msg.value)
	####################################################
	# Nesse ponto os dados poderiam ser persistidos em #
	# um banco de dados gerando um histórico contendo: #
	# 1) Sensor que enviou os dados                    #
	# 2) Data e hora em que o valor foi lido           #
	# 3) Local de instalação do sensor                 #
	# 4) Valor que foi lido pelo sensor                #
	####################################################
	# Se um sensor de presença foi acionado, informar ao controle
	if device.typeCode == COD_SENSOR_PRESENCA:
		print('Enviando mensagem do sensor para a fila do controle')
		controlQueue.put(MonitorItem(device.ID, device.typeCode, device.roomID, device.value, None))
	# Informando que a leitura foi recebida
	msg = MessageStatus()
	SendMessage(device, msg.pack(device.ID, LEITURA_RECEBIDA))
	return SM_CONECTADO_SENSOR

# Envia uma mensagem ao cliente conectado
def SendMessage(device, msg):
	try:
		print('Enviando mensagem: ', device.clientIP)
		device.connection.send(msg)
		return True
	except:
		return False

def DeviceThread(connection, clientIP, controlQueue):
	# Inicializando o status desse dispositivo
	device = Device(connection, clientIP, controlQueue)
	deviceStatus = SM_INICIALIZANDO
	expectMessage = MSG_REGISTRO
	print("Conectado: ", clientIP)
	while True:
		# loop para tratamento das mensagens recebidas
		msg = ReceiveMessage(connection, device)
		if not msg:
			break
		else:
			# Máquina de estado do dispositivo
			#                                               /--> (SM_CONECTADO_SENSOR)
			# (SM_INCIALIZANDO) --> (SM_SELECIONA AMBIENTE)< 
			#                                               \--> (SM_CONECTADO_LAMPADA)
			print("Mensagem recebida: ", clientIP, msg.toString())
			expectTable = [MSG_REGISTRO,MSG_SELECIONA_AMBIENTE,MSG_SENSOR,MSG_STATUS]
			expectMessage = expectTable[deviceStatus-1]
			# verifica se a mensagem recebida era esperada
			if expectMessage == msg.code:
				# chama o tratamento da mensagem de acordo com a máquina de estado
				if deviceStatus == SM_INICIALIZANDO:
					deviceStatus = WorkStart(device, msg)
				elif deviceStatus == SM_SELECIONA_AMBIENTE:
					deviceStatus = WorkSelectRoom(device, msg, controlQueue)
				elif deviceStatus == SM_CONECTADO_LAMPADA:
					deviceStatus = WorkLamp(device, msg)
				elif deviceStatus == SM_CONECTADO_SENSOR:
					deviceStatus = WorkSensor(device, msg, controlQueue)
				if deviceStatus == SM_DESCONECTAR:
					break
			else:
				msg = MessageStatus()
				SendMessage(device, msg.pack(device.ID, ERRO_MENSAGEM_NAO_ESPERADA))
				print('Erro: Estado inválido')
				break
	if device.ID != None:
		if device.typeCode == COD_LAMPADA:
			# Se for uma lâmpada, remove o dispositivo da lista do ambiente
			controlQueue.put(MonitorItem(device.ID, device.typeCode, device.roomID, EXCLUIR_LAMPADA, device.lampQueue))
	print(f'Desconectado: {device.clientIP}')
	connection.close()
