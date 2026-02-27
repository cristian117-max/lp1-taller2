import socket
import threading

HOST = 'localhost'
PORT = 9000

def recibir(cliente):
    while True:
        try:
            data = cliente.recv(1024)
            if not data:
                break
            print(data.decode(), end="")
        except:
            break

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect((HOST, PORT))

# Hilo para recibir mensajes del servidor
threading.Thread(target=recibir, args=(cliente,), daemon=True).start()

while True:
    mensaje = input()
    if mensaje.lower() == "exit":
        break
    cliente.sendall(mensaje.encode())

cliente.close()
