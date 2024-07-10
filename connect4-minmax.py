import pygame
import numpy as np
import sys

# Initialize Pygame
pygame.init()

# Constants
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

ROW_COUNT = 6
COLUMN_COUNT = 7
GRID_SIZE = (ROW_COUNT, COLUMN_COUNT)
SQUARESIZE = 100

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE

RADIUS = int(SQUARESIZE / 2 - 5)

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Connect 4")

def create_grid():
    return np.zeros((ROW_COUNT, COLUMN_COUNT)) + 10000

def drop_piece(grid, row, col, piece):
    grid[row][col] = piece

def is_valid_location(grid, col):
    return grid[0][col] == 10000

def get_next_open_row(grid, col):
    for r in range(ROW_COUNT-1, -1, -1):
        if grid[r][col] == 10000:
            return r

def draw_grid(grid):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            if grid[r][c] == 10000:
                pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif grid[r][c] == 0:
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif grid[r][c] == 1:
                pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
    pygame.display.update()

def available_positions(grid):
    a, b = GRID_SIZE
    couples = []
    for col in range(b):
        for row in range(a-1, -1, -1):
            if grid[row, col]==10000:
                couples.append((row, col))
                break
    return couples

def grid_complete(grid):
    if len(available_positions(grid))==0:
        return True
    return False

def win_grid(grid):
    a, b = GRID_SIZE

    # Horizontal
    for row in range(a-1, -1, -1):
        for col in range(b-3):
            if grid[row, col]==grid[row, col+1]==grid[row, col+2]==grid[row, col+3]!=10000:
                return grid[row, col]
            
    # Vertical
    for col in range(b):
        for row in range(a-1, 2, -1):
            if grid[row, col]==grid[row-1, col]==grid[row-2, col]==grid[row-3, col]!=10000:
                return grid[row, col]
            
    # Diagonal 
    for row in range(a-1, 2, -1):
        for col in range(b-3):
            if grid[row, col]==grid[row-1, col+1]==grid[row-2, col+2]==grid[row-3, col+3]!=10000:
                return grid[row, col]
    
    # Diagonal
    for row in range(a-3):
        for col in range(b-3):
            if grid[row, col]==grid[row+1, col+1]==grid[row+2, col+2]==grid[row+3, col+3]!=10000:
                return grid[row, col]
    return "not finished"

def score_grid(grid, bot_val=1):
    a, b = GRID_SIZE
    score=0

    result = win_grid(grid)

    if result==bot_val:
        return 1000, True
    
    if result==1-bot_val:
        return -1000, True
    
    # Good move 2 align
    # Horizontal
    for row in range(a-1, -1, -1):
        for col in range(b-3):
            if grid[row, col]==grid[row, col+1]==bot_val and grid[row, col+2]==grid[row, col+3]==10000:
                score+=2

    # Diagonal
    for col in range(b-3):
        for row in range(a-1, 3, -1):
            if grid[row, col]==grid[row-1, col+1]==bot_val and grid[row-2, col+2]==grid[row-3, col+3]==10000:
                score+=2

    # Diagonal 
    for row in range(a-3):
        for col in range(b-3):
            if grid[row, col]==grid[row+1, col+1]==bot_val and grid[row+2, col+2]==grid[row+3, col+3]==10000:
                score+=2

    # Vertical
    for col in range(b):
        for row in range(a-3):
            if grid[row, col]==grid[row+1, col]==bot_val and grid[row+2, col]==grid[row+3, col]==10000:
                score+=2

    # Bad move 2 align
    # Horizontal
    for row in range(a-1, -1, -1):
        for col in range(b-3):
            if grid[row, col]==grid[row, col+1]==1-bot_val and grid[row, col+2]==grid[row, col+3]==10000:
                score-=2

    # Diagonal
    for col in range(b-3):
        for row in range(a-1, 3, -1):
            if grid[row, col]==grid[row-1, col+1]==1-bot_val and grid[row-2, col+2]==grid[row-3, col+3]==10000:
                score-=2

    # Diagonal 
    for row in range(a-3):
        for col in range(b-3):
            if grid[row, col]==grid[row+1, col+1]==1-bot_val and grid[row+2, col+2]==grid[row+3, col+3]==10000:
                score-=2

    # Vertical
    for col in range(b):
        for row in range(a-3):
            if grid[row, col]==grid[row+1, col]==1-bot_val and grid[row+2, col]==grid[row+3, col]==10000:
                score-=2

    # Good move 3 align
    # Horizontal
    for row in range(a-1, -1, -1):
        for col in range(b-3):
            if grid[row, col]==grid[row, col+1]==grid[row, col+2]==bot_val and grid[row, col+3]==10000:
                score+=10

    # Diagonal
    for col in range(b-3):
        for row in range(a-1, 3, -1):
            if grid[row, col]==grid[row-1, col+1]==grid[row-2, col+2]==bot_val and grid[row-3, col+3]==10000:
                score+=10

    # Diagonal 
    for row in range(a-3):
        for col in range(b-3):
            if grid[row, col]==grid[row+1, col+1]==grid[row+2, col+2]==bot_val and grid[row+3, col+3]==10000:
                score+=10

    # Vertical
    for col in range(b):
        for row in range(a-3):
            if grid[row, col]==grid[row+1, col]==grid[row+2, col]==bot_val and grid[row+3, col]==10000:
                score+=10

    # Bad move 3 align
    # Horizontal
    for row in range(a-1, -1, -1):
        for col in range(b-3):
            if grid[row, col]==grid[row, col+1]==grid[row, col+2]==1-bot_val and grid[row, col+3]==10000:
                score-=10

    # Diagonal
    for col in range(b-3):
        for row in range(a-1, 3, -1):
            if grid[row, col]==grid[row-1, col+1]==grid[row-2, col+2]==1-bot_val and grid[row-3, col+3]==10000:
                score-=10

    # Diagonal 
    for row in range(a-3):
        for col in range(b-3):
            if grid[row, col]==grid[row+1, col+1]==grid[row+2, col+2]==1-bot_val and grid[row+3, col+3]==10000:
                score-=10

    # Vertical
    for col in range(b):
        for row in range(a-3):
            if grid[row, col]==grid[row+1, col]==grid[row+2, col]==1-bot_val and grid[row+3, col]==10000:
                score-=10

    return score, False

def minmax(grid, depth, alpha, beta, maximize=True, bot_val=1):

    score, is_finish = score_grid(grid, bot_val)

    if depth==0 or grid_complete(grid) or is_finish:
        return score

    if maximize:
        best_score=-10000
        av_pos = available_positions(grid)
        np.random.shuffle(av_pos)
        for (i, j) in av_pos:
            grid[i, j] = bot_val
            score = minmax(grid=grid, alpha=alpha, beta=beta, maximize=False, bot_val=bot_val, depth=depth-1)
            grid[i, j] = 10000
            alpha = max(alpha, best_score)
            if score>best_score:
                best_score=score
            if beta<=alpha:
                break
        return best_score
    
    elif not maximize:
        best_score=1000
        av_pos = available_positions(grid)
        np.random.shuffle(av_pos)
        for (i, j) in av_pos:
            grid[i, j] = 1 - bot_val
            score = minmax(grid=grid, alpha=alpha, beta=beta, maximize=True, bot_val=bot_val, depth=depth-1)
            grid[i, j] = 10000
            beta = min(beta, score)
            if score<best_score:
                    best_score=score
            if beta<=alpha:
                break
        return best_score 
    
def minmax_player(grid, bot_val=1, depth=6):
    best_score = -1000
    best_pos = None
    av_pos = available_positions(grid)
    np.random.shuffle(av_pos)
    for (i, j) in av_pos:
        grid[i, j] = bot_val
        score = minmax(grid, maximize=False, bot_val=bot_val, depth=depth, alpha=-np.inf, beta=np.inf)
        grid[i, j] = 10000
        if score > best_score:
            best_score = score
            best_pos = (i, j)
    if best_pos is not None:
        return best_pos[1]
    if best_pos is None:
        return av_pos[0][0]


def main():
    grid = create_grid()
    game_over = False
    turn = 0

    draw_grid(grid)
    pygame.display.update()

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                if turn == 0:
                    pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)

            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                
                # Player 1 Input
                if turn == 0:
                    posx = event.pos[0]
                    col = int(posx // SQUARESIZE)
                    
                    if is_valid_location(grid, col):
                        row = get_next_open_row(grid, col)
                        drop_piece(grid, row, col, 0)

                        if win_grid(grid)==0:
                            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                            font = pygame.font.SysFont("monospace", 75)
                            label = font.render("Player 1 wins!", 1, RED)
                            screen.blit(label, (40, 10))
                            game_over = True

                        turn += 1
                        turn = turn % 2

                        draw_grid(grid)

        # AI (Player 2) Input
        if turn == 1 and not game_over:
            col = minmax_player(grid, bot_val=1, depth=4)
            print(col)
            
            if is_valid_location(grid, col):
                pygame.time.wait(500)
                row = get_next_open_row(grid, col)
                drop_piece(grid, row, col, 1)

                if win_grid(grid)==1:
                    pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                    font = pygame.font.SysFont("monospace", 75)
                    label = font.render("Player 2 wins!", 1, YELLOW)
                    screen.blit(label, (40, 10))
                    game_over = True

                draw_grid(grid)

                turn += 1
                turn = turn % 2

        if game_over:
            pygame.time.wait(3000)

if __name__ == "__main__":
    main()