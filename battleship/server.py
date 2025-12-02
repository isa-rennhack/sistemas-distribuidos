import socket
import threading
import json

import socket as sock_module

def get_local_ip():
    """Obtém o IP real da máquina na rede local"""
    try:
        # Cria socket temporário para descobrir IP local
        s = sock_module.socket(sock_module.AF_INET, sock_module.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Conecta ao DNS do Google (não envia dados)
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return '0.0.0.0'  # Aceita conexões de qualquer interface

HOST = get_local_ip()
PORT = 65432

rooms = []
room_lock = threading.Lock()

class GameRoom:
    def __init__(self, room_id):
        self.room_id = room_id
        self.clients = []
        self.boards = {}
        self.turn = 0
        self.game_started = False
        self.active_players = [True, True]  # rastreia se cada jogador está ativo
        
    def is_full(self):
        return len(self.clients) >= 2
    
    def add_client(self, conn):
        player_id = len(self.clients)
        self.clients.append(conn)
        return player_id
    
    def disconnect_player(self, player_id):
        """Marca jogador como desconectado e notifica o outro"""
        self.active_players[player_id] = False
        other_id = 1 - player_id
        
        # notifica o outro jogador sobre a desconexão
        if other_id < len(self.clients) and self.active_players[other_id]:
            try:
                self.clients[other_id].sendall((json.dumps({
                    "type": "opponent_disconnected",
                    "message": "Seu oponente desconectou. Você venceu por W.O.!"
                }) + "\n").encode())
            except:
                pass

def create_board():
    return [['~' for _ in range(10)] for _ in range(10)]

def get_available_room():
    """Encontra uma sala disponível ou cria uma nova"""
    with room_lock:
        for room in rooms:
            if not room.is_full():
                return room
        
        new_room = GameRoom(len(rooms))
        rooms.append(new_room)
        return new_room

def handle_client(conn, addr, room, player_id):
    try:
        conn.sendall((json.dumps({"type": "info", "message": f"Bem-vindo à Sala {room.room_id + 1}, Jogador {player_id+1}!"}) + "\n").encode())
        conn.sendall((json.dumps({"type": "player_id", "id": player_id}) + "\n").encode())
        
        # recebe o tabuleiro do cliente
        data = conn.recv(1024)
        if not data:
            raise ConnectionError("Cliente desconectou antes de enviar o tabuleiro")
            
        message = data.decode().strip()
        if message:
            board_msg = json.loads(message)
            if board_msg["type"] == "board":
                room.boards[player_id] = board_msg["board"]
        
        # espera ambos jogadores da sala conectarem e enviarem tabuleiros
        while not room.is_full() or len(room.boards) < 2:
            if not room.active_players[player_id]:
                return  # jogador desconectou durante espera
            pass
        
        if not room.game_started:
            room.game_started = True
            for c in room.clients:
                c.sendall((json.dumps({"type": "game_start"}) + "\n").encode())
                c.sendall((json.dumps({"type": "info", "message": "Ambos conectados! O jogo começou."}) + "\n").encode())
        
        # loop principal do jogo
        while True:
            # verifica se o oponente ainda está conectado
            other_id = 1 - player_id
            if not room.active_players[other_id]:
                break
                
            if room.turn == player_id:
                conn.sendall((json.dumps({"type": "your_turn"}) + "\n").encode())
                data = conn.recv(1024)
                if not data:
                    raise ConnectionError("Cliente desconectou durante o jogo")
                
                message = data.decode().strip()
                if not message:
                    continue
                    
                move = json.loads(message)
                if move["type"] == "attack":
                    target_id = 1 - player_id
                    x, y = move["x"], move["y"]
                    
                    # verifica o ataque
                    hit = room.boards[target_id][x][y] == "N"
                    
                    # atualiza o tabuleiro
                    if hit:
                        room.boards[target_id][x][y] = "X"
                    else:
                        room.boards[target_id][x][y] = "O"
                    
                    # envia resultado do ataque para quem atacou
                    conn.sendall((json.dumps({
                        "type": "attack_result",
                        "x": x,
                        "y": y,
                        "hit": hit
                    }) + "\n").encode())
                    
                    # notifica o outro jogador sobre o ataque sofrido
                    other_conn = room.clients[target_id]
                    other_conn.sendall((json.dumps({
                        "type": "enemy_attack",
                        "x": x,
                        "y": y,
                        "hit": hit
                    }) + "\n").encode())
                    
                    # verifica se o jogo acabou
                    target_ships = sum(row.count("N") for row in room.boards[target_id])
                    
                    if target_ships == 0:
                        for i, c in enumerate(room.clients):
                            c.sendall((json.dumps({
                                "type": "game_over",
                                "winner": player_id
                            }) + "\n").encode())
                        break
                    
                    # alterna o turno
                    room.turn = target_id
                    
                    room.clients[target_id].sendall((json.dumps({"type": "your_turn"}) + "\n").encode())
                    conn.sendall((json.dumps({"type": "wait"}) + "\n").encode())
            else:
                import time
                time.sleep(0.1)
    
    except (ConnectionError, ConnectionResetError, BrokenPipeError) as e:
        print(f"Jogador {player_id + 1} da Sala {room.room_id + 1} desconectou: {e}")
        room.disconnect_player(player_id)
    except Exception as e:
        print(f"Erro no cliente {player_id} da sala {room.room_id}: {e}")
        room.disconnect_player(player_id)
    finally:
        try:
            conn.close()
        except:
            pass
        print(f"Conexão com Jogador {player_id + 1} da Sala {room.room_id + 1} encerrada")

def main():
    print("="*60)
    print("🎮 SERVIDOR DE BATALHA NAVAL")
    print("="*60)
    print(f"\n📡 Servidor rodando em: {HOST}:{PORT}")
    print(f"\n💡 Para conectar de outra máquina, use este IP: {HOST}")
    print(f"   Execute no cliente: python3 client_pygame.py {HOST}")
    print("\n📌 Aguardando conexões...")
    print("   (Salas criadas automaticamente para cada 2 jogadores)\n")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # permite reusar a porta
        s.bind(('0.0.0.0', PORT))  # Aceita conexões de qualquer interface de rede
        s.listen()
        
        while True:
            conn, addr = s.accept()
            print(f"Nova conexão de {addr}")
            
            room = get_available_room()
            player_id = room.add_client(conn)
            
            print(f" → Jogador {player_id + 1} adicionado à Sala {room.room_id + 1}")
            
            if room.is_full():
                print(f"Sala {room.room_id + 1} completa! Jogo pode começar.")
            
            threading.Thread(target=handle_client, args=(conn, addr, room, player_id), daemon=True).start()

if __name__ == "__main__":
    main()