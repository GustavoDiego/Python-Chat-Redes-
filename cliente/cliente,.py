import socket
import random
import threading
from datetime import datetime
import os

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind(("localhost", random.randint(8000, 9998)))

nome = input("Digite seu nome para se conectar a sala: ")

def receber():
    lista_de_partes =[]
    while True:
        try:
            mensagem, _ = client.recvfrom(1024)
            if mensagem.decode() == '!1!1!' or mensagem.decode() == '!0!0!':
                card = ''
                nome_juntado = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
                while True:


                    mensagem, _ = client.recvfrom(1024)
                    if mensagem.decode() == '!0!0!':
                        break
                    elif mensagem.decode() == '!1!1!':
                        continue
                    else:
                        card+=mensagem.decode()

                with open(nome_juntado,'w') as file:
                    file.write(card)
                with open (nome_juntado,'r') as file:
                    ult = file.read()
                    print(ult)


            if mensagem.decode() != "!0!0!":
                nome_arquivo = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
                data_hora = f"{datetime.now().strftime('%H:%M:%S - %d/%m/%Y')}"

                # Abre o arquivo para escrita
                with open(nome_arquivo, "w") as file:
                    file.write(f'{mensagem.decode()}\n')

                # Lê o conteúdo do arquivo
                with open(nome_arquivo, "r") as file:
                    arquivo_final = file.read()
                ip = _[0]
                porta = _[1]
                print(f'{ip}:{porta}/~{nome}: {arquivo_final} {data_hora}')
        except:
            pass
t = threading.Thread(target=receber)
t.start()

while True:
    if "hi, meu nome eh:" in nome:
        nome = nome[15:]
        while True:
            mensagem = input('Digite sua mensagem (ou "bye" para sair): ')
            if mensagem == "bye":
                print(f'{nome} deixou o servidor :(')
                exit()
            else:
                # Gera o nome do arquivo usando a data atual e o nome do autor
                nome_arquivo = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"

                # Abre o arquivo para escrita
                with open(nome_arquivo, "w") as file:
                    file.write(f'{mensagem}\n')

                tamanho_max = 800
                tamanho_do_arquivo = os.path.getsize(nome_arquivo)


                if tamanho_do_arquivo >= tamanho_max:
                    with open(nome_arquivo,"rb") as file:

                        while True:

                            parte_do_arquivo = file.read(1024)

                            if not parte_do_arquivo:
                                flag = '!0!0!'
                                client.sendto(flag.encode(),("localhost",5555))
                                break

                            flag = '!1!1!'
                            client.sendto(flag.encode(),("localhost", 5555))

                            client.sendto(parte_do_arquivo,("localhost", 5555))


                else:
                    # Lê o conteúdo do arquivo
                    with open(nome_arquivo, "rb") as file:
                        arquivo_bytes = file.read()


                    # Envia o arquivo para o servidor

                    client.sendto(arquivo_bytes, ("localhost", 5555))

    else:
        nome = input("Digite seu nome para se conectar a sala: ")