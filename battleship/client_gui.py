import socket
import json
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog

HOST = '127.0.0.1'
PORT = 65432

class BattleshipGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Batalha Naval")
        self.master.geometry("800x600")
        
        self.socket = None
        self.my_board = [['~' for _ in range(5)] for _ in range(5)]
        self.enemy_board = [['~' for _ in range(5)] for _ in range(5)]
        self.ships_placed = 0
        self.game_started = False
        self.my_turn = False
        self.player_id = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = tk.Label(main_frame, text="BATALHA NAVAL", font=("Arial", 20, "bold"))
        title_label.pack(pady=10)
        
        # Status
        self.status_label = tk.Label(main_frame, text="Posicione seus 3 navios no tabuleiro da esquerda", 
                                     font=("Arial", 12), fg="blue")
        self.status_label.pack(pady=5)
        
        # Frame dos tabuleiros
        boards_frame = tk.Frame(main_frame)
        boards_frame.pack(pady=10)
        
        # Tabuleiro do jogador (esquerda)
        left_frame = tk.Frame(boards_frame)
        left_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(left_frame, text="SEU TABULEIRO", font=("Arial", 14, "bold")).pack(pady=5)
        self.my_buttons = []
        my_grid = tk.Frame(left_frame)
        my_grid.pack()
        
        for i in range(5):
            row = []
            for j in range(5):
                btn = tk.Button(my_grid, text="~", width=4, height=2, 
                              font=("Arial", 12), bg="lightblue",
                              command=lambda x=i, y=j: self.place_ship(x, y))
                btn.grid(row=i, column=j, padx=2, pady=2)
                row.append(btn)
            self.my_buttons.append(row)
        
        # Tabuleiro do inimigo (direita)
        right_frame = tk.Frame(boards_frame)
        right_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(right_frame, text="TABULEIRO INIMIGO", font=("Arial", 14, "bold")).pack(pady=5)
        self.enemy_buttons = []
        enemy_grid = tk.Frame(right_frame)
        enemy_grid.pack()
        
        for i in range(5):
            row = []
            for j in range(5):
                btn = tk.Button(enemy_grid, text="~", width=4, height=2,
                              font=("Arial", 12), bg="lightgray",
                              command=lambda x=i, y=j: self.attack(x, y),
                              state=tk.DISABLED)
                btn.grid(row=i, column=j, padx=2, pady=2)
                row.append(btn)
            self.enemy_buttons.append(row)
        
        # Botão de conectar
        self.connect_button = tk.Button(main_frame, text="CONECTAR AO SERVIDOR", 
                                       font=("Arial", 12), bg="green", fg="white",
                                       command=self.connect_to_server, state=tk.DISABLED)
        self.connect_button.pack(pady=10)
        
    def place_ship(self, x, y):
        if self.game_started:
            return
            
        if self.ships_placed >= 3:
            messagebox.showwarning("Aviso", "Você já posicionou todos os navios!")
            return
            
        if self.my_board[x][y] == 'N':
            messagebox.showwarning("Aviso", "Já existe um navio nesta posição!")
            return
        
        self.my_board[x][y] = 'N'
        self.my_buttons[x][y].config(text="⚓", bg="navy", fg="white")
        self.ships_placed += 1
        
        if self.ships_placed == 3:
            self.status_label.config(text="Todos os navios posicionados! Clique em CONECTAR")
            self.connect_button.config(state=tk.NORMAL)
            # Desabilita todos os botões do tabuleiro próprio
            for i in range(5):
                for j in range(5):
                    self.my_buttons[i][j].config(state=tk.DISABLED)
        else:
            self.status_label.config(text=f"Posicione mais {3 - self.ships_placed} navio(s)")
    
    def connect_to_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((HOST, PORT))
            self.connect_button.config(state=tk.DISABLED)
            self.status_label.config(text="Conectado! Aguardando outro jogador...")
            
            # Envia o tabuleiro para o servidor
            self.socket.sendall(json.dumps({
                "type": "board",
                "board": self.my_board
            }).encode())
            
            # Inicia thread para receber mensagens
            thread = threading.Thread(target=self.receive_messages, daemon=True)
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível conectar ao servidor: {e}")
    
    def receive_messages(self):
        try:
            while True:
                data = self.socket.recv(1024)
                if not data:
                    break
                
                msg = json.loads(data.decode())
                self.handle_message(msg)
        except Exception as e:
            print(f"Erro ao receber mensagem: {e}")
    
    def handle_message(self, msg):
        if msg["type"] == "info":
            self.master.after(0, lambda: self.status_label.config(text=msg["message"]))
            
        elif msg["type"] == "player_id":
            self.player_id = msg["id"]
            
        elif msg["type"] == "game_start":
            self.game_started = True
            self.master.after(0, lambda: self.status_label.config(
                text="Jogo iniciado! Aguarde sua vez...", fg="green"))
            
        elif msg["type"] == "your_turn":
            self.my_turn = True
            self.master.after(0, self.enable_enemy_board)
            self.master.after(0, lambda: self.status_label.config(
                text="SUA VEZ! Clique no tabuleiro inimigo para atacar", fg="red"))
            
        elif msg["type"] == "wait":
            self.my_turn = False
            self.master.after(0, self.disable_enemy_board)
            self.master.after(0, lambda: self.status_label.config(
                text="Aguarde o turno do adversário...", fg="blue"))
            
        elif msg["type"] == "attack_result":
            self.master.after(0, lambda: self.show_attack_result(msg))
            
        elif msg["type"] == "enemy_attack":
            self.master.after(0, lambda: self.show_enemy_attack(msg))
            
        elif msg["type"] == "game_over":
            self.master.after(0, lambda: self.show_game_over(msg))
    
    def enable_enemy_board(self):
        for i in range(5):
            for j in range(5):
                if self.enemy_board[i][j] == '~':
                    self.enemy_buttons[i][j].config(state=tk.NORMAL)
    
    def disable_enemy_board(self):
        for i in range(5):
            for j in range(5):
                self.enemy_buttons[i][j].config(state=tk.DISABLED)
    
    def attack(self, x, y):
        if not self.my_turn:
            return
            
        if self.enemy_board[x][y] != '~':
            messagebox.showwarning("Aviso", "Você já atacou esta posição!")
            return
        
        self.socket.sendall(json.dumps({
            "type": "attack",
            "x": x,
            "y": y
        }).encode())
        
        self.my_turn = False
        self.disable_enemy_board()
        self.status_label.config(text="Aguardando resposta do ataque...")
    
    def show_attack_result(self, msg):
        x, y = msg["x"], msg["y"]
        hit = msg["hit"]
        
        if hit:
            self.enemy_board[x][y] = 'X'
            self.enemy_buttons[x][y].config(text="💥", bg="red", state=tk.DISABLED)
            self.status_label.config(text="ACERTOU! Aguarde sua próxima vez...", fg="green")
        else:
            self.enemy_board[x][y] = 'O'
            self.enemy_buttons[x][y].config(text="💨", bg="white", state=tk.DISABLED)
            self.status_label.config(text="ERROU! Aguarde sua próxima vez...", fg="orange")
    
    def show_enemy_attack(self, msg):
        x, y = msg["x"], msg["y"]
        hit = msg["hit"]
        
        if hit:
            self.my_buttons[x][y].config(text="💥", bg="red")
            self.status_label.config(text="Seu navio foi atingido!", fg="red")
        else:
            self.my_buttons[x][y].config(text="💨", bg="lightblue")
    
    def show_game_over(self, msg):
        winner = msg["winner"]
        self.disable_enemy_board()
        
        if winner == self.player_id:
            messagebox.showinfo("VITÓRIA!", "🎉 Parabéns! Você venceu o jogo!")
            self.status_label.config(text="VOCÊ VENCEU! 🎉", fg="green")
        else:
            messagebox.showinfo("DERROTA", "😢 Você perdeu! Todos seus navios foram destruídos.")
            self.status_label.config(text="VOCÊ PERDEU 😢", fg="red")
        
        # Botão para fechar
        close_btn = tk.Button(self.master, text="FECHAR", command=self.master.quit,
                             font=("Arial", 12), bg="red", fg="white")
        close_btn.pack(pady=10)

def main():
    root = tk.Tk()
    app = BattleshipGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
