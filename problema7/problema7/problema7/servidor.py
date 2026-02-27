import socket
import threading

HOST = "localhost"
PORT = 9000
BUFFER = 1024

def manejar_cliente(cliente, addr):
    try:
        # recibir la primera petición
        request = cliente.recv(BUFFER)
        if not request:
            cliente.close()
            return

        primera_linea = request.decode(errors="ignore").split("\n")[0]
        metodo, url, protocolo = primera_linea.split()
        print(f"[LOG] {addr} solicita {url}")

        # soporte HTTPS simple (CONNECT)
        if metodo.upper() == "CONNECT":
            host, port = url.split(":")
            port = int(port)
            cliente.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            destino = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            destino.connect((host, port))
            # Bidireccional: cliente <-> destino
            threading.Thread(target=lambda: transferir(cliente, destino)).start()
            transferir(destino, cliente)
            return

        # HTTP normal
        if "://" in url:
            _, url = url.split("://", 1)
        host = url.split("/")[0]
        puerto = 80

        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.connect((host, puerto))
        servidor.sendall(request)

        while True:
            datos = servidor.recv(BUFFER)
            if not datos:
                break
            cliente.sendall(datos)

    except Exception as e:
        print(f"[ERROR] {addr} - {e}")
    finally:
        cliente.close()
        print(f"[LOG] conexión con {addr} cerrada")

def transferir(origen, destino):
    try:
        while True:
            datos = origen.recv(BUFFER)
            if not datos:
                break
            destino.sendall(datos)
    except:
        pass

proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
proxy.bind((HOST, PORT))
proxy.listen()
print(f"proxy completo escuchando en {HOST}:{PORT} ...")

while True:
    cliente, addr = proxy.accept()
    print(f"[LOG] cliente conectado: {addr}")
    hilo = threading.Thread(target=manejar_cliente, args=(cliente, addr))
    hilo.start()
