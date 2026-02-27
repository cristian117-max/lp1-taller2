#!/usr/bin/env python3
"""
Problema 3: Chat simple con múltiples clientes - Cliente
Objetivo: Crear un cliente de chat que se conecte a un servidor y permita enviar/recibir mensajes en tiempo real
"""

import socket
import threading

HOST = 'localhost'  
PORT = 9000

def recibir_mensajes():
    while True:
        mensaje = cliente.recv(1024).decode()
        print(mensaje)

name = input("cual es tu nombre: ")
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect((HOST, PORT)) 
cliente.send(name.encode()) 

hilo_recibir = threading.Thread(target=recibir_mensajes)
hilo_recibir.start() 

while True:
   mensaje = input("Mensaje: ")
   cliente.send(mensaje.encode()) 
