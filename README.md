# 🌐 Matrix-Link: Documentação e Guia de Uso

Este documento detalha os procedimentos de infraestrutura de rede necessários para rodar o chat **Matrix-Link**. O sistema suporta desde testes isolados na própria máquina até comunicação global criptografada via internet.

---

# 📋 Requisitos & Dependências

* **Linguagem:** Ter o **Python** instalado nas máquinas (tanto no servidor quanto no cliente). É recomendado a utilização da versão mais atualizada.
* **Versões Legacy & Advanced:** **Zero dependências externas.** Funcionam puramente com as bibliotecas nativas do Python (`socket`, `threading`, `json`, `base64`, `hashlib`, etc), sem a necessidade de instalar absolutamente nada.
* **Versão Release:** **Uso obrigatório do `pip install`.** Por ser a versão mais completa e robusta, ela exige a instalação de pacotes externos para gerenciar a interface gráfica, o banco de dados e a arquitetura assíncrona.

**💡 Nota de Execução:**
Os comandos descritos neste guia utilizam os arquivos principais (`matrix-client.py` e `matrix-server.py`) referentes ao Módulo Release. Caso precise acionar o plano de contingência do Módulo Advanced ou Legacy, execute os mesmos comandos substituindo os nomes dos arquivos para o módulo correspondente.

## 🗺️ Arquitetura do Projeto: Níveis de Contingência

O projeto é dividido em três módulos independentes. Eles foram desenhados para oferecer uma **degradação graciosa** do sistema: se a versão principal falhar ou for bloqueada pelo ambiente, você sempre terá uma alternativa funcional imediatamente abaixo.

---

### 🛑 1. Módulo Legacy (100%)
* **O que é:** A versão mais crua, rústica e minimalista do sistema.
* **Propósito:** Garantir a comunicação no pior cenário possível. Ele abre um canal P2P direto extremamente simples usando criptografia básica por XOR.
* **Quando usar:** Quando o tempo é escasso e você precisa colocar duas ou mais máquinas para conversar em 30 segundos, sem se importar com logs avançados, salas ou firulas visuais. É o plano de contingência definitivo: se o Python estiver instalado, ele vai rodar.

### 🛡️ 2. Módulo Advanced (100%)
* **O que é:** Uma evolução direta do módulo Legacy. Ele mantém a filosofia de **zero dependências externas** (não precisa de `pip install`), mas eleva drasticamente o nível.
* **Propósito:** Trazer segurança real e tráfego estruturado para dentro do terminal. Ele organiza os dados em pacotes JSON, cria salas dinâmicas na memória e utiliza hashes complexos para que a criptografia seja imune a análises de frequência simples.
* **Quando usar:** Quando você precisa de privacidade absoluta contra administradores de rede bisbilhoteiros e quer uma experiência de chat organizada por comandos, mas o ambiente onde você está rodando impede o download de bibliotecas externas.

### 🚀 3. Módulo Release (0%)
* **O que é:** A versão topo de linha do projeto, a mais completa, robusta e que recebe atualizações contínuas de recursos.
* **Propósito:** Entregar uma experiência de uso profissional, escalável e confortável, nos moldes de um aplicativo de mercado.
* **Quando usar:** No dia a dia. É a sua aplicação principal, construída com arquitetura assíncrona para aguentar conexões em massa, interface gráfica (GUI) moderna e intuitiva, suporte a comandos superiores, etc.

---

## 🏠 2. Uso Básico: Mesma Máquina ou Rede Local (LAN)

Para comunicação local, um computador deve assumir o papel de **Servidor** (Hospedeiro/Host) e o outro de **Cliente** (Convidado). 

### Descobrindo o IP Local (Para o Hospedeiro)
Se os computadores estiverem na mesma rede Wi-Fi ou roteador, o Hospedeiro precisa informar seu IP local para o Convidado. Abra o terminal e execute o comando referente ao seu Sistema Operacional:

**🪟 Windows (Prompt de Comando ou PowerShell):**
```bash
ipconfig
```

> Procure por "Adaptador de Rede Sem Fio" ou "Ethernet" e localize a linha que começa com **Endereço IPv4**. Seu IP será algo como `192.168.1.X` ou `10.0.0.X`.

**🐧 Linux / 🍏 macOS:**
```bash
ip a
```

*Se o comando falhar, utilize:*
```bash
ifconfig
```
> Procure pela sua interface de rede ativa (geralmente `en`, `eth` ou `wlan`). O IP estará listado ao lado de `inet` (ex: `inet 192.168.1.50`). Ignore o IP `127.0.0.1` (loopback), pois ele serve apenas para testes internos na sua própria máquina.

### Fluxo de Conexão (Rede Local)

| Papel | Ação 1: Inicialização | Ação 2: Conexão |
| :--- | :--- | :--- |
| **Hospedeiro (Servidor)** | Executa `python3 matrix-server.py` | Informa seu **IP Local** descoberto acima aos amigos. |
| **Convidado (Cliente)** | Executa `python3 matrix-client.py` | Digita o **IP Local** do amigo quando o terminal pedir. |
| **Teste Solitário (Você com você)** | Executa `python3 matrix-server.py` em um terminal | Abre outro terminal, roda o cliente e digita `127.0.0.1` (IP de loopback). |

---

## 🌍 3. Acesso Global via Internet (Tunelamento Ngrok)

Quando o **Matrix-Link** (`matrix-server.py`) é executado, ele fica restrito à sua máquina ou rede local. O Firewall e o NAT do seu roteador bloqueiam conexões externas de pessoas em outras cidades ou redes. Para contornar isso com segurança, utilizamos o **Ngrok**.

### 👤 Parte 1: Para o Host (A pessoa que vai rodar o Servidor)
Siga estes passos para tornar seu servidor acessível de qualquer lugar do mundo:

**Passo 1: Instalação:**
- Acesse [ngrok.com](https://ngrok.com/), crie uma conta gratuita, faça o download para o seu sistema operacional e extraia o arquivo baixado.

**Passo 2: Autenticação (Apenas na primeira vez):** 
- Copie o seu *Auth Token* no painel principal do site do Ngrok. Abra o terminal na pasta onde o Ngrok foi extraído e execute:
```bash
ngrok config add-authtoken [TOKEN]
```

**Passo 3: Iniciar o Matrix-Link:** 
- Execute o servidor para abrir a porta local:
```bash
python3 matrix-server.py
```

**Passo 4: Ativar o Túnel do Ngrok:** 
- Em uma **nova janela de terminal** (mantendo o servidor rodando na anterior), inicie o redirecionamento TCP:
```bash
ngrok tcp [Porta]
```

**Passo 5: Compartilhar o Link Público:**
- A tela do Ngrok exibirá o status. Localize a linha **Forwarding** (ex: `tcp://0.tcp.ngrok.io:12345 -> localhost:5555`). 
- Copie apenas a parte após o `tcp://` (neste exemplo, **`0.tcp.ngrok.io:12345`**) e envie para seus amigos.

> ⚠️ **Aviso Crítico:** Em contas gratuitas, toda vez que você reinicia o Ngrok, os números da porta final mudam. É necessário enviar o link atualizado para o grupo.

### 👥 Parte 2: Para os Convidados (Pessoas entrando no chat)
O processo para quem vai apenas se conectar é imediato. **Não é necessário instalar o Ngrok.**

**Passo 1: Executar o Cliente (app)**
- Abra o terminal na pasta do projeto e inicie o chat:
```bash
python matrix-client.py
```

**Passo 2: Credenciais**
* **🖥️ Terminal ID (Login):** Mande as informações necessárias.
* **🌎 Host IP/Link:** Cole exatamente o link ou ip que o Host forneceu (ex: `0.tcp.ngrok.io:12345` ou `10.0.0.X`)
* **🔑 Password:** Digite a senha da sala. (Todos devem inserir a *mesma* senha).
* **🔒 Room ID:** Dê um nome ou ID numérico para a sua sala.

---

## ❓ Problemas ou Dúvidas?
Se você tiver dificuldades quanto ao uso do **Matrix-Link**, consulte o [Guia de Resolução de Problemas](./TROUBLESHOOTING.md) para ver as instruções detalhadas.

---

# 📝 Contribuição
Sinta-se à vontade para abrir uma Issue ou enviar um Pull Request para melhorias!
