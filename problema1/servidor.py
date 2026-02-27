#!/usr/bin/env python3
"""
Problema 1: Sockets básicos - Servidor
Objetivo: Crear un servidor TCP que acepte una conexión y intercambie mensajes básicos
"""

import socket


HOST = 'Localhost'
PORT = 9000 

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

servidor.bind((HOST, PORT)) 


servidor.listen(1)
print("Servidor a la espera de conexiones ...")

#
cliente, direccion = servidor.accept()
print(f"un cliente se conecto desde la direccion{direccion}")


datos = cliente.recv(1024)


cliente.sendall(b"hola! " + datos)

cliente.close()
