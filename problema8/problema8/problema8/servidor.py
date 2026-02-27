import socket
import threading

HOST = 'localhost'
PORT = 9000

# estado del juego
tablero = [" "] * 9
turno = "X"
jugadores = []      # maximo 2 jugadores
espectadores = []   # lista de espectadores
lock = threading.Lock()

def mostrar_tablero():
    t = tablero
    return f"""
 {t[0]} | {t[1]} | {t[2]}
---+---+---
 {t[3]} | {t[4]} | {t[5]}
---+---+---
 {t[6]} | {t[7]} | {t[8]}
"""

def comprobar_ganador():
    combos = [
        (0,1,2),(3,4,5),(6,7,8),
        (0,3,6),(1,4,7),(2,5,8),
        (0,4,8),(2,4,6)
    ]
    for a,b,c in combos:
        if tablero[a] == tablero[b] == tablero[c] != " ":
            return tablero[a]
    if " " not in tablero:
        return "empate"
    return None

def enviar_a_todos(mensaje):
    for c in jugadores + espectadores:
        try:
            c.sendall(mensaje.encode())
        except:
            continue

def manejar_cliente(cliente):
    global turno
    cliente.sendall(b"bienvenido al Tic-Tac-Toe!\n")

    with lock:
        if len(jugadores) < 2:
            jugadores.append(cliente)
            marca = "X" if len(jugadores) == 1 else "O"
            cliente.sendall(f"eres jugador {marca}\n".encode())
        else:
            espectadores.append(cliente)
            cliente.sendall(b"eres espectador\n")
            cliente.sendall(mostrar_tablero().encode())
            # el espectador solo recibe el tablero y no juega

    # si es espectador, solo toca inviar actualizaciones
    if cliente in espectadores:
        try:
            while True:
                # los espectadores no envían comandos
                data = cliente.recv(1024)
                if not data:
                    break
        except:
            pass
        finally:
            with lock:
                if cliente in espectadores:
                    espectadores.remove(cliente)
            cliente.close()
        return

    # lógica para jugadores
    while True:
        try:
            cliente.sendall(f"\nturno actual: {turno}\n".encode())
            cliente.sendall(b"ingrese posici\xc3\xb3n (0-8): ") 
            data = cliente.recv(1024)
            if not data:
                break
            
            move = data.decode().strip()

            with lock:
                jugador_index = jugadores.index(cliente)
                jugador_marca = "X" if jugador_index == 0 else "O"
                
                if jugador_marca != turno:
                    cliente.sendall(b"no es tu turno.\n")
                    continue

                try:
                    pos = int(move)
                    if pos < 0 or pos > 8 or tablero[pos] != " ":
                        cliente.sendall(b"movimiento inv\xc3\xa1lido!\n")
                        continue
                except ValueError:
                    cliente.sendall(b"entrada inv\xc3\xa1lida! Usa 0-8\n")
                    continue

                # realizar movimiento
                tablero[pos] = turno
                
                # envia el tablero actualizado a todos
                tablero_str = mostrar_tablero()
                enviar_a_todos(tablero_str + "\n")

                # verificar ganador
                ganador = comprobar_ganador()
                if ganador:
                    if ganador == "empate":
                        mensaje_final = "¡empate!\n"
                    else:
                        mensaje_final = f"¡gana {ganador}!\n"
                    
                    enviar_a_todos(mensaje_final)
                    
                    # reiniciar tablero
                    tablero[:] = [" "] * 9
                    turno = "X"
                    
                    # notificar el reinicio
                    enviar_a_todos("\n--- NUEVA PARTIDA ---\n")
                    enviar_a_todos(mostrar_tablero() + "\n")
                    continue

                # cambiar de turno
                turno = "O" if turno == "X" else "X"

        except (ConnectionResetError, BrokenPipeError):
            break
        except Exception as e:
            print(f"error inesperado: {e}")
            break

    # limpiar al desconectar
    with lock:
        if cliente in jugadores:
            jugadores.remove(cliente)
            # si un jugador se desconecta, entonces se reicicia el juego
            if len(jugadores) < 2:
                tablero[:] = [" "] * 9
                turno = "X"
                enviar_a_todos("un jugador se ha desconectado. Juego reiniciado.\n")
        if cliente in espectadores:
            espectadores.remove(cliente)
    
    cliente.close()

# servidor TCP
try:
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PORT))
    servidor.listen()
    print(f"servidor Tic-Tac-Toe escuchando en {HOST}:{PORT}...")

    while True:
        cliente, addr = servidor.accept()
        print(f"[LOG] Cliente conectado: {addr}")
        threading.Thread(target=manejar_cliente, args=(cliente,), daemon=True).start()
except KeyboardInterrupt:
    print("\nServidor detenido por el usuario")
finally:
    servidor.close()
