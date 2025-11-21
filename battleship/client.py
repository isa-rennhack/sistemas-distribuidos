import socket
import json

HOST = '127.0.0.1'
PORT = 65432

def print_board(board):
    print("\n  0 1 2 3 4")
    for i, row in enumerate(board):
        print(i, ' '.join(row))
    print()

def main():
    board = [['~' for _ in range(5)] for _ in range(5)]

    # Posiciona manualmente 3 navios
    for i in range(3):
        while True:
            try:
                x, y = map(int, input(f"Posicione o navio {i+1} (x y, 0-4): ").split())
                if 0 <= x < 5 and 0 <= y < 5:
                    if board[x][y] == 'N':
                        print("Já existe um navio nesta posição! Tente outra.")
                        continue
                    board[x][y] = 'N'
                    break
                else:
                    print("Coordenadas inválidas! Use valores entre 0 e 4.")
            except (ValueError, IndexError):
                print("Entrada inválida! Use o formato: x y (exemplo: 2 3)")

    print("\nSeu tabuleiro inicial:")
    print_board(board)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        while True:
            data = s.recv(1024)
            if not data:
                break

            msg = json.loads(data.decode())

            if msg["type"] == "info":
                print(msg["message"])

            elif msg["type"] == "your_turn":
                print_board(board)
                x, y = map(int, input("Sua vez! Ataque (x y): ").split())
                s.sendall(json.dumps({"type": "attack", "x": x, "y": y}).encode())

            elif msg["type"] == "result":
                if msg["attacker"] == 0:
                    who = "Jogador 1"
                else:
                    who = "Jogador 2"
                print(f"{who} atacou ({msg['x']}, {msg['y']}) -> {'ACERTOU!' if msg['hit'] else 'ERROU!'}")

                if msg["winner"]:
                    print(f"🏁 {who} venceu o jogo!")
                    break

if __name__ == "__main__":
    main()
