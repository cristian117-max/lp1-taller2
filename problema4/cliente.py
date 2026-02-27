#!/usr/bin/env python3
"""
Problema 4: Servidor HTTP básico - Cliente
Objetivo: Crear un cliente HTTP que realice una petición GET a un servidor web local
"""
import socket
import http.client

HOST = 'localhost'
PORT = 9000

cliente = http.client.HTTPConnection(HOST, PORT)
cliente.request("GET", "/")
respuesta = cliente.getresponse()
datos = respuesta.read().decode()
print(datos)

cliente.close()
