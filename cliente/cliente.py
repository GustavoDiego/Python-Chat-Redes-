import socket
import random
import threading
from datetime import datetime
import os
import struct

# Configuração do cliente UDP
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
p = random.randint(8000, 9998)
client.bind(("localhost", p)) #alterar por ser desnecessário
unpacker = struct.Struct('5s H 800s')
packer = struct.Struct('5s H 800s')


def __int_chksum(byte_msg):

    total = 0
    length = len(byte_msg)  # length of the byte message object
    i = 0
    while length > 1:
        total += ((byte_msg[i + 1] << 8) & 0xFF00) + ((byte_msg[i]) & 0xFF)
        i += 2
        length -= 2

    if length > 0:
        total += (byte_msg[i] & 0xFF)

    while (total >> 16) > 0:
        total = (total & 0xFFFF) + (total >> 16)

    total = ~total

    return total & 0xFFFF


# Solicita ao usuário que insira um nome para se conectar à sala
nome = input("Digite seu nome para se conectar a sala: ")
c = False

# Função para receber mensagens do servidor
def receber():

    while True:
        try:
            # Recebe mensagens do servidor
            mensagem, _ = client.recvfrom(1024)
            flag, checksum, mensagem = packer.pack(mensagem)
            mensagem = mensagem.decode().rstrip('\x00')

            # Verifica se a mensagem é um indicador de início ou fim de arquivo
            if flag.decode() == '!1!1!':
                card = ''
                nome_juntado = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"

                # Recebe partes do arquivo até encontrar o indicador de fim
                while True:
                    mensagem, _ = client.recvfrom(1024)
                    flag, checksum, mensagem = packer.pack(mensagem)
                    mensagem = mensagem.decode().rstrip('\x00')

                    if flag.decode() == '!0!0!':
                        break
                    elif flag.decode() == '!1!1!':
                        continue
                    else:
                        card += mensagem.decode()

                # Salva o conteúdo do arquivo em um arquivo local
                with open(nome_juntado,'w') as file:
                    file.write(card)
                with open(nome_juntado,'r') as file:
                    arquivo_final = file.read()
                    print(f'{ip}:{p}/~ {arquivo_final} {data_hora}')

            # Processa mensagens regulares
            else:
                nome_arquivo = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
                data_hora = f"{datetime.now().strftime('%H:%M:%S - %d/%m/%Y')}"

                # Salva a mensagem em um arquivo local
                with open(nome_arquivo, "w") as file:
                    file.write(f'{mensagem.decode()}\n')

                # Lê o conteúdo do arquivo
                with open(nome_arquivo, "r") as file:
                    arquivo_final = file.read()
                ip = _[0] #alterar nome do _


                if c:
                    print(f'{ip}:{p}/~ {arquivo_final} {data_hora}')
                else:
                    mensagem = mensagem[17:]
                    print(f'{arquivo_final}')

        except:
            pass

# Inicia uma thread para receber mensagens
t = threading.Thread(target=receber)
t.start()



# Loop principal para o envio de mensagens
while True:
    # Se o nome começar com "hi, meu nome eh:", remove essa parte
    if "hi, meu nome eh: " in nome:
        nome = nome[17:]
        #envia ao servidor a informacao que e um cliente novo
        client.sendto(f'tag_de_entrada:{nome}'.encode(), ("localhost", 5555))
        while True:
            mensagem = input('Digite sua mensagem (ou "bye" para sair): ')
            c = True
            if mensagem == "bye":
                print(f'{nome} deixou o servidor :(')
                exit()
            else:
                # Gera o nome do arquivo usando a data atual e o nome do autor
                nome_arquivo = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"

                # Salva a mensagem em um arquivo local
                with open(nome_arquivo, "w") as file:
                    file.write(f'{nome} : {mensagem}')

                # Verifica se o arquivo é grande demais para ser enviado em uma única mensagem
                tamanho_max = 800
                tamanho_do_arquivo = os.path.getsize(nome_arquivo)
                
                flag = b'!0!0!'
                if tamanho_do_arquivo >= tamanho_max:
                    # Envia o arquivo em partes
                    with open(nome_arquivo, "rb") as file:
                        while True:
                            parte_do_arquivo = file.read(1024)
                            if not parte_do_arquivo:
                                flag = b'!0!0!'
                                checksum = 0
                                msg = 'fim'
                                ini_msg = packer.pack(flag,checksum, msg)
                                checksum = __int_chksum(bytearray(ini_msg))
                                fin_msg = packer.pack(flag,checksum, msg)
                                client.sendto(fin_msg,("localhost", 5555))
                                break

                            flag = b'!1!1!'
                            checksum = 0
                            ini_msg = packer.pack(flag,checksum, parte_do_arquivo)
                            checksum = __int_chksum(bytearray(ini_msg)) #bytearray não sei se vai ser necessário
                            fin_msg = packer.pack(flag, checksum, parte_do_arquivo)
                            client.sendto(fin_msg,("localhost", 5555))
                else:
                    # Envia o arquivo como uma única mensagem
                    with open(nome_arquivo, "rb") as file:
                        arquivo_bytes = file.read()
                    checksum = 0
                    ini_msg = packer.pack(flag,checksum, arquivo_bytes)
                    checksum = __int_chksum(bytearray(ini_msg))
                    fin_msg = packer.pack(flag,checksum, arquivo_bytes)
                    client.sendto(fin_msg, ("localhost", 5555))
    else:
        # Solicita ao usuário que insira um nome para se conectar à sala
        nome = input("Digite seu nome para se conectar a sala (digite 'hi, meu nome eh: >nome<'): ")