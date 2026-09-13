#####################################################
#                                                   #
# Título do trabalho: Trabalho de Sockets           #
#         Disciplina: Redes de Computadores PPComp  #
#                                                   #
#####################################################

import queue

class Device():
	ID = None           # ID do dispositivo
	type = None         # ID do tipo
	typeName = None     #     : descrição do tipo
	typeCode = None     #     : simbolo T=Temperatura, L=Lâmpada, S=Sensor de presença
	roomID = None       # ID do ambiente
	roomName = None     #     : nome do ambiente
	status = None       # Status da última operação realizada
	connection = None   # Conexão TCP
	clientIP = None     # Endereço IP do dispositivo
	value = None        # Último valor lido
	lampQueue = None    # Fila para comunicação com o controle
	buffer = ''

	def __init__(self, connection, clientIP, controlQueue):
		self.ID = 0
		self.value = 0
		self.connection = connection
		self.clientIP = clientIP
		self.controlQueue = controlQueue

	def toString(self):
		return f'{self.typeName}{self.ID}'
