import pygame
import sys
import random

# --- ƏSAS PARAMETRLƏR ---
GRID_WIDTH = 10 
GRID_HEIGHT = 20
BLOCK_SIZE = 30
WINDOW_WIDTH = GRID_WIDTH * BLOCK_SIZE + 200
WINDOW_HEIGHT = GRID_HEIGHT * BLOCK_SIZE
CAPTION = "MƏN MEMARAM - Tetris"

# Rənglər
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_GREY = (50, 50, 50)
GREEN = (0, 255, 0)

# --- OYUN VƏZİYYƏTLƏRİ ---
GAME_STATE = "MENU"
CURRENT_LEVEL = 0
DROP_SPEED = 500
MOVE_DOWN_EVENT = pygame.USEREVENT + 1

# --- GLOBAL OYUN VƏZİYYƏTLƏRİ ---
FALLING_PIECE = None
GRID = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
BLOCK_TEXTURES = None

# --- ABİDƏLƏR VƏ MƏRHƏLƏ MƏLUMATLARI ---
LEVELS = [
    {
        "name": "Qız Qalası (Bakı)",
        "image": "qiz_qalasi.jpg",
        "info": "Qız Qalası 12-ci əsrdə tikilmiş unikal abidədir. O, Bakının simvoludur və UNESCO-nun Dünya İrsi Siyahısına daxildir.",
    },
    {
        "name": "Şirvanşahlar Sarayı (Bakı)",
        "image": "sirvansahlar_sarayi.jpg",
        "info": "Şirvanşahlar Sarayı - 15-ci əsrə aid Şirvanşahlar dövlətinin keçmiş iqamətgahıdır. Yaxın Şərqin ən böyük abidələrindən biridir.",
    },
    {
        "name": "Ağoğlan Monastırı (Laçın)",
        "image": "ag_oglan_monastiri.jpg",
        "info": "Ağoğlan Monastırı (və ya Tsitsernavəng) - V əsrə aid Qafqaz Albaniyası dövrü abidəsidir. Laçın rayonunun ərazisində yerləşir.",
    }
]

# --- TETRIS FİQURLARI ---
TETROMINOES = {
    'I': [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
    'J': [[1, 0, 0], [1, 1, 1], [0, 0, 0]],
    'L': [[0, 0, 1], [1, 1, 1], [0, 0, 0]],
    'O': [[1, 1], [1, 1]],
    'S': [[0, 1, 1], [1, 1, 0], [0, 0, 0]],
    'T': [[0, 1, 0], [1, 1, 1], [0, 0, 0]],
    'Z': [[1, 1, 0], [0, 1, 1], [0, 0, 0]]
}
SHAPES = list(TETROMINOES.keys())

# --- Piece Klassı (Detalın Qaydaları) ---
class Piece:
    def __init__(self, x, y, shape_key, image_slice):
        self.x = x
        self.y = y
        self.shape_key = shape_key
        self.shape_matrix = TETROMINOES[shape_key]
        self.image_slice = image_slice 
        
    def rotate(self, matrix):
        new_matrix = [list(row) for row in zip(*matrix)]
        new_matrix = [row[::-1] for row in new_matrix]
        return new_matrix

    def rotate_piece(self):
        self.shape_matrix = self.rotate(self.shape_matrix)

# --- Oyun Başlanğıcı ---
pygame.init()
SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption(CAPTION)
CLOCK = pygame.time.Clock()

try:
    FONT_LARGE = pygame.font.Font(None, 74)
    FONT_MEDIUM = pygame.font.Font(None, 40)
    FONT_SMALL = pygame.font.Font(None, 24)
except:
    FONT_LARGE = pygame.font.SysFont(None, 74)
    FONT_MEDIUM = pygame.font.SysFont(None, 40)
    FONT_SMALL = pygame.font.SysFont(None, 24)

# --- Şəkil Yükləmə ---
def load_and_scale_image(file_path, size=None):
    try:
        image = pygame.image.load(file_path).convert_alpha()
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except:
        return None

MAIN_BG_IMAGE = load_and_scale_image("main_bg.jpg", (WINDOW_WIDTH, WINDOW_HEIGHT))
LEVEL_IMAGES = {}
for level in LEVELS:
    image = load_and_scale_image(level["image"], (GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE))
    LEVEL_IMAGES[level["name"]] = image

# --- Şəkil Kəsmə ---
def slice_image_for_texture(image, grid_width, grid_height, block_size):
    if image is None: return [[pygame.Surface((block_size, block_size)) for _ in range(grid_width)] for _ in range(grid_height)]
    slices = []
    for r in range(grid_height):
        row_slices = []
        for c in range(grid_width):
            x = c * block_size
            y = r * block_size
            rect = pygame.Rect(x, y, block_size, block_size)
            slice_surface = image.subsurface(rect)
            row_slices.append(slice_surface)
        slices.append(row_slices)
    return slices

# --- Parça Yaratmaq ---
def get_new_piece(textures):
    shape_key = random.choice(SHAPES)
    rand_col = random.randint(0, GRID_WIDTH - 4)
    rand_row = random.randint(0, GRID_HEIGHT - 4)
    texture_coords = (rand_col, rand_row)
    return Piece(GRID_WIDTH // 2 - 2, 0, shape_key, texture_coords)

# --- Toqquşma Yoxlanılması ---
def check_collision(piece, grid):
    for r, row in enumerate(piece.shape_matrix):
        for c, cell in enumerate(row):
            if cell:
                target_x = piece.x + c
                target_y = piece.y + r
                if target_x < 0 or target_x >= GRID_WIDTH or target_y >= GRID_HEIGHT: return True
                if target_y >= 0 and grid[target_y][target_x] != 0: return True
    return False

def is_valid_move(piece, dx, dy, new_matrix=None):
    piece.x += dx
    piece.y += dy
    original_matrix = piece.shape_matrix
    if new_matrix: piece.shape_matrix = new_matrix
    collision = check_collision(piece, GRID)
    piece.x -= dx
    piece.y -= dy
    if new_matrix: piece.shape_matrix = original_matrix
    return not collision

# --- Mərhələnin Tamamlanması ---
def check_level_completion():
    global GAME_STATE
    is_complete = True
    for r in range(GRID_HEIGHT):
        if any(cell == 0 for cell in GRID[r]):
            is_complete = False
            break

    if is_complete:
        GAME_STATE = "LEVEL_COMPLETE"
        pygame.time.set_timer(MOVE_DOWN_EVENT, 0)

# --- Sətr Təmizləmə ---
def clear_rows():
    global GRID
    new_grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    rows_cleared = 0
    for r in range(GRID_HEIGHT - 1, -1, -1):
        is_full = all(cell != 0 for cell in GRID[r])
        if is_full:
            rows_cleared += 1
        else:
            if r + rows_cleared < GRID_HEIGHT:
                new_grid[r + rows_cleared] = GRID[r]
    GRID = new_grid

# --- Parçanı Yerləşdirmək ---
def lock_piece(piece):
    for r, row in enumerate(piece.shape_matrix):
        for c, cell in enumerate(row):
            if cell:
                target_y = piece.y + r
                target_x = piece.x + c
                if target_y < 0: return 
                
                GRID[target_y][target_x] = (
                    piece.image_slice[0] + c, 
                    piece.image_slice[1] + r
                )
    clear_rows()
    check_level_completion()

# --- Oyun vəziyyətləri ---

def start_level(level_index):
    global GAME_STATE, CURRENT_LEVEL, BLOCK_TEXTURES, FALLING_PIECE, GRID
    if level_index >= len(LEVELS): 
        GAME_STATE = "FINAL_WIN"
        return
        
    CURRENT_LEVEL = level_index
    GAME_STATE = "PLAYING"
    GRID = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    current_image = LEVEL_IMAGES[LEVELS[CURRENT_LEVEL]["name"]]
    BLOCK_TEXTURES = slice_image_for_texture(current_image, GRID_WIDTH, GRID_HEIGHT, BLOCK_SIZE)
    FALLING_PIECE = get_new_piece(BLOCK_TEXTURES)
    pygame.time.set_timer(MOVE_DOWN_EVENT, DROP_SPEED)

def draw_menu():
    if MAIN_BG_IMAGE: SCREEN.blit(MAIN_BG_IMAGE, (0, 0))
    else: SCREEN.fill(BLACK)
    title_text = FONT_LARGE.render("MƏN MEMARAM", True, WHITE)
    SCREEN.blit(title_text, title_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4)))
    start_text = FONT_MEDIUM.render("Başlamaq üçün istənilən düyməni basın", True, WHITE)
    SCREEN.blit(start_text, start_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 3 // 4)))

def draw_level_complete_screen():
    current_level_data = LEVELS[CURRENT_LEVEL]
    SCREEN.fill(BLACK)
    success_text = FONT_LARGE.render("SƏN ƏLA MEMARSAN!", True, GREEN)
    SCREEN.blit(success_text, success_text.get_rect(center=(WINDOW_WIDTH // 2, 50)))

    info_lines = current_level_data["info"].split(". ")
    y_offset = 120
    for line in info_lines:
        line_text = FONT_SMALL.render(line.strip() + (". " if info_lines.index(line) < len(info_lines) - 1 else ""), True, WHITE)
        SCREEN.blit(line_text, line_text.get_rect(center=(WINDOW_WIDTH // 2, y_offset)))
        y_offset += 30
        
    completed_image = LEVEL_IMAGES[current_level_data["name"]]
    if completed_image:
        img_rect = completed_image.get_rect(center=(WINDOW_WIDTH // 2, y_offset + 100))
        SCREEN.blit(completed_image, img_rect)
        
    button_text = "GEDƏK NÖVBƏTİ ABİDƏYƏ" if CURRENT_LEVEL < len(LEVELS) - 1 else "BÜTÜN ABİDƏLƏR TİKİLDİ!"
    button_surface = FONT_MEDIUM.render(button_text, True, WHITE)
    button_rect = button_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
    pygame.draw.rect(SCREEN, LIGHT_GREY, button_rect.inflate(20, 10))
    SCREEN.blit(button_surface, button_rect)
    return button_rect

def draw_playing_screen():
    SCREEN.fill(BLACK)
    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            if GRID[r][c] != 0:
                tex_c, tex_r = GRID[r][c]
                block_surface = BLOCK_TEXTURES[tex_r][tex_c] 
                SCREEN.blit(block_surface, (c * BLOCK_SIZE, r * BLOCK_SIZE))
                             
    if FALLING_PIECE:
        start_tex_c, start_tex_r = FALLING_PIECE.image_slice
        for r, row in enumerate(FALLING_PIECE.shape_matrix):
            for c, cell in enumerate(row):
                if cell:
                    tex_c = start_tex_c + c
                    tex_r = start_tex_r + r
                    if 0 <= tex_r < GRID_HEIGHT and 0 <= tex_c < GRID_WIDTH:
                        block_surface = BLOCK_TEXTURES[tex_r][tex_c]
                        SCREEN.blit(block_surface, ((FALLING_PIECE.x + c) * BLOCK_SIZE, (FALLING_PIECE.y + r) * BLOCK_SIZE))

def draw_final_win():
    SCREEN.fill(BLACK)
    text = FONT_LARGE.render("TƏBRİKLƏR! BÜTÜN ABİDƏLƏR TİKİLDİ!", True, GREEN)
    SCREEN.blit(text, text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)))

# --- ƏSAS OYUN DÖVRƏSİ (MAIN LOOP) ---
def main():
    global GAME_STATE, CURRENT_LEVEL, FALLING_PIECE

    pygame.time.set_timer(MOVE_DOWN_EVENT, DROP_SPEED)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if GAME_STATE == "MENU":
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    start_level(0)

            elif GAME_STATE == "LEVEL_COMPLETE":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    next_button_rect = draw_level_complete_screen()
                    if next_button_rect.collidepoint(event.pos):
                        start_level(CURRENT_LEVEL + 1)
                        
            elif GAME_STATE == "PLAYING" and FALLING_PIECE:
                if event.type == MOVE_DOWN_EVENT:
                    if is_valid_move(FALLING_PIECE, 0, 1): FALLING_PIECE.y += 1
                    else:
                        lock_piece(FALLING_PIECE)
                        if GAME_STATE == "PLAYING":
                            FALLING_PIECE = get_new_piece(BLOCK_TEXTURES)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT and is_valid_move(FALLING_PIECE, -1, 0): FALLING_PIECE.x -= 1
                    elif event.key == pygame.K_RIGHT and is_valid_move(FALLING_PIECE, 1, 0): FALLING_PIECE.x += 1
                    elif event.key == pygame.K_DOWN and is_valid_move(FALLING_PIECE, 0, 1): FALLING_PIECE.y += 1
                    elif event.key == pygame.K_UP:
                        while is_valid_move(FALLING_PIECE, 0, 1): FALLING_PIECE.y += 1
                        lock_piece(FALLING_PIECE)
                        if GAME_STATE == "PLAYING":
                            FALLING_PIECE = get_new_piece(BLOCK_TEXTURES)
                    elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        temp_matrix = FALLING_PIECE.rotate(FALLING_PIECE.shape_matrix)
                        if is_valid_move(FALLING_PIECE, 0, 0, temp_matrix):
                            FALLING_PIECE.rotate_piece()

        # B. Ekranın Yenilənməsi
        if GAME_STATE == "MENU": draw_menu()
        elif GAME_STATE == "PLAYING": draw_playing_screen()
        elif GAME_STATE == "LEVEL_COMPLETE": draw_level_complete_screen()
        elif GAME_STATE == "FINAL_WIN": draw_final_win()

        pygame.display.flip()
        CLOCK.tick(60)

if __name__ == "__main__":
    main()