import socket
import random
import threading
from datetime import datetime
import os

# Configuração do cliente UDP
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
p = random.randint(8000, 9998)
client.bind(("localhost", p))

# Solicita ao usuário que insira um nome para se conectar à sala
nome = input("Digite seu nome para se conectar a sala: ")
c = False

# Função para receber mensagens do servidor
def receber():
    lista_de_partes =[]
    while True:
        try:
            # Recebe mensagens do servidor
            mensagem, _ = client.recvfrom(1024)

            # Verifica se a mensagem é um indicador de início ou fim de arquivo
            if mensagem.decode() == '!1!1!' or mensagem.decode() == '!0!0!':
                card = ''
                nome_juntado = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"

                # Recebe partes do arquivo até encontrar o indicador de fim
                while True:
                    mensagem, _ = client.recvfrom(1024)
                    if mensagem.decode() == '!0!0!':
                        break
                    elif mensagem.decode() == '!1!1!':
                        continue
                    else:
                        card += mensagem.decode()

                # Salva o conteúdo do arquivo em um arquivo local
                with open(nome_juntado,'w') as file:
                    file.write(card)
                with open(nome_juntado,'r') as file:
                    ult = file.read()
                    print(ult)

            # Processa mensagens regulares
            if mensagem.decode() != "!0!0!":
                nome_arquivo = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
                data_hora = f"{datetime.now().strftime('%H:%M:%S - %d/%m/%Y')}"

                # Salva a mensagem em um arquivo local
                with open(nome_arquivo, "w") as file:
                    file.write(f'{mensagem.decode()}\n')

                # Lê o conteúdo do arquivo
                with open(nome_arquivo, "r") as file:
                    arquivo_final = file.read()
                ip = _[0]
                porta = _[1]

                if c:
                    print(f'{ip}:{p}/~{nome}: {arquivo_final} {data_hora}')
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
                    file.write(f'{mensagem}')

                # Verifica se o arquivo é grande demais para ser enviado em uma única mensagem
                tamanho_max = 800
                tamanho_do_arquivo = os.path.getsize(nome_arquivo)

                if tamanho_do_arquivo >= tamanho_max:
                    # Envia o arquivo em partes
                    with open(nome_arquivo, "rb") as file:
                        while True:
                            parte_do_arquivo = file.read(1024)
                            if not parte_do_arquivo:
                                flag = '!0!0!'
                                client.sendto(flag.encode(),("localhost", 5555))
                                break

                            flag = '!1!1!'
                            client.sendto(flag.encode(),("localhost", 5555))
                            client.sendto(parte_do_arquivo,("localhost", 5555))
                else:
                    # Envia o arquivo como uma única mensagem
                    with open(nome_arquivo, "rb") as file:
                        arquivo_bytes = file.read()

                    client.sendto(arquivo_bytes, ("localhost", 5555))
    else:
        # Solicita ao usuário que insira um nome para se conectar à sala
        nome = input("Digite seu nome para se conectar a sala (digite 'hi, meu nome eh: >nome<'): ")