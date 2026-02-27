#!/usr/bin/env python3
"""
Problema 1: Sockets básicos - Cliente
Objetivo: Crear un cliente TCP que se conecte a un servidor e intercambie mensajes básicos
"""

import socket
HOST = 'Localhost'
PORT = 9000


cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

cliente.connect((HOST, PORT))

cliente.sendall(b"Mundo!") 

respuesta = cliente.recv(1024)

print(f"respuesta: {respuesta}")

cliente.close()
