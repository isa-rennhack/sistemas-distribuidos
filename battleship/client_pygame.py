import socket
import json
import threading
import pygame
import sys

# Aceita IP do servidor como argumento
if len(sys.argv) > 1:
    HOST = sys.argv[1]
else:
    HOST = input("Digite o IP do servidor (ou Enter para localhost): ").strip()
    if not HOST:
        HOST = '127.0.0.1'

PORT = 65432

print(f"\n🎮 Conectando ao servidor {HOST}:{PORT}...\n")

# Configurações
WINDOW_WIDTH = 1300
WINDOW_HEIGHT = 850
CELL_SIZE = 40
BOARD_MARGIN = 50
FPS = 60

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 150, 255)
LIGHT_BLUE = (173, 216, 230)
MEDIUM_BLUE = (135, 184, 210)
DARK_GRAY = (70, 70, 70)
RED = (255, 50, 50)
GREEN = (50, 200, 50)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)
YELLOW = (255, 200, 0)
ORANGE = (255, 150, 0)

class BattleshipGame:
    def __init__(self):
        # inicialização
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Batalha Naval")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # tenta carregar uma fonte que suporte emojis (macOS)
        try:
            self.emoji_font = pygame.font.SysFont('Apple Color Emoji', 28)
            # testa se consegue renderizar emoji
            test_surface = self.emoji_font.render("⚓", True, WHITE)
            if test_surface.get_width() == 0:
                raise Exception("Emoji font não funciona")
        except:
            # fallback: usar fonte padrão
            self.emoji_font = None
        
        self.socket = None
        self.my_board = [['~' for _ in range(10)] for _ in range(10)]
        self.enemy_board = [['~' for _ in range(10)] for _ in range(10)]

        # NAVIOS
        self.ship_sizes = [5, 4, 3, 3, 2]
        self.current_ship_index = 0

        # ORIENTAÇÃO DO NAVIO
        self.ship_orientation = "H"   # H = horizontal, V = vertical
        
        self.ships_placed = 0
        self.game_started = False
        self.connected = False
        self.my_turn = False
        self.player_id = None
        self.status_message = "Clique para posicionar o navio de 5 células (R para girar)"
        self.status_color = BLUE
        self.game_over = False
        
        # Preview do navio
        self.preview_row = None
        self.preview_col = None
        
        # posição dos tabuleiros
        self.my_board_x = 100
        self.my_board_y = 210
        self.enemy_board_x = 800
        self.enemy_board_y = 210
        
        # botão conectar
        self.connect_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, 710, 200, 50)
        self.connect_button_enabled = False

    def can_place_ship(self, board, row, col, size, orientation):
        """Verifica se é possível posicionar um navio"""
        if orientation == "H":
            if col + size > 10:
                return False
            for c in range(col, col + size):
                if board[row][c] == 'N':
                    return False
        else:  # vertical
            if row + size > 10:
                return False
            for r in range(row, row + size):
                if board[r][col] == 'N':
                    return False
        return True
    
    def draw_board(self, board, x, y, clickable=False, is_enemy=False):
        # desenha todas as células
        for i in range(10):
            for j in range(10):
                cell_x = x + j * CELL_SIZE
                cell_y = y + i * CELL_SIZE
                rect = pygame.Rect(cell_x, cell_y, CELL_SIZE, CELL_SIZE)
                
                cell_value = board[i][j]
                if cell_value == '~':
                    color = LIGHT_BLUE if not is_enemy else MEDIUM_BLUE
                elif cell_value == 'N':
                    color = DARK_GRAY
                elif cell_value == 'X':
                    color = RED
                elif cell_value == 'O':
                    color = WHITE
                else:
                    color = LIGHT_BLUE if not is_enemy else MEDIUM_BLUE
                
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, BLACK, rect, 2)
                
                # desenha navios
                if cell_value == 'N' and not is_enemy:
                    if self.emoji_font:
                        # tenta desenhar emoji de navio
                        try:
                            emoji = self.emoji_font.render("⚓", True, WHITE)
                            if emoji.get_width() > 0:
                                emoji_rect = emoji.get_rect(center=rect.center)
                                self.screen.blit(emoji, emoji_rect)
                            else:
                                raise Exception("Emoji vazio")
                        except:
                            # fallback: não desenha nada, só deixa a cor cinza da célula
                            pass
                    # Se não tem emoji_font, também não desenha nada
                        
                # desenha hits
                elif cell_value == 'X':
                    if self.emoji_font:
                        # tenta desenhar emoji de explosão
                        try:
                            emoji = self.emoji_font.render("💥", True, BLACK)
                            if emoji.get_width() > 0:
                                emoji_rect = emoji.get_rect(center=rect.center)
                                self.screen.blit(emoji, emoji_rect)
                            else:
                                raise Exception("Emoji vazio")
                        except:
                            # fallback: desenha X
                            pygame.draw.line(self.screen, BLACK, (cell_x + 8, cell_y + 8), 
                                           (cell_x + CELL_SIZE - 8, cell_y + CELL_SIZE - 8), 4)
                            pygame.draw.line(self.screen, BLACK, (cell_x + CELL_SIZE - 8, cell_y + 8), 
                                           (cell_x + 8, cell_y + CELL_SIZE - 8), 4)
                    else:
                        # fallback: desenha X
                        pygame.draw.line(self.screen, BLACK, (cell_x + 8, cell_y + 8), 
                                       (cell_x + CELL_SIZE - 8, cell_y + CELL_SIZE - 8), 4)
                        pygame.draw.line(self.screen, BLACK, (cell_x + CELL_SIZE - 8, cell_y + 8), 
                                       (cell_x + 8, cell_y + CELL_SIZE - 8), 4)
                        
                # desenha misses
                elif cell_value == 'O':
                    if self.emoji_font:
                        # tenta desenhar emoji de água
                        try:
                            emoji = self.emoji_font.render("💧", True, BLUE)
                            if emoji.get_width() > 0:
                                emoji_rect = emoji.get_rect(center=rect.center)
                                self.screen.blit(emoji, emoji_rect)
                            else:
                                raise Exception("Emoji vazio")
                        except:
                            # fallback: desenha círculo
                            pygame.draw.circle(self.screen, BLUE, rect.center, 8, 3)
                    else:
                        # fallback: desenha círculo
                        pygame.draw.circle(self.screen, BLUE, rect.center, 8, 3)
        
        # desenha o preview por cima (se aplicável)
        if not is_enemy and not self.game_started and self.current_ship_index < len(self.ship_sizes):
            if self.preview_row is not None and self.preview_col is not None:
                size = self.ship_sizes[self.current_ship_index]
                can_place = self.can_place_ship(board, self.preview_row, self.preview_col, size, self.ship_orientation)
                
                # cor do preview: verde se pode, vermelho se não pode
                preview_color = (100, 255, 100, 180) if can_place else (255, 100, 100, 180)
                
                if self.ship_orientation == "H":
                    for c in range(self.preview_col, min(self.preview_col + size, 10)):
                        cell_x = x + c * CELL_SIZE
                        cell_y = y + self.preview_row * CELL_SIZE
                        preview_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                        preview_surface.fill(preview_color)
                        self.screen.blit(preview_surface, (cell_x, cell_y))
                        # desenha borda mais grossa no preview
                        pygame.draw.rect(self.screen, BLACK, (cell_x, cell_y, CELL_SIZE, CELL_SIZE), 3)
                else:  # vertical
                    for r in range(self.preview_row, min(self.preview_row + size, 10)):
                        cell_x = x + self.preview_col * CELL_SIZE
                        cell_y = y + r * CELL_SIZE
                        preview_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                        preview_surface.fill(preview_color)
                        self.screen.blit(preview_surface, (cell_x, cell_y))
                        # desenha borda mais grossa no preview
                        pygame.draw.rect(self.screen, BLACK, (cell_x, cell_y, CELL_SIZE, CELL_SIZE), 3)

    def draw_ui(self):
        self.screen.fill(WHITE)
        
        title = self.font.render("BATALHA NAVAL", True, BLACK)
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 70)))
        
        status = self.small_font.render(self.status_message, True, self.status_color)
        self.screen.blit(status, status.get_rect(center=(WINDOW_WIDTH // 2, 120)))
        
        my_label = self.small_font.render("SEU TABULEIRO", True, BLACK)
        self.screen.blit(my_label, (self.my_board_x + 130, self.my_board_y - 30))
        
        enemy_label = self.small_font.render("TABULEIRO INIMIGO", True, BLACK)
        self.screen.blit(enemy_label, (self.enemy_board_x + 130, self.enemy_board_y - 30))
        
        self.draw_board(self.my_board, self.my_board_x, self.my_board_y, clickable=not self.game_started)
        self.draw_board(self.enemy_board, self.enemy_board_x, self.enemy_board_y, clickable=self.my_turn, is_enemy=True)
        
        # botões após game over
        if self.game_over:
            # novo jogo
            self.new_game_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 220, 710, 200, 50)
            pygame.draw.rect(self.screen, GREEN, self.new_game_button_rect)
            new_game_text = self.small_font.render("NOVO JOGO", True, WHITE)
            self.screen.blit(new_game_text, new_game_text.get_rect(center=self.new_game_button_rect.center))
            
            # sair
            self.exit_button_rect = pygame.Rect(WINDOW_WIDTH // 2 + 20, 710, 200, 50)
            pygame.draw.rect(self.screen, RED, self.exit_button_rect)
            exit_text = self.small_font.render("SAIR", True, WHITE)
            self.screen.blit(exit_text, exit_text.get_rect(center=self.exit_button_rect.center))
        else:
            # só mostra botão conectar se o jogo não acabou
            if self.connect_button_enabled and not self.connected:
                button_color = GREEN
                text_color = WHITE
            else:
                button_color = GRAY
                text_color = LIGHT_GRAY
            
            pygame.draw.rect(self.screen, button_color, self.connect_button_rect)
            button_text = self.small_font.render("CONECTAR", True, text_color)
            self.screen.blit(button_text, button_text.get_rect(center=self.connect_button_rect.center))
        
        pygame.display.flip()

    def get_cell_from_pos(self, pos, board_x, board_y):
        x, y = pos
        if board_x <= x < board_x + 10 * CELL_SIZE and board_y <= y < board_y + 10 * CELL_SIZE:
            col = (x - board_x) // CELL_SIZE
            row = (y - board_y) // CELL_SIZE
            return row, col
        return None, None

    def place_ship(self, row, col):
        size = self.ship_sizes[self.current_ship_index]
        
        # verifica se pode posicionar
        if not self.can_place_ship(self.my_board, row, col, size, self.ship_orientation):
            self.status_message = "Não é possível posicionar o navio aqui!"
            self.status_color = ORANGE
            return
        
        # posiciona o navio
        if self.ship_orientation == "H":
            for c in range(col, col + size):
                self.my_board[row][c] = 'N'
        else:  # vertical
            for r in range(row, row + size):
                self.my_board[r][col] = 'N'

        self.current_ship_index += 1

        if self.current_ship_index == len(self.ship_sizes):
            self.status_message = "Todos os navios posicionados! Clique em CONECTAR"
            self.status_color = GREEN
            self.connect_button_enabled = True
        else:
            next_size = self.ship_sizes[self.current_ship_index]
            ori = "horizontal" if self.ship_orientation == "H" else "vertical"
            self.status_message = f"Posicione navio de {next_size} células ({ori}) - R para girar"

    def connect_to_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((HOST, PORT))
            self.connected = True
            self.connect_button_enabled = False
            self.status_message = "Conectado! Aguardando outro jogador..."
            self.status_color = BLUE
            
            self.socket.sendall((json.dumps({
                "type": "board",
                "board": self.my_board
            }) + "\n").encode())
            
            thread = threading.Thread(target=self.receive_messages, daemon=True)
            thread.start()
            
        except Exception as e:
            self.status_message = f"Erro ao conectar: {e}"
            self.status_color = RED

    def receive_messages(self):
        buffer = ""
        try:
            while True:
                data = self.socket.recv(1024)
                if not data:
                    break
                
                buffer += data.decode()
                
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        try:
                            msg = json.loads(line)
                            self.handle_message(msg)
                        except:
                            pass
        except:
            pass

    def handle_message(self, msg):
        msg_type = msg.get("type")
        
        if msg_type == "info":
            self.status_message = msg["message"]
            self.status_color = BLUE
        
        elif msg_type == "player_id":
            self.player_id = msg["id"]
        
        elif msg_type == "game_start":
            self.game_started = True
            self.status_message = "Jogo iniciado! Aguarde sua vez..."
            self.status_color = GREEN
        
        elif msg_type == "your_turn":
            self.my_turn = True
            self.status_message = "SUA VEZ! Clique no tabuleiro inimigo para atacar"
            self.status_color = GREEN
        
        elif msg_type == "wait":
            self.my_turn = False
            self.status_message = "Aguarde o oponente jogar..."
            self.status_color = ORANGE
        
        elif msg_type == "attack_result":
            x, y = msg["x"], msg["y"]
            if msg["hit"]:
                self.enemy_board[x][y] = "X"
                self.status_message = "ACERTOU! 💥 Aguarde o oponente..."
                self.status_color = RED
            else:
                self.enemy_board[x][y] = "O"
                self.status_message = "Errou... Aguarde o oponente..."
                self.status_color = BLUE
            self.my_turn = False
        
        elif msg_type == "enemy_attack":
            x, y = msg["x"], msg["y"]
            if msg["hit"]:
                self.my_board[x][y] = "X"
                self.status_message = "Seu navio foi atingido! 💥"
                self.status_color = RED
            else:
                self.my_board[x][y] = "O"
                self.status_message = "Oponente errou! Sua vez!"
                self.status_color = GREEN
        
        elif msg_type == "game_over":
            winner = msg["winner"]
            self.game_over = True
            if winner == self.player_id:
                self.status_message = "🎉 VOCÊ VENCEU! Parabéns!"
                self.status_color = GREEN
            else:
                self.status_message = "😢 Você perdeu... Tente novamente!"
                self.status_color = RED
        
        elif msg_type == "opponent_disconnected":
            # oponente desconectou - vitória por W.O.
            self.game_over = True
            self.status_message = msg["message"]
            self.status_color = ORANGE
            print(f"[INFO] {msg['message']}")

    def reset_game(self):
        """Reseta o jogo para uma nova partida"""
        if self.socket:
            self.socket.close()
        
        self.socket = None
        self.my_board = [['~' for _ in range(10)] for _ in range(10)]
        self.enemy_board = [['~' for _ in range(10)] for _ in range(10)]
        self.current_ship_index = 0
        self.ship_orientation = "H"
        self.game_started = False
        self.connected = False
        self.my_turn = False
        self.player_id = None
        self.game_over = False
        self.connect_button_enabled = False
        self.status_message = "Clique para posicionar o navio de 5 células (R para girar)"
        self.status_color = BLUE
        self.preview_row = None
        self.preview_col = None
    
    def attack(self, row, col):
        if not self.my_turn:
            return
        
        if self.enemy_board[row][col] != '~':
            self.status_message = "Já atacou aqui!"
            self.status_color = ORANGE
            return
        
        self.socket.sendall((json.dumps({
            "type": "attack",
            "x": row,
            "y": col
        }) + "\n").encode())
        
        self.my_turn = False
        self.status_message = "Aguardando resultado..."
        self.status_color = BLUE

    def run(self):
        running = True
        
        while running:
            # atualiza preview do navio baseado na posição do mouse
            if not self.game_started and self.current_ship_index < len(self.ship_sizes):
                mouse_pos = pygame.mouse.get_pos()
                row, col = self.get_cell_from_pos(mouse_pos, self.my_board_x, self.my_board_y)
                self.preview_row = row
                self.preview_col = col
            else:
                self.preview_row = None
                self.preview_col = None
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # TECLA R GIRA O NAVIO
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and not self.game_started and self.current_ship_index < len(self.ship_sizes):
                        # alternar H ↔ V
                        self.ship_orientation = "V" if self.ship_orientation == "H" else "H"
                        ori = "vertical" if self.ship_orientation == "V" else "horizontal"
                        size = self.ship_sizes[self.current_ship_index]
                        self.status_message = f"Posicione navio de {size} células ({ori})"

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    
                    # botões de game over
                    if self.game_over:
                        if hasattr(self, 'new_game_button_rect') and self.new_game_button_rect.collidepoint(pos):
                            self.reset_game()
                            continue
                        elif hasattr(self, 'exit_button_rect') and self.exit_button_rect.collidepoint(pos):
                            running = False
                            continue
                    
                    if self.connect_button_rect.collidepoint(pos):
                        if self.connect_button_enabled and not self.connected:
                            self.connect_to_server()
                    
                    elif not self.game_started and self.current_ship_index < len(self.ship_sizes):
                        row, col = self.get_cell_from_pos(pos, self.my_board_x, self.my_board_y)
                        if row is not None:
                            self.place_ship(row, col)
                    
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
