import socket
import os

HOST = "localhost"
PORT = 9000
BUFFER = 1024

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect((HOST, PORT))

while True:
    comando = input("Comando (UPLOAD/DOWNLOAD/LIST/EXIT): ").strip()
    if comando.upper() == "EXIT":
        break

    if comando.startswith("UPLOAD"):
        _, ruta_local = comando.split(maxsplit=1)
        if not os.path.exists(ruta_local):
            print("Archivo no existe")
            continue
        nombre_archivo = os.path.basename(ruta_local)
        cliente.sendall(f"UPLOAD {nombre_archivo}".encode())
        with open(ruta_local, "rb") as f:
            while True:
                datos = f.read(BUFFER)
                if not datos:
                    break
                cliente.sendall(datos)
        cliente.sendall(b"EOF")
        respuesta = cliente.recv(BUFFER)
        print(respuesta.decode())

    elif comando.startswith("DOWNLOAD"):
        _, nombre_archivo = comando.split(maxsplit=1)
        cliente.sendall(f"DOWNLOAD {nombre_archivo}".encode())
        ruta = f"descarga_{nombre_archivo}"
        with open(ruta, "wb") as f:
            while True:
                datos = cliente.recv(BUFFER)
                if datos == b"EOF" or datos.startswith(b"ERROR"):
                    if datos.startswith(b"ERROR"):
                        print(datos.decode())
                        os.remove(ruta)
                    break
                f.write(datos)
        print(f"Archivo descargado: {ruta}")

    elif comando.startswith("LIST"):
        cliente.sendall(b"LIST")
        datos = cliente.recv(BUFFER)
        print("Archivos en servidor:\n", datos.decode())

    else:
        print("Comando no reconocido")

cliente.close()
