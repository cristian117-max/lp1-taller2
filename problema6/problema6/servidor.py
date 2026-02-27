import socket
import threading

HOST = "localhost"
PORT = 9000


salas = {}
usuarios = {}
cliente_sala = {}

lock = threading.Lock()

def manejar_cliente(cliente):
    nombre = cliente.recv(1024).decode()
    usuarios[cliente] = nombre
    cliente_sala[cliente] = None
    cliente.send(f"bienvenido {nombre}! Usa JOIN, LEAVE, CREATE, LIST, PRIVATE, EXIT.".encode())

    while True:
        try:
            comando = cliente.recv(1024).decode()
            if not comando:
                break

            if comando.upper() == "EXIT":
                cliente.send("adios!".encode())
                break

            elif comando.startswith("CREATE"):
                _, sala = comando.split(maxsplit=1)
                with lock:
                    if sala not in salas:
                        salas[sala] = []
                        cliente.send(f"sala '{sala}' creada.".encode())
                    else:
                        cliente.send(f"sala '{sala}' ya existe.".encode())

            elif comando.startswith("JOIN"):
                _, sala = comando.split(maxsplit=1)
                with lock:
                    if sala not in salas:
                        cliente.send(f"sala '{sala}' no existe.".encode())
                    else:
                        
                        sala_actual = cliente_sala.get(cliente)
                        if sala_actual:
                            salas[sala_actual].remove(cliente)
                        salas[sala].append(cliente)
                        cliente_sala[cliente] = sala
                        cliente.send(f"te uniste a la sala '{sala}'".encode())

            elif comando.startswith("LEAVE"):
                sala_actual = cliente_sala.get(cliente)
                if sala_actual:
                    with lock:
                        salas[sala_actual].remove(cliente)
                        cliente_sala[cliente] = None
                    cliente.send(f"saliste de la sala '{sala_actual}'".encode())
                else:
                    cliente.send("no estás en ninguna sala.".encode())

            elif comando.upper() == "LIST":
                with lock:
                    lista_salas = ", ".join(salas.keys()) if salas else "No hay salas"
                cliente.send(f"salas disponibles: {lista_salas}".encode())

            elif comando.startswith("PRIVATE"):
                parts = comando.split(maxsplit=2)
                if len(parts) < 3:
                    cliente.send("formato: PRIVATE NombreUsuario Mensaje".encode())
                else:
                    _, target, msg = parts
                    encontrado = False
                    with lock:
                        for c, nombre_c in usuarios.items():
                            if nombre_c == target:
                                c.send(f"[privado {usuarios[cliente]}]: {msg}".encode())
                                encontrado = True
                    if not encontrado:
                        cliente.send(f"usuario '{target}' no encontrado.".encode())

            else:
                
                sala_actual = cliente_sala.get(cliente)
                if sala_actual:
                    with lock:
                        for c in salas[sala_actual]:
                            if c != cliente:
                                c.send(f"[{usuarios[cliente]}]: {comando}".encode())
                else:
                    cliente.send("unete a una sala para enviar mensajes".encode())

        except ConnectionResetError:
            break

    
    with lock:
        sala_actual = cliente_sala.get(cliente)
        if sala_actual and cliente in salas[sala_actual]:
            salas[sala_actual].remove(cliente)
        if cliente in usuarios:
            del usuarios[cliente]
        if cliente in cliente_sala:
            del cliente_sala[cliente]
    cliente.close()

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind((HOST, PORT))
servidor.listen()
print("servidor 'Chat con salas' en espera de conexiones...")

while True:
    cliente, addr = servidor.accept()
    hilo = threading.Thread(target=manejar_cliente, args=(cliente,))
    hilo.start()
