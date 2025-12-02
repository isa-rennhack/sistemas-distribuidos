# 🚢 Batalha Naval - Multiplayer

Jogo de Batalha Naval multiplayer desenvolvido em Python com Pygame e sockets TCP.

## 📋 Características

- Interface gráfica com Pygame
- Preview visual ao posicionar navios
- Rotação de navios com tecla R
- Suporte a múltiplas salas simultâneas
- Emojis para melhor visualização (⚓ 💥 💧)

## 🎮 Como Jogar

### 1. Iniciar o Servidor

```bash
python3 server.py
```

### 2. Iniciar os Clientes (2 jogadores)

Em terminais separados:

```bash
python3 client_pygame.py
python3 client_pygame.py
```

### 3. Gameplay

1. **Posicionar navios**: Clique no seu tabuleiro para posicionar (5 navios: 5, 4, 3, 3, 2 células)
2. **Girar navio**: Pressione tecla **R** para alternar entre horizontal/vertical
3. **Conectar**: Após posicionar todos os navios, clique em "CONECTAR"
4. **Atacar**: Quando for sua vez, clique no tabuleiro inimigo para atacar
5. **Vencer**: Destrua todos os navios do oponente!

## 🌐 Configuração de Rede

### ⚡ Novo! Conexão Automática em Rede

O jogo agora **detecta automaticamente o IP real da máquina** e permite conexões de outras máquinas!

### 📍 Descobrir o IP do Servidor

Na máquina que vai hospedar o servidor:

```bash
python3 get_ip.py
```

Isso mostrará seu IP na rede local (ex: `192.168.1.100`)

### 🎮 Jogar em Máquinas Diferentes

**1. Iniciar o servidor:**
```bash
python3 server.py
```
O servidor mostrará automaticamente o IP para conexão.

**2. Conectar clientes de outras máquinas:**

**Opção A - Passar IP como argumento:**
```bash
python3 client_pygame.py 192.168.1.100
```

**Opção B - Digitar quando solicitado:**
```bash
python3 client_pygame.py
# Digite o IP do servidor quando solicitado
```

### 🏠 Testar na Mesma Máquina

Pressione Enter quando o cliente pedir o IP (usará localhost automaticamente).

### 🔥 Configurar Firewall

**macOS:**
```bash
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3
```

**Linux:**
```bash
sudo ufw allow 65432/tcp
```

**Windows:**
- Painel de Controle → Firewall → Permitir porta 65432/TCP

### Internet (redes diferentes)

Para jogar pela internet você precisa:

1. **No servidor**: 
   - Usar `HOST = '0.0.0.0'`
   - Configurar **port forwarding** no roteador (porta 65432 → IP do servidor)

2. **No cliente**:
   - Usar o IP público do servidor
   - Descobrir IP público em: https://whatismyipaddress.com/

**Alternativa fácil**: Use [ngrok](https://ngrok.com/) para expor o servidor:
```bash
ngrok tcp 65432
```

## 🎯 Símbolos do Jogo

- ⚓ = Navio intacto (seu tabuleiro)
- 💥 = Acerto
- 💧 = Erro (água)
- 🟩 = Preview válido (pode posicionar)
- 🟥 = Preview inválido (não pode posicionar)

## 📂 Arquivos

- `server.py` - Servidor do jogo (gerencia salas e lógica)
- `client_pygame.py` - Cliente com interface gráfica
- `config.py` - Arquivo de configuração de rede (referência)

## 🔄 Sistema de Salas

- Salas são criadas automaticamente para cada 2 jogadores
- IDs das salas são sequenciais (Sala 1, Sala 2, ...)
- Ao reiniciar o servidor, a numeração volta do zero
- Múltiplas partidas podem ocorrer simultaneamente

## 🛠️ Requisitos

- Python 3.7+
- Pygame

```bash
pip install pygame
```

## 🚀 Início Rápido (Script Auxiliar)

Para facilitar, use o script de inicialização:

```bash
./start.sh
```

Escolha uma opção:
1. Iniciar servidor
2. Iniciar cliente (mesma máquina)
3. Iniciar cliente (rede - digite o IP)
4. Ver IP da máquina
5. Sair

## 🐛 Solução de Problemas

**Emojis não aparecem?**
- Os emojis usam a fonte do sistema (Apple Color Emoji no macOS)
- Se não funcionar, o jogo usa formas geométricas alternativas

**Erro de conexão?**
- Verifique se o servidor está rodando
- Confirme que HOST e PORT estão corretos
- Em rede local, verifique firewall

**Jogo travado?**
- Feche tudo e reinicie servidor primeiro, depois clientes
- Certifique-se de ter exatamente 2 clientes por partida
