import socket
import threading
import json

HOST = '127.0.0.1'
PORT = 65432

clients = []
boards = {}
turn = 0
lock = threading.Lock()

def create_board():
    # Cria um tabuleiro 5x5 vazio
    return [['~' for _ in range(5)] for _ in range(5)]

def handle_client(conn, addr, player_id):
    global turn

    conn.sendall(json.dumps({"type": "info", "message": f"Bem-vindo, Jogador {player_id+1}!"}).encode())

    # Cria o tabuleiro do jogador
    boards[player_id] = create_board()

    # Espera ambos conectarem
    while len(clients) < 2:
        pass

    conn.sendall(json.dumps({"type": "info", "message": "Ambos conectados! O jogo vai começar."}).encode())

    while True:
        if turn == player_id:
            conn.sendall(json.dumps({"type": "your_turn"}).encode())
            data = conn.recv(1024)
            if not data:
                break

            move = json.loads(data.decode())
            if move["type"] == "attack":
                target_id = 1 - player_id
                x, y = move["x"], move["y"]

                hit = boards[target_id][x][y] == "N"
                boards[target_id][x][y] = "X" if hit else "O"

                # Verifica se acabou
                winner = not any("N" in row for row in boards[target_id])

                for c in clients:
                    c.sendall(json.dumps({
                        "type": "result",
                        "attacker": player_id,
                        "x": x,
                        "y": y,
                        "hit": hit,
                        "winner": winner
                    }).encode())

                if winner:
                    break

                with lock:
                    turn = target_id

    conn.close()

def main():
    global clients
    print(f"Servidor rodando em {HOST}:{PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(2)

        while len(clients) < 2:
            conn, addr = s.accept()
            player_id = len(clients)
            clients.append(conn)
            threading.Thread(target=handle_client, args=(conn, addr, player_id)).start()

if __name__ == "__main__":
    main()
