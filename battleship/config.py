# Configuração de rede para o jogo de Batalha Naval

# ====== CONFIGURAÇÕES DO SERVIDOR ======

# Modo LOCAL (mesma máquina):
# SERVER_HOST = '127.0.0.1'

# Modo REDE LOCAL (computadores na mesma rede Wi-Fi/LAN):
# SERVER_HOST = '0.0.0.0'  # Servidor escuta em todas as interfaces
# No cliente, use o IP local do servidor (ex: '192.168.1.100')

# Para descobrir o IP local no servidor, use:
# macOS/Linux: ifconfig | grep "inet "
# Windows: ipconfig

SERVER_HOST = '127.0.0.1'  # Padrão: localhost
SERVER_PORT = 65432

# ====== CONFIGURAÇÕES DO CLIENTE ======
# IP do servidor para conectar
CLIENT_HOST = '127.0.0.1'  # Mude para o IP do servidor se estiver em rede local
CLIENT_PORT = 65432

# ====== NOTAS SOBRE REDE EXTERNA (Internet) ======
# Para jogar pela internet (redes diferentes):
# 1. No servidor: use '0.0.0.0'
# 2. Configure port forwarding no roteador (porta 65432 -> IP do servidor)
# 3. No cliente: use o IP público do servidor
# 4. Alternativa fácil: use ngrok ou serviços similares para expor o servidor
