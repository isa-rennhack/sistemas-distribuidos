import socket
import json
import threading
import pygame
import sys

HOST = '127.0.0.1'
PORT = 65432

# Configurações
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
CELL_SIZE = 60
BOARD_MARGIN = 50
FPS = 60

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 150, 255)
DARK_BLUE = (30, 60, 150)
RED = (255, 50, 50)
GREEN = (50, 200, 50)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)
YELLOW = (255, 200, 0)
ORANGE = (255, 150, 0)

class BattleshipGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Batalha Naval")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.socket = None
        self.my_board = [['~' for _ in range(5)] for _ in range(5)]
        self.enemy_board = [['~' for _ in range(5)] for _ in range(5)]
        self.ships_placed = 0
        self.game_started = False
        self.connected = False
        self.my_turn = False
        self.player_id = None
        self.status_message = "Clique para posicionar seus 3 navios no tabuleiro esquerdo"
        self.status_color = BLUE
        
        # Posições dos tabuleiros
        self.my_board_x = 50
        self.my_board_y = 150
        self.enemy_board_x = 500
        self.enemy_board_y = 150
        
        # Botão conectar
        self.connect_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, 600, 200, 50)
        self.connect_button_enabled = False
        
    def draw_board(self, board, x, y, clickable=False, is_enemy=False):
        """Desenha um tabuleiro"""
        for i in range(5):
            for j in range(5):
                cell_x = x + j * CELL_SIZE
                cell_y = y + i * CELL_SIZE
                rect = pygame.Rect(cell_x, cell_y, CELL_SIZE, CELL_SIZE)
                
                # Cor de fundo da célula
                cell_value = board[i][j]
                if cell_value == '~':
                    color = LIGHT_GRAY if not is_enemy else GRAY
                elif cell_value == 'N':
                    color = DARK_BLUE
                elif cell_value == 'X':
                    color = RED
                elif cell_value == 'O':
                    color = WHITE
                else:
                    color = LIGHT_GRAY
                
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, BLACK, rect, 2)
                
                # Símbolos
                if cell_value == 'N' and not is_enemy:
                    text = self.font.render("⚓", True, WHITE)
                    text_rect = text.get_rect(center=rect.center)
                    self.screen.blit(text, text_rect)
                elif cell_value == 'X':
                    text = self.font.render("💥", True, BLACK)
                    text_rect = text.get_rect(center=rect.center)
                    self.screen.blit(text, text_rect)
                elif cell_value == 'O':
                    text = self.font.render("•", True, BLUE)
                    text_rect = text.get_rect(center=rect.center)
                    self.screen.blit(text, text_rect)
    
    def draw_ui(self):
        """Desenha toda a interface"""
        self.screen.fill(WHITE)
        
        # Título
        title = self.font.render("BATALHA NAVAL", True, BLACK)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 40))
        self.screen.blit(title, title_rect)
        
        # Status
        status = self.small_font.render(self.status_message, True, self.status_color)
        status_rect = status.get_rect(center=(WINDOW_WIDTH // 2, 90))
        self.screen.blit(status, status_rect)
        
        # Labels dos tabuleiros
        my_label = self.small_font.render("SEU TABULEIRO", True, BLACK)
        self.screen.blit(my_label, (self.my_board_x + 50, self.my_board_y - 30))
        
        enemy_label = self.small_font.render("TABULEIRO INIMIGO", True, BLACK)
        self.screen.blit(enemy_label, (self.enemy_board_x + 30, self.enemy_board_y - 30))
        
        # Tabuleiros
        self.draw_board(self.my_board, self.my_board_x, self.my_board_y, clickable=not self.game_started)
        self.draw_board(self.enemy_board, self.enemy_board_x, self.enemy_board_y, clickable=self.my_turn, is_enemy=True)
        
        # Botão conectar
        if self.connect_button_enabled and not self.connected:
            button_color = GREEN
            text_color = WHITE
        else:
            button_color = GRAY
            text_color = LIGHT_GRAY
        
        pygame.draw.rect(self.screen, button_color, self.connect_button_rect)
        pygame.draw.rect(self.screen, BLACK, self.connect_button_rect, 2)
        
        button_text = self.small_font.render("CONECTAR", True, text_color)
        button_text_rect = button_text.get_rect(center=self.connect_button_rect.center)
        self.screen.blit(button_text, button_text_rect)
        
        pygame.display.flip()
    
    def get_cell_from_pos(self, pos, board_x, board_y):
        """Retorna a célula do tabuleiro baseado na posição do mouse"""
        x, y = pos
        if board_x <= x < board_x + 5 * CELL_SIZE and board_y <= y < board_y + 5 * CELL_SIZE:
            col = (x - board_x) // CELL_SIZE
            row = (y - board_y) // CELL_SIZE
            return row, col
        return None, None
    
    def place_ship(self, row, col):
        """Posiciona um navio"""
        if self.ships_placed >= 3:
            self.status_message = "Você já posicionou todos os navios!"
            self.status_color = ORANGE
            return
        
        if self.my_board[row][col] == 'N':
            self.status_message = "Já existe um navio nesta posição!"
            self.status_color = ORANGE
            return
        
        self.my_board[row][col] = 'N'
        self.ships_placed += 1
        
        if self.ships_placed == 3:
            self.status_message = "Todos os navios posicionados! Clique em CONECTAR"
            self.status_color = GREEN
            self.connect_button_enabled = True
        else:
            self.status_message = f"Posicione mais {3 - self.ships_placed} navio(s)"
            self.status_color = BLUE
    
    def connect_to_server(self):
        """Conecta ao servidor"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((HOST, PORT))
            self.connected = True
            self.connect_button_enabled = False
            self.status_message = "Conectado! Aguardando outro jogador..."
            self.status_color = BLUE
            
            # Envia o tabuleiro para o servidor
            self.socket.sendall((json.dumps({
                "type": "board",
                "board": self.my_board
            }) + "\n").encode())
            
            # Inicia thread para receber mensagens
            thread = threading.Thread(target=self.receive_messages, daemon=True)
            thread.start()
            
        except Exception as e:
            self.status_message = f"Erro ao conectar: {e}"
            self.status_color = RED
    
    def receive_messages(self):
        """Thread para receber mensagens do servidor"""
        buffer = ""
        try:
            while True:
                data = self.socket.recv(1024)
                if not data:
                    break
                
                buffer += data.decode()
                
                # Processa todas as mensagens completas no buffer
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        try:
                            msg = json.loads(line)
                            self.handle_message(msg)
                        except json.JSONDecodeError as e:
                            print(f"Erro ao decodificar JSON: {e}")
        except Exception as e:
            print(f"Erro ao receber mensagem: {e}")
    
    def handle_message(self, msg):
        """Processa mensagens do servidor"""
        if msg["type"] == "info":
            self.status_message = msg["message"]
            self.status_color = BLUE
            
        elif msg["type"] == "player_id":
            self.player_id = msg["id"]
            
        elif msg["type"] == "game_start":
            self.game_started = True
            self.status_message = "Jogo iniciado! Aguarde sua vez..."
            self.status_color = GREEN
            
        elif msg["type"] == "your_turn":
            self.my_turn = True
            self.status_message = "SUA VEZ! Clique no tabuleiro inimigo para atacar"
            self.status_color = RED
            
        elif msg["type"] == "wait":
            self.my_turn = False
            self.status_message = "Aguarde o turno do adversário..."
            self.status_color = BLUE
            
        elif msg["type"] == "attack_result":
            x, y = msg["x"], msg["y"]
            hit = msg["hit"]
            
            if hit:
                self.enemy_board[x][y] = 'X'
                self.status_message = "ACERTOU! Aguarde sua próxima vez..."
                self.status_color = GREEN
            else:
                self.enemy_board[x][y] = 'O'
                self.status_message = "ERROU! Aguarde sua próxima vez..."
                self.status_color = ORANGE
            
        elif msg["type"] == "enemy_attack":
            x, y = msg["x"], msg["y"]
            hit = msg["hit"]
            
            if hit:
                self.my_board[x][y] = 'X'
                self.status_message = "Seu navio foi atingido!"
                self.status_color = RED
            else:
                self.my_board[x][y] = 'O'
                
        elif msg["type"] == "game_over":
            winner = msg["winner"]
            self.my_turn = False
            
            if winner == self.player_id:
                self.status_message = "VOCÊ VENCEU! 🎉"
                self.status_color = GREEN
            else:
                self.status_message = "VOCÊ PERDEU! 😢"
                self.status_color = RED
    
    def attack(self, row, col):
        """Ataca uma célula do tabuleiro inimigo"""
        if not self.my_turn:
            return
        
        if self.enemy_board[row][col] != '~':
            self.status_message = "Você já atacou esta posição!"
            self.status_color = ORANGE
            return
        
        self.socket.sendall((json.dumps({
            "type": "attack",
            "x": row,
            "y": col
        }) + "\n").encode())
        
        self.my_turn = False
        self.status_message = "Aguardando resposta do ataque..."
        self.status_color = BLUE
    
    def run(self):
        """Loop principal do jogo"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    
                    # Clique no botão conectar
                    if self.connect_button_rect.collidepoint(pos):
                        if self.connect_button_enabled and not self.connected:
                            self.connect_to_server()
                    
                    # Clique no seu tabuleiro (posicionar navios)
                    elif not self.game_started and self.ships_placed < 3:
                        row, col = self.get_cell_from_pos(pos, self.my_board_x, self.my_board_y)
                        if row is not None:
                            self.place_ship(row, col)
                    
                    # Clique no tabuleiro inimigo (atacar)
                    elif self.game_started and self.my_turn:
                        row, col = self.get_cell_from_pos(pos, self.enemy_board_x, self.enemy_board_y)
                        if row is not None:
                            self.attack(row, col)
            
            self.draw_ui()
            self.clock.tick(FPS)
        
        if self.socket:
            self.socket.close()
        pygame.quit()
        sys.exit()

def main():
    game = BattleshipGame()
    game.run()

if __name__ == "__main__":
    main()
