#!/usr/bin/env python3
"""
Script auxiliar para descobrir o IP da máquina na rede local
"""
import socket

def get_local_ip():
    """Obtém o IP real da máquina na rede local"""
    try:
        # Cria socket temporário para descobrir IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Conecta ao DNS do Google (não envia dados)
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "Não foi possível determinar o IP"

if __name__ == "__main__":
    ip = get_local_ip()
    print("="*50)
    print("🌐 SEU IP NA REDE LOCAL")
    print("="*50)
    print(f"\n📍 IP: {ip}")
    print(f"\n💡 Para iniciar o servidor:")
    print(f"   python3 server.py")
    print(f"\n💡 Para conectar de outra máquina:")
    print(f"   python3 client_pygame.py {ip}")
    print("\n" + "="*50)
