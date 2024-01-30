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
