## 🛠️ 1. Resolução de Problemas (Troubleshooting)

**❌ Erro: Conexão Perdida ou Servidor Desligado**
* **Causa (Ngrok):** O host esqueceu de executar o `matrix-server.py` antes de abrir o Ngrok, ou o link foi atualizado após o túnel ser reiniciado.
* **Solução:** O host deve verificar se o servidor está ativo. O cliente deve confirmar se o endereço digitado corresponde ao túnel atual.

* **Causa (Rede Local):** O Firewall do sistema operacional está bloqueando a porta 5555, ou a rede Wi-Fi possui "Isolamento de AP" (comum em redes públicas ou de faculdades).
* **Solução:** Permita o Python nas conexões de entrada do Firewall do Windows/Linux. Caso seja bloqueio do roteador corporativo, utilizem o Ngrok em vez da rede local.

**🔣 Mensagens criptografadas ilegíveis (Ex: `🔐 [Mensagem Criptografada - Ilegível...]`)**
* **Causa:** Conexão bem-sucedida ao servidor, mas divergência de senha (*Password*).
* **Solução:** Utilize o comando `/quit` para desconectar. Abra o cliente (app) novamente garantindo que todas as partes digitem exatamente a mesma senha para a sala (respeitando letras maiúsculas e minúsculas).
