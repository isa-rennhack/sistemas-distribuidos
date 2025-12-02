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

### Mesma Máquina (Localhost)
**Padrão atual** - não precisa mudar nada!
- Servidor e clientes no mesmo computador
- `HOST = '127.0.0.1'`

### Rede Local (mesma Wi-Fi/LAN)

**No servidor (`server.py`):**
```python
HOST = '0.0.0.0'  # Escuta em todas as interfaces
```

**No cliente (`client_pygame.py`):**
```python
HOST = '192.168.1.XXX'  # IP local do servidor
```

Para descobrir o IP do servidor:
- **macOS/Linux**: `ifconfig | grep "inet "`
- **Windows**: `ipconfig`

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
