import socket
import threading
import time
from collections import deque

HOST = 'localhost'
PORT = 5000
CHECK_INTERVAL = 5  # segundos entre health checks

servers = {}          # {addr: last_heartbeat}  addr = "host:port"
servers_lock = threading.Lock()
rr_index = 0

def health_check():
    global servers
    while True:
        time.sleep(CHECK_INTERVAL)
        with servers_lock:
            to_remove = []
            for addr, last in list(servers.items()):
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(2)
                    host, port = addr.split(':')
                    s.connect((host, int(port)))
                    s.sendall(b'HEALTH\n')
                    data = s.recv(1024)
                    if data.strip() != b'OK':
                        raise Exception("No OK")
                    s.close()
                except:
                    print(f"Servidor {addr} no responde, eliminado")
                    to_remove.append(addr)
            for addr in to_remove:
                del servers[addr]

def handle_client(conn):
    global rr_index
    data = conn.recv(1024).decode().strip()
    if not data:
        conn.close()
        return
    parts = data.split()
    cmd = parts[0]

    if cmd == 'REGISTER' and len(parts) == 3:
        addr = f"{parts[1]}:{parts[2]}"
        with servers_lock:
            servers[addr] = time.time()
        conn.sendall(b'OK\n')
        print(f"servidor registrado: {addr}")

    elif cmd == 'GET_SERVER':
        with servers_lock:
            if not servers:
                conn.sendall(b'ERROR No hay servidores disponibles\n')
            else:
                addrs = list(servers.keys())
                addr = addrs[rr_index % len(addrs)]
                rr_index += 1
                conn.sendall(f'SERVER {addr}\n'.encode())

    elif cmd == 'GET_SERVERS':
        with servers_lock:
            addrs = list(servers.keys())
            resp = f"SERVERS {len(addrs)} " + " ".join(addrs) + "\n"
            conn.sendall(resp.encode())
    else:
        conn.sendall(b'ERROR Comando desconocido\n')
    conn.close()

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f"LB escuchando en {HOST}:{PORT}")

    threading.Thread(target=health_check, daemon=True).start()

    while True:
        conn, addr = sock.accept()
        threading.Thread(target=handle_client, args=(conn,)).start()

if __name__ == '__main__':
    main()
