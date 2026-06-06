import socket
import threading

def criptografar_descriptografar(texto, chave):
    return "".join(chr(ord(c) ^ ord(chave[i % len(chave)])) for i, c in enumerate(texto))

def receber_mensagens(client_socket, chave_secreta):
    while True:
        try:
            mensagem_criptografada = client_socket.recv(1024).decode('utf-8')
            if not mensagem_criptografada:
                break
            mensagem_limpa = criptografar_descriptografar(mensagem_criptografada, chave_secreta)
            
            print(f"\n{mensagem_limpa}")
            print("[Você]: ", end="", flush=True)
            
        except Exception:
            print("\n[Erro] Conexão perdida com o servidor.")
            break

def iniciar_cliente():
    print("-" * 40)
    print(" TERMINAL SECRETO - MÓDULO DE EMERGÊNCIA ")
    print("-" * 40)
    
    ip_servidor = input("🌐 IP do Servidor [Enter para 127.0.0.1]: ").strip()
    if not ip_servidor:
        ip_servidor = "127.0.0.1"
        
    porta = 0
    while True:
        entrada_porta = input("🚪 Porta [Enter para 5555]: ").strip()
        if not entrada_porta:
            porta = 5555
            break
        elif entrada_porta.isdigit():
            porta = int(entrada_porta)
            break
        else:
            print("[Aviso] A porta precisa ser um número válido! Tente novamente.")
    
    nome = ""
    while not nome.strip():
        nome = input("👤 Seu Apelido: ").strip()
        if not nome:
            print("[Aviso] O apelido não pode ficar em branco!")
            
    chave_secreta = ""
    while len(chave_secreta) < 8:
        chave_secreta = input("🔑 Chave de Acesso (Mínimo 8 caracteres): ").strip()
        if len(chave_secreta) < 8:
            print("[Aviso] Chave muito curta! Digite pelo menos 8 caracteres válidos.")
    
    print("-" * 40)
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((ip_servidor, porta))
        print(f"\n[Conectado no IP {ip_servidor}:{porta}]")
        print(f"Bem-vindo, {nome}! (Digite 'sair' para desconectar)")
    except Exception as e:
        print(f"\n[Erro] Não foi possível conectar: {e}")
        return
    
    threading.Thread(target=receber_mensagens, args=(client, chave_secreta), daemon=True).start()
    
    while True:
        mensagem = input("[Você]: ")
        
        if mensagem.lower() == 'sair':
            print("Desconectando...")
            client.close()
            break
            
        if mensagem.strip() != "":
            try:
                mensagem_formatada = f"[{nome}]: {mensagem}"
                mensagem_segura = criptografar_descriptografar(mensagem_formatada, chave_secreta)
                
                client.send(mensagem_segura.encode('utf-8'))
            except Exception:
                print("\n[Erro] Falha ao enviar mensagem.")
                break

if __name__ == "__main__":
    iniciar_cliente()
