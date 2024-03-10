import socket
import random
import threading
from datetime import datetime
import os
import struct
import time


# Configuração do cliente UDP
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
p = random.randint(8000, 9998)
client.bind(("localhost", p)) #alterar por ser desnecessário



unpacker = struct.Struct('s s 5s H 800s')
packer = struct.Struct('s s 5s H 800s')
seqnum = '0'.encode("utf-8") #primeiroseqnum
seqnum_esperado = '0'.encode("utf-8")
ack = '1'.encode("utf-8")
pkt = '0'.encode("utf-8")
ack_chegou = True
mensagem = ''



def __int_chksum(byte_msg):

    checksum_value = 0
    for byte in byte_msg:
        checksum_value += byte
    checksum_value &= 0xFF  # Limita o checksum a um byte
    return checksum_value
def timer():

    while True:
        # Define o tempo padrão aqui (por exemplo, 2 segundos)
        tempo_padrao = 2
        # Define o tempo para esperar até a próxima execução
        time.sleep(tempo_padrao)
        # Define o que deve acontecer quando o timer for acionado
        break




# Solicita ao usuário que insira um nome para se conectar à sala
nome = input("Digite seu nome para se conectar a sala: ")
escreveu_mensagem = True

# Função para receber mensagens do servidor
def receber():
    card = ''

    global seqnum_esperado, ack_chegou, seqnum
    while True:

            # Recebe mensagens do servidor
            mensagem_c, endereco = client.recvfrom(1024)


            tipo, seqnum_ext, flag, checksum_ext, mensagem_ = unpacker.unpack(mensagem_c)

            mensagem_chks = packer.pack(tipo, seqnum_ext, flag, 0, mensagem_)
            checksum_ext_novo = __int_chksum(bytearray(mensagem_chks))


            mensagem = mensagem_.decode("utf-8").rstrip('\x00')

            if tipo.decode("utf-8") == ack.decode("utf-8"):
                if seqnum_ext.decode("utf-8") == seqnum_esperado.decode("utf-8"):


                    ack_chegou = True

                else:
                    print('\nseqnum não bateu\n')

                    print(f"seqnum:{seqnum.decode('utf-8')}")

                    print(f"seqesperado = {seqnum_esperado.decode('utf-8')}")
                    pass
            else:

                # Verifica se a mensagem é um indicador de início ou fim de arquivo
                if flag.decode("utf-8") == '!1!1!':
                    mensagem_chks = packer.pack(tipo, seqnum_ext, flag, 0, mensagem_)
                    checksum_cut = __int_chksum(bytearray(mensagem_chks))
                    if checksum_cut == checksum_ext:

                        enviar_ack(seqnum_ext)
                        card += mensagem_.decode('utf-8')

                if flag.decode("utf-8") == '!0!0!':
                    mensagem_chks = packer.pack(tipo, seqnum_ext, flag, 0, mensagem_)
                    checksum_cut = __int_chksum(bytearray(mensagem_chks))
                    if checksum_cut == checksum_ext:
                        enviar_ack(seqnum_ext)
                        nome_juntado = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
                        with open(nome_juntado,'w') as file:
                            file.write(card)
                        with open(nome_juntado,'r') as file:
                            arquivo_final = file.read()

                            ip = endereco[0]
                            data_hora = f"{datetime.now().strftime('%H:%M:%S - %d/%m/%Y')}"

                            print(f'{ip}:{p}/~ {arquivo_final} {data_hora}')
                            card = ''

                # Processa mensagens regulares

                elif flag.decode('utf-8') == '!1!0!':




                    if checksum_ext_novo == checksum_ext:



                        enviar_ack(seqnum_ext)
                        nome_arquivo = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
                        data_hora = f"{datetime.now().strftime('%H:%M:%S - %d/%m/%Y')}"

                        # Salva a mensagem em um arquivo local
                        with open(nome_arquivo, "w") as file:
                            file.write(f'{mensagem}\n')

                        # Lê o conteúdo do arquivo
                        with open(nome_arquivo, "r") as file:
                            arquivo_final = file.read()


                        ip = endereco[0]


                        if escreveu_mensagem:
                            print(f'{ip}:{p}/~ {arquivo_final} {data_hora}')

                        else:
                            #envio de ack seqnum_esperado = seqnum seqnum = (int(seqnum)+1) % 2
                            mensagem = mensagem[17:]
                            print(f'{arquivo_final}')







def enviar_ack(seqnum):
    checksum = 0
    ini_msg = packer.pack(ack, seqnum, '!0!0!'.encode("utf-8"), checksum, 'ack'.encode("utf-8"))
    checksum_env = __int_chksum(bytearray(ini_msg))
    fin_msg = packer.pack(ack, seqnum, '!0!0!'.encode("utf-8"), checksum_env, 'ack'.encode("utf-8"))
    client.sendto(fin_msg, ("localhost", 5555))




# Inicia uma thread para receber mensagens

t = threading.Thread(target=receber)
t.start()
# Inicia uma thread para iniciar timer
t_time = threading.Thread(target=timer)
t_time.start()

# Loop principal para o envio de mensagens
while True:
    # Se o nome começar com "hi, meu nome eh:", remove essa parte
    if "hi, meu nome eh: " in nome:
        nome_v = nome[17:]
        #envia ao servidor a informacao que e um cliente novo

        checksum = 0

        ini_msg = packer.pack(pkt, seqnum, b'ini', checksum, 'ini'.encode('utf-8'))
        checksum_ini = __int_chksum(bytearray(ini_msg))
        fin_msg = packer.pack(pkt, seqnum, b'ini', checksum_ini, 'ini'.encode('utf-8'))
        client.sendto(fin_msg, ("localhost", 5555))
        ack_chegou = False
        timer()






        if ack_chegou:

            checksum = 0
            ini_msg = packer.pack(pkt, seqnum, b'tag', checksum, f' Entrou na conversa : {nome_v}'.encode("utf-8"))
            checksum_tag = __int_chksum(bytearray(ini_msg))
            fin_msg = packer.pack(pkt, seqnum, b'tag', checksum_tag, f' Entrou na conversa : {nome_v}'.encode("utf-8"))
            client.sendto(fin_msg, ("localhost", 5555))

            while True:
                if ack_chegou:
                    seqnum = (str((int(seqnum) + 1) % 2)).encode("utf-8")
                    seqnum_esperado = seqnum
                    if mensagem != "bye":

                        mensagem = input('Digite sua mensagem (ou "bye" para sair): ')
                        escreveu_mensagem = True

                    if mensagem == "bye":

                        checksum = 0

                        ini_msg = packer.pack(pkt, seqnum, b'syn', checksum, ''.encode("utf-8"))
                        checksum_bye = __int_chksum(bytearray(ini_msg))
                        fin_msg = packer.pack(pkt, seqnum, b'syn', checksum_bye, ''.encode("utf-8"))


                        client.sendto(fin_msg, ("localhost", 5555))

                        ack_chegou = False
                        timer()

                        if ack_chegou:

                            checksum = 0

                            ini_msg = packer.pack(pkt, seqnum, b'fin', checksum, f'{nome_v} Saiu da conversa'.encode("utf-8"))
                            checksum_Ack = __int_chksum(bytearray(ini_msg))
                            fin_msg = packer.pack(pkt, seqnum, b'fin', checksum_Ack,  f'{nome_v} Saiu da conversa'.encode("utf-8"))
                            client.sendto(fin_msg, ("localhost", 5555))

                            print(f'{nome_v} deixou a conversa :(')
                            exit()

                        else:

                            mensagem = "bye"

                            continue

                    else:
                        # Gera o nome do arquivo usando a data atual e o nome do autor
                        nome_arquivo = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"

                        # Salva a mensagem em um arquivo local
                        with open(nome_arquivo, "w") as file:
                            file.write(f'{nome_v} : {mensagem}')

                        # Verifica se o arquivo é grande demais para ser enviado em uma única mensagem
                        tamanho_max = 800
                        tamanho_do_arquivo = os.path.getsize(nome_arquivo)


                        flag = '!1!0!'.encode("utf-8")
                        if tamanho_do_arquivo >= tamanho_max:
                            # Envia o arquivo em partes
                            with open(nome_arquivo, "r") as file:

                                while True:

                                    if ack_chegou:


                                        parte_do_arquivo = file.read(800)
                                        parte_do_arquivo = parte_do_arquivo.encode("utf-8")


                                    else:


                                        pass


                                    if not parte_do_arquivo:


                                        flag = '!0!0!'.encode("utf-8")


                                        checksum = 0


                                        msg = 'fim'.encode("utf-8")


                                        ini_msg = packer.pack(pkt,seqnum,flag,checksum, msg)
                                        checksum_fim = __int_chksum(bytearray(ini_msg))
                                        fin_msg = packer.pack(pkt,seqnum,flag,checksum_fim, msg)
                                        client.sendto(fin_msg,("localhost", 5555))


                                        ack_chegou = False
                                        timer()


                                        if ack_chegou:

                                            break

                                        else:

                                            continue

                                    flag = '!1!1!'.encode("utf-8")

                                    checksum = 0

                                    ini_msg = packer.pack(pkt,seqnum,flag,checksum, parte_do_arquivo)
                                    checksum_fl = __int_chksum(bytearray(ini_msg))
                                    fin_msg = packer.pack(pkt,seqnum,flag, checksum_fl, parte_do_arquivo)

                                    client.sendto(fin_msg,("localhost", 5555))

                                    ack_chegou = False
                                    timer()

                        else:
                            # Envia o arquivo como uma única mensagem
                            with open(nome_arquivo, "r") as file:
                                arquivo_bytes = file.read()
                                arquivo_bytes = arquivo_bytes.encode("utf-8")



                            checksum = 0

                            ini_msg = packer.pack(pkt,seqnum,flag,checksum, arquivo_bytes)
                            checksum_ = __int_chksum(bytearray(ini_msg))
                            
                            fin_msg = packer.pack(pkt,seqnum,flag,checksum_, arquivo_bytes)


                            client.sendto(fin_msg, ("localhost", 5555))


                            ack_chegou = False
                            timer()
                else:

                    checksum = 0

                    ini_msg = packer.pack(pkt, seqnum, flag, checksum, arquivo_bytes)
                    checksum_Ack = __int_chksum(bytearray(ini_msg))

                    fin_msg = packer.pack(pkt, seqnum, flag, checksum_Ack, arquivo_bytes)


                    client.sendto(fin_msg, ("localhost", 5555))


                    ack_chegou = False
                    timer()


    else:
        # Solicita ao usuário que insira um nome para se conectar à sala
        nome = input("Digite seu nome para se conectar a sala (digite 'hi, meu nome eh: >nome<'): ")