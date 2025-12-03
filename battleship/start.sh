#!/bin/bash

# Script para facilitar o início rápido do jogo

echo "🚢 BATALHA NAVAL - Setup Rápido"
echo "================================"
echo ""

# Descobre o IP
IP=$(python3 -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8', 80)); print(s.getsockname()[0]); s.close()")

echo "📍 Seu IP na rede: $IP"
echo ""
echo "Escolha uma opção:"
echo ""
echo "  1) Iniciar SERVIDOR"
echo "  2) Iniciar CLIENTE (local)"
echo "  3) Iniciar CLIENTE (rede)"
echo "  4) Sair"
echo ""
read -p "Opção: " choice

case $choice in
    1)
        echo ""
        echo "🎮 Iniciando servidor..."
        echo "Outros jogadores podem conectar usando: python3 client_pygame.py $IP"
        echo ""
        python3 server.py
        ;;
    2)
        echo ""
        echo "🎮 Iniciando cliente (localhost)..."
        python3 client_pygame.py 127.0.0.1
        ;;
    3)
        echo ""
        read -p "Digite o IP do servidor: " server_ip
        echo "🎮 Conectando a $server_ip..."
        python3 client_pygame.py $server_ip
        ;;
    4)
        echo "👋 Até logo!"
        exit 0
        ;;
    *)
        echo "❌ Opção inválida!"
        exit 1
        ;;
esac
