import socket
import threading
import queue

mensagens = queue.Queue()
clientes = []

servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
servidor.bind(("localhost", 5555))

def receber():
    while True:
        try:
            mensagem, addr = servidor.recvfrom(1024)
            mensagens.put((mensagem, addr))
        except:
            pass

def broadcast():
    while True:
        while not mensagens.empty():
            mensagem, addr = mensagens.get()
            print(mensagem.decode())

            if addr not in clientes:
                clientes.append(addr)

            for cliente in clientes:
                try:
                    if mensagem.decode().startswith("tag_de_entrada:"):
                        nome = mensagem.decode()[mensagem.decode().index(":")+1:]
                        servidor.sendto(f"{nome} entrou!".encode(), cliente)
                    else:
                        # Envie a mensagem para todos os clientes
                        servidor.sendto(mensagem, cliente)
                except:
                    clientes.remove(cliente)

t1 = threading.Thread(target=receber)
t2 = threading.Thread(target=broadcast)

t1.start()
t2.start()