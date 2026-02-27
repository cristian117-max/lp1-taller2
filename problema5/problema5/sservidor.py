
import socket
import threading
import os
import hashlib

HOST = "localhost"
PORT = 9000
CARPETA = "archivos_servidor" 
BUFFER = 1024


os.makedirs(CARPETA, exist_ok=True)

def checksum(ruta):
    """Calcula md5 de un archivo"""
    h = hashlib.md5()
    with open(ruta, "rb") as f:
        while True:
            datos = f.read(BUFFER)
            if not datos:
                break
            h.update(datos)
    return h.hexdigest()

def manejar_cliente(cliente, direccion):
    print(f"Conexión desde {direccion}")
    try:
        while True:
            comando = cliente.recv(BUFFER).decode().strip()
            if not comando:
                break

            if comando.startswith("LIST"):
                archivos = os.listdir(CARPETA)
                cliente.sendall("\n".join(archivos).encode())

            elif comando.startswith("UPLOAD"):
                _, nombre_archivo = comando.split(maxsplit=1)
                ruta = os.path.join(CARPETA, os.path.basename(nombre_archivo))
                with open(ruta, "wb") as f:
                    while True:
                        datos = cliente.recv(BUFFER)
                        if datos == b"EOF":
                            break
                        f.write(datos)
                print(f"Archivo recibido: {ruta}")
                cliente.sendall(b"UPLOAD OK")

            elif comando.startswith("DOWNLOAD"):
                _, nombre_archivo = comando.split(maxsplit=1)
                ruta = os.path.join(CARPETA, os.path.basename(nombre_archivo))
                if os.path.exists(ruta):
                    with open(ruta, "rb") as f:
                        while True:
                            datos = f.read(BUFFER)
                            if not datos:
                                break
                            cliente.sendall(datos)
                    cliente.sendall(b"EOF")
                else:
                    cliente.sendall(b"ERROR: Archivo no encontrado")
            else:
                cliente.sendall(b"ERROR: Comando no reconocido")

    except Exception as e:
        print(f"Error con {direccion}: {e}")
    finally:
        cliente.close()
        print(f"Conexión cerrada: {direccion}")

# Socket TCP
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind((HOST, PORT))
servidor.listen()
print(f"Servidor de archivos escuchando en {HOST}:{PORT}")

while True:
    cliente, direccion = servidor.accept()
    hilo = threading.Thread(target=manejar_cliente, args=(cliente, direccion))
    hilo.start()
