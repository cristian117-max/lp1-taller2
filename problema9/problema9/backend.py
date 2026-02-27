import socket
import threading
import sys
import time

LB_HOST = 'localhost'
LB_PORT = 5000

data_store = {}          # diccionario local clave-valor
data_lock = threading.Lock()

def register(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((LB_HOST, LB_PORT))
        s.sendall(f"REGISTER {host} {port}\n".encode())
        resp = s.recv(1024)
        s.close()
        if resp.strip() == b'OK':
            print("Registro exitoso en LB")
        else:
            print("Error en registro")
    except:
        print("No se pudo conectar con LB")

def get_active_servers():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((LB_HOST, LB_PORT))
        s.sendall(b'GET_SERVERS\n')
        resp = s.recv(4096).decode().strip()
        s.close()
        parts = resp.split()
        if parts[0] == 'SERVERS':
            count = int(parts[1])
            return parts[2:2+count]
        return []
    except:
        return []

def replicate_to_others(key, value, my_addr):
    servers = get_active_servers()
    for addr in servers:
        if addr == my_addr:
            continue
        try:
            host, port = addr.split(':')
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, int(port)))
            s.sendall(f"REPLICATE {key} {value}\n".encode())
            resp = s.recv(1024)
            s.close()
            if resp.strip() != b'OK':
                print(f"Fallo replicación en {addr}")
        except:
            print(f"No se pudo conectar con {addr} para replicar")

def handle_connection(conn, my_addr):
    data = conn.recv(1024).decode().strip()
    if not data:
        conn.close()
        return
    parts = data.split()
    cmd = parts[0]

    if cmd == 'HEALTH':
        conn.sendall(b'OK\n')
    elif cmd == 'READ' and len(parts) == 2:
        key = parts[1]
        with data_lock:
            value = data_store.get(key, '')
        conn.sendall(f"{value}\n".encode())
    elif cmd == 'WRITE' and len(parts) == 3:
        key, value = parts[1], parts[2]
        with data_lock:
            data_store[key] = value
        # replicar en segundo plano para no bloquear al cliente
        threading.Thread(target=replicate_to_others, args=(key, value, my_addr)).start()
        conn.sendall(b'OK\n')
    elif cmd == 'REPLICATE' and len(parts) == 3:
        key, value = parts[1], parts[2]
        with data_lock:
            data_store[key] = value
        conn.sendall(b'OK\n')
    else:
        conn.sendall(b'ERROR Comando no soportado\n')
    conn.close()

def main(port):
    host = 'localhost'
    my_addr = f"{host}:{port}"
    register(host, port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(5)
    print(f"servidor escuchando en {host}:{port}")

    while True:
        conn, addr = sock.accept()
        threading.Thread(target=handle_connection, args=(conn, my_addr)).start()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("uso: python server.py <puerto>")
        sys.exit(1)
    port = int(sys.argv[1])
    main(port)
