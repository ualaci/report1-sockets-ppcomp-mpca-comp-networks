#####################################################
# Cliente: Ventilador de Teto                       #
#####################################################

from Config import *
from Message import *
from ClientUtil import *
import socket

deviceID = None

if __name__ == '__main__':
    print('Inicializando cliente: Ventilador de Teto...')
    try:
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        destination = (SERVIDOR, PORTA)
        connection.connect(destination)
    except Exception as e:
        print(f'Falha ao tentar se conectar com o servidor {SERVIDOR} porta {PORTA}')
        exit()
        
    device = Device(connection, NUM_VENTILADOR)
    roomDict = ClientRegister(device)
    
    if roomDict != None:
        deviceID, roomID, roomName = SelectRoom(device, roomDict)
        if deviceID != None:
            while True:
                print(f'\n==> Ambiente [{roomID}] {roomName} - Ventilador')
                msg = ReceiveMessage(connection, device)
                
                # Aguarda receber um MSG_VENTILADOR instruindo a nova velocidade
                if msg and msg.code == MSG_VENTILADOR:
                    print('#####################################')
                    if msg.speed == VENTILADOR_DESLIGADO:
                        print('       VENTILADOR DESLIGADO')
                    elif msg.speed == VENTILADOR_VELOCIDADE_1:
                        print('       VENTILADOR: VELOCIDADE 1')
                    elif msg.speed == VENTILADOR_VELOCIDADE_2:
                        print('       VENTILADOR: VELOCIDADE 2')
                    elif msg.speed == VENTILADOR_VELOCIDADE_3:
                        print('       VENTILADOR: VELOCIDADE 3')
                    else:
                        print(f'Velocidade não reconhecida: {msg.speed}')
                    print('#####################################')
                    
                    # Devolve a confirmação de que a ação foi executada com sucesso
                    msg_status = MessageStatus()
                    connection.send(msg_status.pack(deviceID, ACAO_EXECUTADA))					
                else:
                    if msg:
                        print('Mensagem inválida recebida. Código:', msg.code)
                    else:
                        print('Conexão encerrada pelo servidor.')
                        break
        connection.close()
