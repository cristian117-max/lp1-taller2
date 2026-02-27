import socket
import threading

HOST = "localhost"
PORT = 9000

nombre = input("tu nombre: ")

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect((HOST, PORT))
cliente.send(nombre.encode())

def recibir():
    while True:
        try:
            datos = cliente.recv(1024).decode()
            if not datos:
                break
            print(datos)
        except:
            break

hilo = threading.Thread(target=recibir)
hilo.daemon = True
hilo.start()

while True:
    msg = input("comando o mensaje: ")
    cliente.send(msg.encode())
    if msg.upper() == "EXIT":
        break

cliente.close()
