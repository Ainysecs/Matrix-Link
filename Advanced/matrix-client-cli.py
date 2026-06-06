import socket
import threading
import sys
import os
import json
import time
import base64
import hashlib
import hmac
import secrets
from datetime import datetime
from typing import Tuple, Set, List

BUFFER_SIZE = 4096
ENCODING = 'utf-8'
DEFAULT_PORT = 5555

class Color:
    USER = '\033[38;5;10m'     # Verde
    FRIEND = '\033[38;5;39m'   # Ciano
    SYS = '\033[38;5;220m'    # Amarelo
    PANIC = '\033[38;5;15m'    # Branco
    DANGER = '\033[38;5;196m'  # Vermelho
    RESET = '\033[0m'          # Reset

class NativeCipher:
    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        return hashlib.pbkdf2_hmac('sha256', password.encode(ENCODING), salt, 100000)

    @classmethod
    def encrypt(cls, text: str, password: str) -> str:
        if not password: return text

        salt = secrets.token_bytes(16)
        iv = secrets.token_bytes(16)
        key = cls.derive_key(password, salt)

        plaintext = text.encode(ENCODING)
        ciphertext = bytearray()
        counter = 0

        for i in range(len(plaintext)):
            if i % 32 == 0:
                keystream_block = hashlib.sha256(key + iv + counter.to_bytes(4, 'big')).digest()
                counter += 1
            ciphertext.append(plaintext[i] ^ keystream_block[i % 32])

        ciphertext = bytes(ciphertext)

        mac = hmac.new(key, iv + ciphertext, hashlib.sha256).digest()

        final_payload = salt + iv + mac + ciphertext
        return base64.b64encode(final_payload).decode(ENCODING)

    @classmethod
    def decrypt(cls, b64_text: str, password: str) -> str:
        if not password: return b64_text
        try:
            raw_data = base64.b64decode(b64_text)

            if len(raw_data) < 65:
                raise ValueError("Payload corrompido")

            salt = raw_data[:16]
            iv = raw_data[16:32]
            mac_received = raw_data[32:64]
            ciphertext = raw_data[64:]

            key = cls.derive_key(password, salt)

            mac_calculated = hmac.new(key, iv + ciphertext, hashlib.sha256).digest()
            if not hmac.compare_digest(mac_received, mac_calculated):
                return f"{Color.DANGER}🚨 [ALERTA] Mensagem adulterada na rede! Ignorada.{Color.RESET}"

            plaintext = bytearray()
            counter = 0
            for i in range(len(ciphertext)):
                if i % 32 == 0:
                    keystream_block = hashlib.sha256(key + iv + counter.to_bytes(4, 'big')).digest()
                    counter += 1
                plaintext.append(ciphertext[i] ^ keystream_block[i % 32])

            return plaintext.decode(ENCODING)
        except Exception:
            return f"🔐 {Color.SYS}[Mensagem Ilegível ou Senha Incorreta]{Color.RESET}"

# --- KERNEL ---
class ChatClient:
    def __init__(self, host: str, port: int, username: str, secret_key: str, room_id: str):
        self.server_address: Tuple[str, int] = (host, port)
        self.username: str = username
        self.secret_key: str = secret_key
        self.room_id: str = room_id
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.is_running: bool = False
        self.local_history: List[str] = []
        self.active_users: Set[str] = set()

    @staticmethod
    def clear_screen() -> None:
        os.system('cls' if os.name == 'nt' else 'clear')

    def trigger_panic_button(self) -> None:
        self.clear_screen()
        print(f"{Color.PANIC}Microsoft Windows [versão 10.0.19045]")
        print("(c) Microsoft Corporation. Todos os direitos reservados.\n")
        print("C:\\Windows\\system32> chkdsk /f /r")
        print("O tipo do sistema de arquivos é NTFS.")
        print("Desmontando o volume para verificação de clusters defeituosos...")
        print("Estágio 1: Examinando a estrutura básica do sistema de arquivos... 27% concluído.")

    def display_help(self) -> None:
        print(f"\n{Color.SYS}═══ COMANDOS OCULTOS DO TERMINAL ═══{Color.RESET}")
        print(f"{Color.USER}/clear{Color.RESET}   -> Limpa o histórico visual do chat na sua tela.")
        print(f"{Color.USER}/panic{Color.RESET}   -> Disfarça o terminal instantaneamente.")
        print(f"{Color.USER}/history{Color.RESET} -> Recupera as últimas 50 mensagens.")
        print(f"{Color.USER}/info{Color.RESET}    -> Lista os usuários ativos na sala '{self.room_id}'.")
        print(f"{Color.USER}/quit{Color.RESET}    -> Desconecta da rede com segurança.")
        print(f"{Color.SYS}════════════════════════════════════{Color.RESET}\n")

    def display_info(self) -> None:
        print(f"\n{Color.SYS}👥 --- Inteligência de Rede (Sala: {self.room_id}) ---{Color.RESET}")
        print(f"Total de Nós Únicos: {len(self.active_users) + 1}")
        print(f"[{self.username}] (Você)")
        for user in sorted(self.active_users):
            print(f"[{user}]")
        print(f"{Color.SYS}──────────────────────────────────────────{Color.RESET}\n")

    def connect(self) -> None:
        try:
            self.client_socket.connect(self.server_address)
            self.is_running = True
            self.clear_screen()

            print(f"{Color.SYS}🤖 [Conexão Estabelecida]: {self.server_address[0]}:{self.server_address[1]}{Color.RESET}")
            print(f"{Color.SYS}🚪 [Sala Ativa]: {Color.USER}{self.room_id}{Color.RESET}")

            if self.secret_key:
                print(f"{Color.DANGER}🔒 [Segurança]: Suíte PBKDF2+HMAC+XOR Dinâmico Ativada.{Color.RESET}")
            print(f"{Color.SYS}💡 Digite {Color.USER}/help{Color.SYS} para ver comandos.{Color.RESET}\n")

            threading.Thread(target=self._receive_messages, daemon=True).start()

            join_msg = NativeCipher.encrypt("👋 Entrou na sala.", self.secret_key)
            payload = json.dumps({
                "room": self.room_id,
                "user": self.username,
                "msg": join_msg
            }) + "\n"
            self.client_socket.send(payload.encode(ENCODING))

            self._handle_user_input()

        except ConnectionRefusedError:
            print(f"\n{Color.DANGER}❌ [Erro de Rede]: Servidor offline ou bloqueado.{Color.RESET}")
        except Exception as e:
            print(f"\n{Color.DANGER}❌ [Erro Crítico]: {e}{Color.RESET}")
        finally:
            self.disconnect()

    def _receive_messages(self) -> None:
        buffer = ""
        while self.is_running:
            try:
                raw_data = self.client_socket.recv(BUFFER_SIZE).decode(ENCODING)
                if not raw_data:
                    break

                buffer += raw_data

                while "\n" in buffer:
                    linha, buffer = buffer.split("\n", 1)
                    if not linha.strip():
                        continue

                    try:
                        packet = json.loads(linha)

                        if packet.get("cmd") == "kick":
                            print(f"\n{Color.DANGER}🛑 [CONEXÃO ENCERRADA]: {packet.get('msg')}{Color.RESET}")
                            self.is_running = False
                            break

                        packet_room = packet.get("room", "")
                        friend_name = packet.get("user", "Desconhecido")
                        encrypted_msg = packet.get("msg", "")

                        if packet_room != self.room_id:
                            continue

                        if friend_name == self.username:
                            old_name = self.username
                            self.username = f"{self.username}_{secrets.randbelow(999)}"

                            alerta = f"\n{Color.DANGER}🚨 [CONFLITO]: O nome '{old_name}' já está em uso na sala! Você foi renomeado para '{self.username}'.{Color.RESET}\n"
                            sys.stdout.write(f"\r\033[K{alerta}")

                            self.active_users.add(friend_name)
                        else:
                            if friend_name != "Desconhecido":
                                self.active_users.add(friend_name)

                        decrypted_msg = NativeCipher.decrypt(encrypted_msg, self.secret_key)
                        timestamp = datetime.now().strftime("%H:%M")

                        formatted_msg = f"{Color.FRIEND}[{timestamp}] {friend_name}:{Color.RESET} {decrypted_msg}"
                        self.local_history.append(formatted_msg)

                    except json.JSONDecodeError:
                        formatted_msg = f"{Color.SYS}>> {linha}{Color.RESET}"
                        self.local_history.append(formatted_msg)

                    if len(self.local_history) > 50:
                        self.local_history.pop(0)

                    current_prompt = f"{Color.USER}[{self.room_id}] [{self.username}]:{Color.RESET} "
                    sys.stdout.write(f"\r\033[K{formatted_msg}\n")
                    sys.stdout.write(current_prompt)
                    sys.stdout.flush()

            except:
                break

        if self.is_running:
            print(f"\n{Color.DANGER}❌ [Sistema]: Conexão perdida.{Color.RESET}")
            self.is_running = False
            sys.stdout.write("\nPressione ENTER para sair...")
            sys.stdout.flush()

    def _handle_user_input(self) -> None:
        while self.is_running:
            try:
                current_prompt = f"{Color.USER}[{self.room_id}] [{self.username}]:{Color.RESET} "
                sys.stdout.write(current_prompt)
                sys.stdout.flush()

                message = input().strip()

                if not self.is_running:
                    break

                if not message:
                    continue

                cmd_check = message.lower()

                if cmd_check in ('/quit', '/exit'):
                    self.is_running = False
                    break
                elif cmd_check == '/clear':
                    self.clear_screen()
                    continue
                elif cmd_check == '/help':
                    self.display_help()
                    continue
                elif cmd_check == '/panic':
                    self.trigger_panic_button()
                    continue
                elif cmd_check == '/info':
                    self.display_info()
                    continue
                elif cmd_check == '/history':
                    self.clear_screen()
                    for msg in self.local_history: print(msg)
                    print(f"{Color.SYS}─────────────────────────────────────────{Color.RESET}\n")
                    continue

                timestamp = datetime.now().strftime("%H:%M")
                sys.stdout.write(f"\033[F\r\033[K{Color.USER}[{timestamp}] Você:{Color.RESET} {message}\n")

                encrypted_body = NativeCipher.encrypt(message, self.secret_key)

                payload = json.dumps({
                    "room": self.room_id,
                    "user": self.username,
                    "msg": encrypted_body
                }) + "\n"

                self.client_socket.send(payload.encode(ENCODING))

            except KeyboardInterrupt:
                self.is_running = False
                break
            except Exception:
                break

    def disconnect(self) -> None:
        self.is_running = False
        try:
            self.client_socket.close()
        except: pass
        os._exit(0)

# --- BOOT ---
if __name__ == "__main__":
    ChatClient.clear_screen()
    print(f"{Color.USER}========================================")
    print(f"    🕶️  MATRIX-LINK CLIENT ADVANCED  ")
    print(f"========================================{Color.RESET}\n")

    user_alias = input("👤 ID do Terminal (Seu Apelido): ").strip() or "Anon_" + str(int(time.time()))[-4:]
    host_input = input("🌐 IP/Link do Host [Enter = Localhost]: ").strip()

    room_input = input("💬 ID da Sala [Enter = Global]: ").strip() or "Global"

    print(f"\n{Color.SYS}Deixe em branco para um chat público sem criptografia.{Color.RESET}")
    encryption_key = input("🔑 Chave de Criptografia (Senha): ").strip()

    if ":" in host_input:
        try:
            target_ip, port_str = host_input.split(":", 1)
            target_port = int(port_str)
        except ValueError:
            target_ip, target_port = "127.0.0.1", DEFAULT_PORT
    else:
        target_ip = host_input if host_input else "127.0.0.1"
        port_input = input(f"🚪 Porta Alvo [Enter = {DEFAULT_PORT}]: ").strip()
        target_port = int(port_input) if port_input.isdigit() else DEFAULT_PORT

    client = ChatClient(target_ip, target_port, user_alias, encryption_key, room_input)
    client.connect()
