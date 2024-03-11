import socket
import threading
import queue
import time
import struct

unpacker = struct.Struct('s s 5s H 800s')
packer = struct.Struct('s s 5s H 800s')
seqnum = '0'.encode("utf-8") #primeiroseqnum
seqnum_esperado = '0'.encode("utf-8")
ack = '1'.encode("utf-8")
pkt = '0'.encode("utf-8")
ack_chegou = True
ack_chegou_errado = False

def __int_chksum(byte_msg):

    checksum_value = 0
    for byte in byte_msg:
        checksum_value += byte
    checksum_value &= 0xFF  # Limita o checksum a um byte
    return checksum_value

def enviar_ack(seqnum, flag, addr):

    if flag.decode().rstrip('\x00') == 'ini':

        checksum = 0
        ini_msg = packer.pack(ack, seqnum, 'iniac'.encode("utf-8"), checksum, 'ack'.encode("utf-8"))
        checksum = __int_chksum(bytearray(ini_msg))
        fin_msg = packer.pack(ack, seqnum, 'iniac'.encode("utf-8"), checksum, 'ack'.encode("utf-8"))
        servidor.sendto(fin_msg, addr)
    elif flag.decode().rstrip('\x00') == 'syn':

        checksum = 0
        ini_msg = packer.pack(ack, seqnum, 'synac'.encode("utf-8"), checksum, 'ack'.encode("utf-8"))
        checksum = __int_chksum(bytearray(ini_msg))
        fin_msg = packer.pack(ack, seqnum, 'synac'.encode("utf-8"), checksum, 'ack'.encode("utf-8"))
        servidor.sendto(fin_msg, addr)
    else:

        checksum = 0
        ini_msg = packer.pack(ack, seqnum, flag, checksum, 'ack'.encode("utf-8"))
        checksum = __int_chksum(bytearray(ini_msg))
        fin_msg = packer.pack(ack, seqnum, flag, checksum, 'ack'.encode("utf-8"))
        servidor.sendto(fin_msg, addr)

    print('ack enviado')

def timer():
    global ack_chegou, ack_chegou_errado
    for _ in range(20):
        if ack_chegou or ack_chegou_errado:
            break
        time.sleep(0.1)

def receber():
    global ack_chegou,  seqnum_esperado, seqnum, ack_chegou_errado
    while True:
            mensagem_toda, addr = servidor.recvfrom(1024)

            tipo, seqnum_ext, flag, checksum_ext, mensagem = unpacker.unpack(mensagem_toda)

            if tipo == ack:
                    print('chegou um ack')
                    mensagem_chks = packer.pack(tipo,seqnum_ext,flag,0,mensagem)
                    checksum = __int_chksum(bytearray(mensagem_chks))
                    if checksum == checksum_ext:
                        if seqnum_ext == seqnum_esperado:
                            seqnum = (str((int(seqnum) + 1) % 2)).encode("utf-8")
                            seqnum_esperado = seqnum
                            ack_chegou = True
                        else:
                            print(f"senum esperado: {seqnum_esperado.decode('utf-8')} seqnum recebido: {seqnum_ext.decode('utf-8')}")
                            ack_chegou_errado = True
                    else:
                        print("cheksum não bateu")

            else:

                mensagem_chks = packer.pack(tipo, seqnum_ext, flag, 0, mensagem)
                checksum = __int_chksum(bytearray(mensagem_chks))

                if checksum == checksum_ext:
                    if ":" in mensagem.decode('utf-8')  and flag.decode().rstrip('\x00') != "tag" :
                        print(f'nome: ' + mensagem.decode('utf-8')[:mensagem.decode().index(":")-1].rstrip(
                            "\x00") + f', ip: {addr[0]} , porta {addr[1]} falou:' + mensagem.decode("utf-8").rstrip('\x00').split(':')[-1])
                    if  flag.decode('utf-8') == "!1!1!":
                        print(f', ip: {addr[0]} , porta {addr[1]} falou:' + mensagem.decode('utf-8'))
                    if flag.decode().rstrip('\x00') == 'tag':
                        print(mensagem.decode("utf-8")[21:].rstrip('\x00') + " Entrou no Server")
                        clientes.append(addr)
                        checksum = 0
                        ini_msg = packer.pack(pkt, seqnum_ext, '!1!0!'.encode('utf-8'), checksum, mensagem)
                        checksum = __int_chksum(bytearray(ini_msg))
                        mensagem_toda = packer.pack(pkt, seqnum_ext, '!1!0!'.encode("utf-8"), checksum, mensagem)
                        mensagens.put((mensagem_toda, addr))

                    elif flag.decode().rstrip('\x00') == 'fin':
                        ini_msg = packer.pack(tipo, seqnum, "!1!0!".encode("utf-8"), 0, mensagem)
                        checksum = __int_chksum(bytearray(ini_msg))
                        mensagem_toda = packer.pack(tipo, seqnum, "!1!0!".encode("utf-8"), checksum, mensagem)
                        mensagens.put((mensagem_toda, addr))
                        clientes.remove(addr)

                    elif flag.decode("utf-8") == '!1!0!' or flag.decode("utf-8") == '!1!1!' or flag.decode("utf-8") == '!0!0!':

                        ini_msg = packer.pack(pkt, seqnum, flag, 0, mensagem)
                        checksum = __int_chksum(bytearray(ini_msg))
                        mensagem_toda = packer.pack(tipo,seqnum,flag, checksum, mensagem)
                        mensagens.put((mensagem_toda, addr))
                        enviar_ack(seqnum_ext, flag, addr)

                    else:
                        enviar_ack(seqnum_ext, flag, addr)

                else:
                    print("cheksum não bateu")
                    enviar_ack((int(seqnum_ext.decode("utf-8"))+1)%2, flag, addr)

def broadcast():
    global ack_chegou
    while True:
        while not mensagens.empty():
            mensagem_c, addr = mensagens.get()
            for cliente in clientes:
                try:
                        # Envie a mensagem para todos os clientes menos ele mesmo
                        if addr != cliente:

                            ack_chegou = False
                            while not ack_chegou :
                                servidor.sendto(mensagem_c, cliente)
                                timer()

                except:
                    clientes.remove(cliente)

mensagens = queue.Queue()
clientes = []

servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
servidor.bind(("localhost", 5555))

t1 = threading.Thread(target=receber)
t2 = threading.Thread(target=broadcast)
t_time = threading.Thread(target=timer)

t1.start()
t2.start()
t_time.start()