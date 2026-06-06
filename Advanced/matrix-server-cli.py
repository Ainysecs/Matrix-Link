import socket
import threading
import sys
import os
import json

class Color:
    USER = '\033[38;5;10m'     # Verde claro
    FRIEND = '\033[38;5;39m'   # Ciano
    SYS = '\033[38;5;220m'    # Amarelo
    PANIC = '\033[38;5;15m'    # Branco
    DANGER = '\033[38;5;196m'  # Vermelho
    RESET = '\033[0m'          # Reset

HOST = '0.0.0.0'
DEFAULT_PORT = 5555
BUFFER_SIZE = 4096

clientes_conectados = {}
ips_banidos = set()
users_banidos = set()
lista_lock = threading.Lock()

def clear_screen() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')

def broadcast(mensagem: bytes, client_origem: socket.socket) -> None:
    with lista_lock:
        mortos = []

        for cliente in list(clientes_conectados.keys()):
            if cliente != client_origem:
                try:
                    cliente.sendall(mensagem)
                except (OSError, ConnectionResetError):
                    mortos.append(cliente)

        for morto in mortos:
            if morto in clientes_conectados:
                del clientes_conectados[morto]
                try:
                    morto.close()
                except Exception:
                    pass

def escutar_comandos_servidor() -> None:
    while True:
        try:
            comando = input().strip()
            if not comando: continue

            if comando == "/list":
                with lista_lock:
                    print(f"\n{Color.SYS}📋 --- Tabela de Roteamento ---{Color.RESET}")
                    if not clientes_conectados:
                        print("Nenhum agente conectado.")
                    for sock, info in clientes_conectados.items():
                        print(f" -> IP: {info['ip']}:{info['port']} | Sala: {Color.USER}{info['room']}{Color.RESET} | User: {Color.FRIEND}{info['user']}{Color.RESET}")
                    print(f"{Color.SYS}------------------------------{Color.RESET}\n")

            elif comando.startswith("/kick ") or comando.startswith("/ban "):
                partes = comando.split(" ", 1)
                acao = partes[0]
                alvo_raw = partes[1]

                tipo = "ip"
                valor = alvo_raw
                if ":" in alvo_raw:
                    tipo, valor = alvo_raw.split(":", 1)
                    tipo = tipo.lower()

                if acao == "/ban":
                    if tipo == "ip": ips_banidos.add(valor)
                    elif tipo == "user": users_banidos.add(valor)
                    print(f"{Color.DANGER}🔨 [BAN]: Regra de quarentena ativa para -> {tipo}:{valor}{Color.RESET}")

                with lista_lock:
                    removidos = 0
                    for sock in list(clientes_conectados.keys()):
                        info = clientes_conectados[sock]

                        if (tipo == "ip" and info["ip"] == valor) or \
                           (tipo == "user" and info["user"] == valor) or \
                           (tipo == "sala" and info["room"] == valor):

                            try:
                                aviso = json.dumps({"cmd": "kick", "msg": f"Removido pelo admin (Regra: {tipo}:{valor})"}) + "\n"
                                sock.sendall(aviso.encode('utf-8'))
                                sock.close()
                            except: pass

                            del clientes_conectados[sock]
                            removidos += 1

                    print(f"{Color.SYS}⚡ Ação concluída. {removidos} nó(s) obliterado(s).{Color.RESET}")

        except Exception:
            break

def gerenciar_cliente(client_socket: socket.socket, endereco: tuple) -> None:
    ip, porta = endereco
    print(f"{Color.USER}📡 [Nó Conectado]: {ip}:{porta} entrou no túnel.{Color.RESET}")

    while True:
        try:
            mensagem = client_socket.recv(BUFFER_SIZE)
            if not mensagem:
                break

            try:
                decoded = message_chunk = mensagem.decode('utf-8')
                for linha in decoded.split('\n'):
                    if not linha.strip(): continue
                    pacote = json.loads(linha)

                    with lista_lock:
                        if client_socket in clientes_conectados:
                            user_atual = pacote.get("user", "Desconhecido")
                            clientes_conectados[client_socket]["user"] = user_atual
                            clientes_conectados[client_socket]["room"] = pacote.get("room", "Desconhecido")

                            if user_atual in users_banidos:
                                aviso = json.dumps({"cmd": "kick", "msg": "Usuário na lista negra do servidor."}) + "\n"
                                client_socket.sendall(aviso.encode('utf-8'))
                                raise ConnectionAbortedError("Tentativa de uso de username banido.")
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass

            broadcast(mensagem, client_socket)

        except (ConnectionResetError, ConnectionAbortedError):
            break
        except Exception as e:
            print(f"{Color.SYS}⚠️ [Aviso]: Erro na rota de {ip}: {e}{Color.RESET}")
            break

    print(f"{Color.DANGER}❌ [Nó Desconectado]: {ip}:{porta} quebrou o link.{Color.RESET}")

    with lista_lock:
        if client_socket in clientes_conectados:
            del clientes_conectados[client_socket]
            print(f"{Color.FRIEND}👥 [Status da Teia]: {len(clientes_conectados)} agente(s) online.{Color.RESET}")

    try:
        client_socket.close()
    except Exception:
        pass

def iniciar_servidor(porta: int) -> None:
    clear_screen()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind((HOST, porta))
        server.listen()
        print(f"{Color.SYS}=================================================={Color.RESET}")
        print(f"{Color.USER} 🌐 MATRIX-LINK [METADATA RELAY] - PORTA {porta} {Color.RESET}")
        print(f"{Color.SYS}  Criptografia da Mensagem : [BLIND / CEGA] {Color.RESET}")
        print(f"{Color.SYS}  Rastreio de Metadados    : [ATIVO (Room/User)] {Color.RESET}")
        print(f"{Color.SYS}=================================================={Color.RESET}")
        print(f"{Color.USER} Comandos: /list, /kick tipo:alvo, /ban tipo:alvo{Color.RESET}")
        print(f"{Color.SYS} Ex: /kick user:Neo | /kick sala:Zion | /ban ip:10.0.0.1{Color.RESET}\n")
    except Exception as e:
        print(f"{Color.DANGER}🛑 [Erro Crítico]: Falha ao vincular a porta {porta}. {e}{Color.RESET}")
        sys.exit(1)

    threading.Thread(target=escutar_comandos_servidor, daemon=True).start()

    while True:
        try:
            client_socket, endereco = server.accept()
            ip_visitante = endereco[0]

            if ip_visitante in ips_banidos:
                print(f"{Color.DANGER}🛡️ [Bloqueio]: O IP banido {ip_visitante} foi barrado no portão.{Color.RESET}")
                client_socket.close()
                continue

            with lista_lock:
                clientes_conectados[client_socket] = {
                    "ip": ip_visitante,
                    "port": endereco[1],
                    "user": "Conectando...",
                    "room": "..."
                }
                total_atual = len(clientes_conectados)

            print(f"{Color.FRIEND}👥 [Status da Teia]: {total_atual} agente(s) conectados.{Color.RESET}")

            thread = threading.Thread(
                target=gerenciar_cliente,
                args=(client_socket, endereco),
                daemon=True
            )
            thread.start()

        except KeyboardInterrupt:
            print(f"\n{Color.DANGER}🛑 [Desligando]: Relay central encerrado pelo operador.{Color.RESET}")
            break
        except Exception as e:
            print(f"{Color.DANGER}⚠️ [Erro no Loop Principal]: {e}{Color.RESET}")

# --- BOOT ---
if __name__ == "__main__":
    clear_screen()
    print(f"{Color.SYS}=================================================={Color.RESET}")
    print(f"{Color.USER}      🌐 MATRIX-LINK SERVER INITIALIZATION        {Color.RESET}")
    print(f"{Color.SYS}=================================================={Color.RESET}\n")

    porta_input = input(f"🚪 Porta de Escuta do Servidor [Enter = {DEFAULT_PORT}]: ").strip()
    target_port = int(porta_input) if porta_input.isdigit() else DEFAULT_PORT

    iniciar_servidor(target_port)
