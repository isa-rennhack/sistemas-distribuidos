import socket
import threading
import json

HOST = '127.0.0.1'
PORT = 65432

rooms = []  # Lista de salas de jogo
room_lock = threading.Lock()

class GameRoom:
    def __init__(self, room_id):
        self.room_id = room_id
        self.clients = []
        self.boards = {}
        self.turn = 0
        self.game_started = False
        
    def is_full(self):
        return len(self.clients) >= 2
    
    def add_client(self, conn):
        player_id = len(self.clients)
        self.clients.append(conn)
        return player_id

def create_board():
    # Cria um tabuleiro 5x5 vazio
    return [['~' for _ in range(5)] for _ in range(5)]

def get_available_room():
    """Encontra uma sala disponível ou cria uma nova"""
    with room_lock:
        for room in rooms:
            if not room.is_full():
                return room
        
        # Cria nova sala
        new_room = GameRoom(len(rooms))
        rooms.append(new_room)
        return new_room

def handle_client(conn, addr, room, player_id):
    try:
        conn.sendall((json.dumps({"type": "info", "message": f"Bem-vindo à Sala {room.room_id + 1}, Jogador {player_id+1}!"}) + "\n").encode())
        conn.sendall((json.dumps({"type": "player_id", "id": player_id}) + "\n").encode())
        
        # Recebe o tabuleiro do cliente
        data = conn.recv(1024)
        if data:
            message = data.decode().strip()
            if message:
                board_msg = json.loads(message)
                if board_msg["type"] == "board":
                    room.boards[player_id] = board_msg["board"]
        
        # Espera ambos jogadores da sala conectarem e enviarem tabuleiros
        while not room.is_full() or len(room.boards) < 2:
            pass
        
        if not room.game_started:
            room.game_started = True
            for c in room.clients:
                c.sendall((json.dumps({"type": "game_start"}) + "\n").encode())
                c.sendall((json.dumps({"type": "info", "message": "Ambos conectados! O jogo começou."}) + "\n").encode())
        
        # Loop principal do jogo
        while True:
            if room.turn == player_id:
                conn.sendall((json.dumps({"type": "your_turn"}) + "\n").encode())
                data = conn.recv(1024)
                if not data:
                    break
                
                message = data.decode().strip()
                if not message:
                    continue
                    
                move = json.loads(message)
                if move["type"] == "attack":
                    target_id = 1 - player_id
                    x, y = move["x"], move["y"]
                    
                    # Verifica o ataque
                    hit = room.boards[target_id][x][y] == "N"
                    
                    # Atualiza o tabuleiro
                    if hit:
                        room.boards[target_id][x][y] = "X"
                    else:
                        room.boards[target_id][x][y] = "O"
                    
                    # Envia resultado do ataque para quem atacou
                    conn.sendall((json.dumps({
                        "type": "attack_result",
                        "x": x,
                        "y": y,
                        "hit": hit
                    }) + "\n").encode())
                    
                    # Notifica o outro jogador sobre o ataque sofrido
                    other_conn = room.clients[target_id]
                    other_conn.sendall((json.dumps({
                        "type": "enemy_attack",
                        "x": x,
                        "y": y,
                        "hit": hit
                    }) + "\n").encode())
                    
                    # Verifica se o jogo acabou (todos navios do alvo destruídos)
                    target_ships = sum(row.count("N") for row in room.boards[target_id])
                    
                    if target_ships == 0:
                        # Jogo acabou - jogador atual venceu
                        for i, c in enumerate(room.clients):
                            c.sendall((json.dumps({
                                "type": "game_over",
                                "winner": player_id
                            }) + "\n").encode())
                        break
                    
                    # Alterna o turno
                    room.turn = target_id
                    
                    # Notifica próximo jogador que é a vez dele
                    room.clients[target_id].sendall((json.dumps({"type": "your_turn"}) + "\n").encode())
                    conn.sendall((json.dumps({"type": "wait"}) + "\n").encode())
            else:
                # Aguarda vez
                import time
                time.sleep(0.1)
    
    except Exception as e:
        print(f"Erro no cliente {player_id} da sala {room.room_id}: {e}")
    finally:
        conn.close()

def main():
    print(f"🎮 Servidor de Batalha Naval rodando em {HOST}:{PORT}")
    print("📌 Aguardando conexões... (Salas criadas automaticamente para cada 2 jogadores)")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        
        while True:
            conn, addr = s.accept()
            print(f"✅ Nova conexão de {addr}")
            
            # Encontra ou cria uma sala disponível
            room = get_available_room()
            player_id = room.add_client(conn)
            
            print(f"   → Jogador {player_id + 1} adicionado à Sala {room.room_id + 1}")
            
            if room.is_full():
                print(f"🎯 Sala {room.room_id + 1} completa! Jogo pode começar.")
            
            # Cria thread para lidar com o cliente
            threading.Thread(target=handle_client, args=(conn, addr, room, player_id), daemon=True).start()

if __name__ == "__main__":
    main()
