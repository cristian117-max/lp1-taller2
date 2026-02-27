#!/usr/bin/env python3
"""
Problema 3: Chat simple con múltiples clientes - Servidor
Objetivo: Crear un servidor de chat que maneje múltiples clientes simultáneamente usando threads
"""

import socket
import threading 

HOST = 'localhost'
PORT = 9000

clientes = []
def atender_cliente(cliente, name):
    while True: 
        try: 
            mensaje = cliente.recv(1024) 
            if not mensaje:
                break
            print(f"{name}: {mensaje.decode()}")
            broadcast(mensaje.decode(), cliente) 
        except ConnectionResetError:
            clientes.remove(cliente) 
            cliente.close()
            break

def broadcast(mensaje, emisor):
    for cliente in clientes:
        if cliente != emisor:
            cliente.send(mensaje.encode()) 

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind((HOST, PORT))
servidor.listen() 
print("El servidor 'Chat' esta a la espera de conexiones ...")

while True: 
   cliente, direccion = servidor.accept()
   print(f"cliente conectado desde la direccion {direccion}")
   name = cliente.recv(10249).decode()
   clientes.append(cliente)
   broadcast(f"{name} se ha unido al chat!", cliente)
   hilo_cliente = threading.Thread(target=atender_cliente, args=(cliente, name))
   hilo_cliente.start()

