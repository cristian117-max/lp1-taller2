import socket

HOST = "localhost"
PORT = 9000
BUFFER = 1024

url = input("Ingresa URL (http:// o https://): ")

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect((HOST, PORT))

if url.startswith("https://"):
    host_port = url.split("//")[1].split("/")[0]
    request = f"CONNECT {host_port} HTTP/1.1\r\nHost: {host_port}\r\n\r\n"
else:
    host = url.split("//")[1].split("/")[0]
    request = f"GET {url} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"

cliente.sendall(request.encode())

respuesta_total = b""
while True:
    datos = cliente.recv(BUFFER)
    if not datos:
        break
    respuesta_total += datos

print(respuesta_total.decode(errors="ignore")[:500])
cliente.close()
