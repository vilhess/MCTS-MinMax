import pygame
import numpy as np
import time

# Configuration de la grille
WIDTH = 300
ROWS = 3
GRID_SIZE = (3, 3)
GRID_LINE_WIDTH = 5

Marker2Int = {
    0: "x",
    1: "o",
    10000: '-'
}

# Initialisation de la grille
grid = np.full(GRID_SIZE, 10000)


def available_positions(grid):
    pos = np.where(grid == 10000)
    couples = [(x, y) for x, y in zip(pos[0], pos[1])]
    return couples

def win_grid(grid):
    diag = np.diag(grid)
    reverse_diag = np.diag(np.fliplr(grid))
    if diag[0]==diag[1]==diag[2]!=0:
        return diag[0]
    
    if reverse_diag[0]==reverse_diag[1]==reverse_diag[2]!=0:
        return reverse_diag[0]
    
    for col in range(3):
        if grid[0, col]==grid[1, col]==grid[2, col]!=0:
            return grid[0, col]
    
    for row in range(3):
        if grid[row, 0]==grid[row, 1]==grid[row, 2]!=0:
            return grid[row, 0]
    
    return False

def score_grid(grid, bot_value=1):
    win = win_grid(grid)
    if win==bot_value:
        return 100
    if win==-bot_value:
        return -100
    if grid_complete(grid):
        return 0
    return False
    
def grid_complete(grid):
    if len(available_positions(grid))==0:
        return True
    return False


def minmax(grid, depth, alpha, beta, maximize=True, bot_val=1):

    score = score_grid(grid, bot_val)

    if depth==0 or score is not False:
        return score

    av_pos = available_positions(grid)
    np.random.shuffle(av_pos)
    if maximize:
        best_score=-float('inf')
        for pos in av_pos:
            grid[pos] = bot_val
            score = minmax(grid=grid, alpha=alpha, beta=beta, maximize=False, bot_val=bot_val, depth=depth-1)
            grid[pos] = 10000
            alpha = max(alpha, best_score)
            if score>best_score:
                best_score=score
            if beta<=alpha:
                break
        return best_score
    
    elif not maximize:
        best_score=float("inf")
        for pos in av_pos:
            grid[pos] = 1 - bot_val
            score = minmax(grid=grid, alpha=alpha, beta=beta, maximize=True, bot_val=bot_val, depth=depth-1)
            grid[pos] = 10000
            beta = min(beta, score)
            if score<best_score:
                    best_score=score
            if beta<=alpha:
                break
        return best_score 

def minmax_player(grid, bot_val=1, depth=6):
    best_score = -float("inf")
    best_pos = None
    av_pos = available_positions(grid)
    np.random.shuffle(av_pos)
    for pos in av_pos:
        grid[pos] = bot_val
        score = minmax(grid, maximize=False, bot_val=bot_val, depth=depth, alpha=-np.inf, beta=np.inf)
        grid[pos] = 10000
        if score > best_score:
            best_score = score
            best_pos = pos
    if best_pos is not None:
        return best_pos

# Initialisation de Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Morpion avec Bot")
font = pygame.font.Font(None, 100)

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def draw_grid():
    screen.fill(WHITE)
    for i in range(1, ROWS):
        pygame.draw.line(screen, BLACK, (0, i * WIDTH // ROWS), (WIDTH, i * WIDTH // ROWS), GRID_LINE_WIDTH)
        pygame.draw.line(screen, BLACK, (i * WIDTH // ROWS, 0), (i * WIDTH // ROWS, WIDTH), GRID_LINE_WIDTH)
    pygame.display.update()


def draw_marks():
    for i in range(ROWS):
        for j in range(ROWS):
            if grid[i, j] == 0:
                text = font.render("X", True, BLACK)
                screen.blit(text, (j * WIDTH // ROWS + 50, i * WIDTH // ROWS + 30))
            elif grid[i, j] == 1:
                text = font.render("O", True, BLACK)
                screen.blit(text, (j * WIDTH // ROWS + 50, i * WIDTH // ROWS + 30))
    pygame.display.update()


def main():
    run = True
    player_turn = False

    draw_grid()

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.MOUSEBUTTONDOWN and player_turn:
                mouseX, mouseY = event.pos
                clicked_row = mouseY // (WIDTH // ROWS)
                clicked_col = mouseX // (WIDTH // ROWS)

                if (clicked_row, clicked_col) in available_positions(grid):
                    grid[clicked_row, clicked_col] = 0
                    player_turn = False
                    draw_marks()

        if not player_turn and not score_grid(grid, bot_value=1):
            bot_move = minmax_player(grid, bot_val=1, depth=8)
            if bot_move:
                grid[bot_move[0], bot_move[1]] = 1
                player_turn = True
                draw_marks()

        if score_grid(grid) != False:
            time.sleep(3)
            run = False

    pygame.quit()


if __name__ == "__main__":
    main()
