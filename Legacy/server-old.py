import socket
import threading

clientes_conectados = []

def transmitir_mensagem(mensagem_criptografada, remetente):
    for cliente in clientes_conectados:
        if cliente != remetente:
            try:
                cliente.send(mensagem_criptografada.encode('utf-8'))
            except:
                cliente.close()
                if cliente in clientes_conectados:
                    clientes_conectados.remove(cliente)

def gerenciar_cliente(conn, addr):
    print(f"\n[Nova Conexão] IP {addr[0]}:{addr[1]} entrou no chat.")
    clientes_conectados.append(conn)

    while True:
        try:
            mensagem_criptografada = conn.recv(1024).decode('utf-8')
            if not mensagem_criptografada:
                break

            transmitir_mensagem(mensagem_criptografada, conn)

        except:
            break

    print(f"\n[Desconectado] IP {addr[0]}:{addr[1]} saiu do chat.")
    if conn in clientes_conectados:
        clientes_conectados.remove(conn)
    conn.close()

def iniciar_servidor():
    print("-" * 40)
    print(" SERVIDOR HUB CEGO - MÓDULO DE EMERGÊNCIA ")
    print("-" * 40)

    porta = 0
    while True:
        entrada_porta = input("🚪 Porta para abrir [Enter para 5555]: ").strip()
        if not entrada_porta:
            porta = 5555
            break
        elif entrada_porta.isdigit():
            porta = int(entrada_porta)
            break
        else:
            print("[Aviso] A porta precisa ser um número válido!")

    print("-" * 40)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind(('0.0.0.0', porta))
        server.listen()

        print(f"[Iniciando] Servidor HUB aberto na porta {porta}!")
        print(f"[Aguardando] Roteamento invisível ativado. As mensagens não serão lidas aqui...")
    except Exception as e:
        print(f"\n[Erro] Falha ao iniciar o servidor: {e}")
        return

    while True:
        conn, addr = server.accept()
        threading.Thread(target=gerenciar_cliente, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    iniciar_servidor()
