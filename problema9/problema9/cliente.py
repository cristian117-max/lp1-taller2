import socket
import sys

LB_HOST = 'localhost'
LB_PORT = 5000

def get_server():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((LB_HOST, LB_PORT))
        s.sendall(b'GET_SERVER\n')
        resp = s.recv(1024).decode().strip()
        s.close()
        if resp.startswith('SERVER'):
            return resp.split()[1]
        else:
            print("no hay servidores")
            return None
    except:
        print("error contactando LB")
        return None

def send_request(server_addr, request):
    try:
        host, port = server_addr.split(':')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, int(port)))
        s.sendall(request.encode() + b'\n')
        resp = s.recv(1024).decode().strip()
        s.close()
        return resp
    except:
        return "ERROR de conexión"

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Uso: python client.py <read|write> <clave> [valor]")
        sys.exit(1)
    cmd = sys.argv[1].upper()
    key = sys.argv[2]
    value = sys.argv[3] if len(sys.argv) == 4 else None

    server = get_server()
    if not server:
        sys.exit(1)

    if cmd == 'READ':
        resp = send_request(server, f"READ {key}")
        print(f"valor leído: {resp}")
    elif cmd == 'WRITE' and value:
        resp = send_request(server, f"WRITE {key} {value}")
        print(f"escritura: {resp}")
    else:
        print("comando no válido") 
