import socket
import threading
import queue
import time
import struct

# Configuração da estrutura de empacotamento e desempacotamento de mensagens
unpacker = struct.Struct('s s 5s H 800s')  # Estrutura para desempacotar mensagens recebidas
packer = struct.Struct('s s 5s H 800s')    # Estrutura para empacotar mensagens a serem enviadas

# Variáveis de controle de sequência e ACK
seqnum = '0'.encode("utf-8")              # Número de sequência atual
seqnum_esperado = '0'.encode("utf-8")      # Número de sequência esperado
ack = '1'.encode("utf-8")                  # Flag indicando um ACK
pkt = '0'.encode("utf-8")                  # Flag indicando um pacote de dados
ack_chegou = True                          # Indica se um ACK foi recebido com sucesso
ack_chegou_errado = False                  # Indica se um ACK foi recebido com erro

# Função para calcular o checksum de uma mensagem
def __int_chksum(byte_msg):
    checksum_value = 0
    for byte in byte_msg:
        checksum_value += byte
    checksum_value &= 0xFF  # Limita o checksum a um byte
    return checksum_value

# Função para enviar ACKs para o cliente
def enviar_ack(seqnum, flag, addr):
    # Verifica o tipo de flag recebido no parâmetro
    if flag.decode().rstrip('\x00') == 'ini':
        # Cria e envia um ACK para a flag 'ini'
        checksum = 0
        ini_msg = packer.pack(ack, seqnum, 'iniac'.encode("utf-8"), checksum, 'ack'.encode("utf-8"))
        checksum = __int_chksum(bytearray(ini_msg))
        fin_msg = packer.pack(ack, seqnum, 'iniac'.encode("utf-8"), checksum, 'ack'.encode("utf-8"))
        servidor.sendto(fin_msg, addr)
    elif flag.decode().rstrip('\x00') == 'syn':
        # Cria e envia um ACK para a flag 'syn'
        checksum = 0
        ini_msg = packer.pack(ack, seqnum, 'synac'.encode("utf-8"), checksum, 'ack'.encode("utf-8"))
        checksum = __int_chksum(bytearray(ini_msg))
        fin_msg = packer.pack(ack, seqnum, 'synac'.encode("utf-8"), checksum, 'ack'.encode("utf-8"))
        servidor.sendto(fin_msg, addr)
    else:
        # Cria e envia um ACK para outras flags
        checksum = 0
        ini_msg = packer.pack(ack, seqnum, flag, checksum, 'ack'.encode("utf-8"))
        checksum = __int_chksum(bytearray(ini_msg))
        fin_msg = packer.pack(ack, seqnum, flag, checksum, 'ack'.encode("utf-8"))
        servidor.sendto(fin_msg, addr)
    # Exibe uma mensagem indicando que o ACK foi enviado com sucesso
    print('ack enviado')

# Função para temporização de recebimento de ACKs
def timer():
    global ack_chegou, ack_chegou_errado
    for _ in range(20):
        if ack_chegou or ack_chegou_errado:
            break
        time.sleep(0.1)

# Função para receber mensagens dos clientes
def receber():
    global ack_chegou, seqnum_esperado, seqnum, ack_chegou_errado
    while True:
        # Recebe mensagem completa e o endereço do remetente
        mensagem_toda, addr = servidor.recvfrom(1024)
        # Desempacota a mensagem recebida
        tipo, seqnum_ext, flag, checksum_ext, mensagem = unpacker.unpack(mensagem_toda)

        # Verifica se a mensagem recebida é um ACK
        if tipo == ack:
            print('chegou um ack')
            # Empacota a mensagem do ACK e calcula o checksum
            mensagem_chks = packer.pack(tipo, seqnum_ext, flag, 0, mensagem)
            checksum = __int_chksum(bytearray(mensagem_chks))
            # Verifica se o checksum recebido corresponde ao calculado
            if checksum == checksum_ext:
                if seqnum_ext == seqnum_esperado:
                    # Atualiza o número de sequência esperado e indica que o ACK foi recebido com sucesso
                    seqnum = (str((int(seqnum) + 1) % 2)).encode("utf-8")
                    seqnum_esperado = seqnum
                    ack_chegou = True
                else:
                    # Indica que o ACK recebido está errado
                    print(f"senum esperado: {seqnum_esperado.decode('utf-8')} seqnum recebido: {seqnum_ext.decode('utf-8')}")
                    ack_chegou_errado = True
            else:
                print("cheksum não bateu")
        else:
            # Verifica o checksum da mensagem recebida
            mensagem_chks = packer.pack(tipo, seqnum_ext, flag, 0, mensagem)
            checksum = __int_chksum(bytearray(mensagem_chks))

            if checksum == checksum_ext:
                if ":" in mensagem.decode('utf-8') and flag.decode().rstrip('\x00') != "tag":
                    # Verifica se a mensagem é uma mensagem de entrada de cliente
                    print(f'nome: ' + mensagem.decode('utf-8')[:mensagem.decode().index(":")-1].rstrip("\x00") +
                          f', ip: {addr[0]} , porta {addr[1]} falou:' + mensagem.decode("utf-8").rstrip('\x00').split(':')[-1])
                if flag.decode('utf-8') == "!1!1!":
                    # Verifica se a mensagem é um pacote de dados
                    print(f', ip: {addr[0]} , porta {addr[1]} falou:' + mensagem.decode('utf-8'))
                if flag.decode().rstrip('\x00') == 'tag':
                    # Verifica se a mensagem é uma entrada de novo cliente
                    print(mensagem.decode("utf-8")[21:].rstrip('\x00') + " Entrou no Server")
                    # Adiciona o cliente à lista de clientes
                    clientes.append(addr)
                    checksum = 0
                    # Empacota e envia a mensagem para adicionar o cliente à fila de mensagens
                    ini_msg = packer.pack(pkt, seqnum_ext, '!1!0!'.encode('utf-8'), checksum, mensagem)
                    checksum = __int_chksum(bytearray(ini_msg))
                    mensagem_toda = packer.pack(pkt, seqnum_ext, '!1!0!'.encode("utf-8"), checksum, mensagem)
                    mensagens.put((mensagem_toda, addr))

                elif flag.decode().rstrip('\x00') == 'fin':
                    # Verifica se a mensagem é um pedido de desconexão de cliente
                    ini_msg = packer.pack(tipo, seqnum, "!1!0!".encode("utf-8"), 0, mensagem)
                    checksum = __int_chksum(bytearray(ini_msg))
                    mensagem_toda = packer.pack(tipo, seqnum, "!1!0!".encode("utf-8"), checksum, mensagem)
                    mensagens.put((mensagem_toda, addr))
                    # Remove o cliente da lista de clientes
                    clientes.remove(addr)

                elif flag.decode("utf-8") == '!1!0!' or flag.decode("utf-8") == '!1!1!' or flag.decode("utf-8") == '!0!0!':
                    # Verifica se a mensagem é um pacote de dados ou um pedido de desconexão
                    ini_msg = packer.pack(pkt, seqnum, flag, 0, mensagem)
                    checksum = __int_chksum(bytearray(ini_msg))
                    mensagem_toda = packer.pack(tipo, seqnum, flag, checksum, mensagem)
                    mensagens.put((mensagem_toda, addr))
                    # Envia um ACK em resposta à mensagem recebida
                    enviar_ack(seqnum_ext, flag, addr)

                else:
                    # Envia um ACK em resposta à mensagem recebida
                    enviar_ack(seqnum_ext, flag, addr)

            else:
                print("cheksum não bateu")
                # Envia um ACK em resposta à mensagem recebida
                enviar_ack((int(seqnum_ext.decode("utf-8"))+1)%2, flag, addr)

# Função para transmitir mensagens para todos os clientes
def broadcast():
    global ack_chegou
    while True:
        while not mensagens.empty():
            # Obtém mensagem e endereço da fila de mensagens
            mensagem_c, addr = mensagens.get()
            for cliente in clientes:
                try:
                    # Envia a mensagem para todos os clientes, exceto o remetente original
                    if addr != cliente:
                        ack_chegou = False
                        # Envia a mensagem e espera pelo recebimento do ACK
                        while not ack_chegou:
                            servidor.sendto(mensagem_c, cliente)
                            timer()
                except:
                    # Remove o cliente da lista de clientes se houver um problema ao enviar a mensagem
                    clientes.remove(cliente)

# Configuração inicial da fila de mensagens e lista de clientes
mensagens = queue.Queue()
clientes = []

# Configuração do servidor UDP
servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
servidor.bind(("localhost", 5555))

# Cria e inicia as threads para as funções de receber, transmitir e temporizar mensagens
t1 = threading.Thread(target=receber)
t2 = threading.Thread(target=broadcast)
t_time = threading.Thread(target=timer)

t1.start()
t2.start()
t_time.start()