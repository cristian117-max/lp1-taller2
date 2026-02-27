#!/usr/bin/env python3
"""
Problema 4: Servidor HTTP básico - Servidor
Objetivo: Implementar un servidor web simple que responda peticiones HTTP GET
y sirva archivos estáticos comprendiendo headers HTTP
"""
import socket
import http.server

HOST = 'localhost'  
PORT = 9000         



class Servidor(http.server.SimpleHTTPRequestHandler):
    pass

servidor = http.server.HTTPServer((HOST, PORT), Servidor)
servidor.serve_forever()
