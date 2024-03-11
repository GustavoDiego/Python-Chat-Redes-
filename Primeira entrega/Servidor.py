import socket
import threading
import queue

# Fila para armazenar mensagens recebidas e informações do remetente
mensagens = queue.Queue()

# Lista para armazenar os clientes conectados
clientes = []

# Configuração do servidor UDP
servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
servidor.bind(("localhost", 5555))

# Função para receber mensagens e adicionar à fila
def receber():
    while True:
        try:
            # Recebe mensagem e endereço do remetente
            mensagem, addr = servidor.recvfrom(1024)
            # Adiciona mensagem e endereço à fila
            mensagens.put((mensagem, addr))
        except:
            pass

# Função para transmitir mensagens para todos os clientes
def broadcast():
    while True:
        while not mensagens.empty():
            # Obtém mensagem e endereço da fila
            mensagem, addr = mensagens.get()
            # Exibe mensagem no servidor
            print(mensagem.decode())

            # Adiciona novo cliente à lista, se ainda não estiver presente
            if addr not in clientes:
                clientes.append(addr)

            # Envia a mensagem para todos os clientes conectados
            for cliente in clientes:
                try:
                    # Verifica se a mensagem é uma mensagem de entrada
                    if mensagem.decode().startswith("tag_de_entrada:"):
                        nome = mensagem.decode()[mensagem.decode().index(":")+1:]
                        servidor.sendto(f"{nome} entrou!".encode(), cliente)
                    else:
                        # Envia a mensagem para todos os clientes
                        servidor.sendto(mensagem, cliente)
                except:
                    # Remove cliente se houver um problema ao enviar a mensagem
                    clientes.remove(cliente)

# Cria threads para as funções de receber e transmitir mensagens
t1 = threading.Thread(target=receber)
t2 = threading.Thread(target=broadcast)

# Inicia as threads
t1.start()
t2.start()