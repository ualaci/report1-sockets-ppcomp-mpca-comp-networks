#####################################################
#                                                   #
#               Nome: Domingos José Pereira Paraiso #
#          Matrícula: 20221mpca0051                 #
# Título do trabalho: Trabalho de Sockets           #
#               Data: 24/04/2022                    #
#                Ano: 2022                          #
#         Disciplina: Redes de Computadores PPComp  #
#                                                   #
#####################################################

# Definições
SERVIDOR = 'localhost' # IP ou nome do Servidor
PORTA = 5000           # Porta TCP do serviço
TAM_BUFFER = 1024      # Tamanho máximo do buffer

# Arquivos com as tabelas
ARQUIVO_AMBIENTES = 'ambientes.txt'
ARQUIVO_TIPOS_DISPOSITIVOS = 'dispositivos.txt'

TEMPO_LUZ_ACESA = 5 #10 * 60 # 10 minutos x 60 segundos

# CONSTANTES USADAS NO SISTEMA
##############################
# Códigos do status
OK = 0
DISPOSITIVO_REGISTRADO = 1
LEITURA_RECEBIDA = 2
ACAO_EXECUTADA = 3
ERRO_DISPOSITIVO_NAO_REGISTRADO = 4
ERRO_DISPOSITIVO_NAO_SUPORTADO = 5
ERRO_FORMATO_MENSAGEM_INVALIDA = 6
ERRO_AMBIENTE_INVALIDO = 7
ERRO_ID_DE_DISPOSITIVO_INVALIDO = 8
ERRO_ACAO_NAO_SUPORTADA = 9
ERRO_MENSAGEM_NAO_ESPERADA = 10
ERRO_COMUNICACAO = 11

# Identificação dos tipos de sensores
NUM_LAMPADA = 1
COD_LAMPADA = 'L'
NUM_SENSOR_PRESENCA = 2
COD_SENSOR_PRESENCA = 'S'
NUM_TERMOMETRO = 3
COD_TERMOMETRO = 'T'
NUM_VENTILADOR = 4
COD_VENTILADOR = 'V'

# Códigos das mensagens
MSG_NULL = 0
MSG_STATUS = 1
MSG_REGISTRO = 2
MSG_LISTA_AMBIENTES = 3
MSG_SELECIONA_AMBIENTE = 4
MSG_SENSOR = 5
MSG_LAMPADA = 6
MSG_VENTILADOR = 7

# Máquina de estados do cliente conectado
SM_DESCONECTAR = 0
SM_INICIALIZANDO = 1
SM_SELECIONA_AMBIENTE = 2
SM_CONECTADO_SENSOR = 3
SM_CONECTADO_LAMPADA = 4
SM_CONECTADO_VENTILADOR = 5

# Comandos para fazer manutenção da lista de lâmpadas conectadas
INCLUIR_LAMPADA = 1
EXCLUIR_LAMPADA = 2
INCLUIR_VENTILADOR = 3
EXCLUIR_VENTILADOR = 4
LUZ_APAGADA = 0
LUZ_ACESA = 1

# Valores possíveis no sensor de presença
PRESENCA_NAO_DETECTADA = 0
PRESENCA_DETECTADA = 1

# Status do ventilador
VENTILADOR_DESLIGADO = 0
VENTILADOR_VELOCIDADE_1 = 1
VENTILADOR_VELOCIDADE_2 = 2
VENTILADOR_VELOCIDADE_3 = 3