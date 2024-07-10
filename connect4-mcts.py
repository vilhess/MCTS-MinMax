import pygame
import numpy as np
from copy import deepcopy
import sys
import time

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


def drop_piece(grid, row, col, piece):
    grid[row][col] = piece
    return grid


def is_valid_location(grid, col):
    return grid[0][col] == 0


def get_next_open_row(grid, col):
    for r in range(ROW_COUNT - 1, -1, -1):
        if grid[r][col] == 0:
            return r


def draw_grid(grid):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            if grid[r][c] == 0:
                pygame.draw.circle(screen, BLACK, (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif grid[r][c] == -1:
                pygame.draw.circle(screen, RED, (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif grid[r][c] == 1:
                pygame.draw.circle(screen, YELLOW, (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    pygame.display.update()


class Grid:

    def __init__(self, parent=None):
        self.GRID_SIZE = (6, 7)
        self.create_grid()
        self.children = []
        self.results = []
        self.parent = parent
        self.curr_val = 1
        self.base_val = 1

    def create_grid(self):
        self.grid = np.zeros(self.GRID_SIZE)

    def is_leaf(self):
        return True if len(self.children) == 0 else False

    def is_terminal(self):
        return self.score_grid() != "not finished"

    def available_positions(self):
        couples = []
        for col in range(self.GRID_SIZE[1]):
            for row in range(self.GRID_SIZE[0] - 1, -1, -1):
                if self.grid[row, col] == 0:
                    couples.append((row, col))
                    break
        return couples

    def grid_complete(self):
        return len(self.available_positions()) == 0

    def win_grid(self):
        a, b = self.GRID_SIZE
        grid = self.grid

        # Horizontal check
        for row in range(a):
            for col in range(b - 3):
                if grid[row, col] == grid[row, col + 1] == grid[row, col + 2] == grid[row, col + 3] != 0:
                    return grid[row, col]

        # Vertical check
        for col in range(b):
            for row in range(a - 1, 2, -1):
                if grid[row, col] == grid[row - 1, col] == grid[row - 2, col] == grid[row - 3, col] != 0:
                    return grid[row, col]

        # Diagonal (bottom-left to top-right) check
        for row in range(a - 1, 2, -1):
            for col in range(b - 3):
                if grid[row, col] == grid[row - 1, col + 1] == grid[row - 2, col + 2] == grid[row - 3, col + 3] != 0:
                    return grid[row, col]

        # Diagonal (top-left to bottom-right) check
        for row in range(a - 3):
            for col in range(b - 3):
                if grid[row, col] == grid[row + 1, col + 1] == grid[row + 2, col + 2] == grid[row + 3, col + 3] != 0:
                    return grid[row, col]

        return False

    def play_move(self, pos):
        if len(pos) != 2:
            print("position length should be 2")
            return "position length should be 2"
        self.grid[pos] = self.curr_val
        self.curr_val = -self.curr_val

    def get_children(self):
        if not self.children:
            self.children = [(lambda g: (g.play_move(pos), g)[1])(deepcopy(self)) for pos in self.available_positions()]
            for child in self.children:
                child.parent = self
        return self.children

    def score_grid(self):
        win = self.win_grid()

        if win == self.base_val:
            return 100
        if win == -self.base_val:
            return -100
        if self.grid_complete():
            return 0
        return "not finished"

    def reset_grid(self):
        self.children = []
        self.results = []
        self.parent = None

    def show_grid(self):
        grid = self.grid.astype(str)
        grid[grid == "0.0"] = " "
        grid[grid == "1.0"] = "X"
        grid[grid == "-1.0"] = "O"

        # Afficher la grille avec une délimitation claire
        print("-----------------------------")
        for i, row in enumerate(grid):
            print(f"| {' | '.join(row)} |")
            print("-----------------------------")


def ucb_score(child, parent, C=np.sqrt(2)):
    if len(child.results) == 0:
        return np.inf
    return np.mean(child.results) + C * np.sqrt(np.log(len(parent.results)) / len(child.results))


def selection(grid):
    if not grid.is_leaf():
        ucbs = [ucb_score(child, grid) for child in grid.get_children()]
        candidate = np.random.choice(np.flatnonzero(ucbs == np.max(ucbs)))
        candidate = grid.get_children()[candidate]
        return selection(candidate)
    return grid


def expansion(grid):
    if not grid.is_terminal():
        if len(grid.results) == 0 and grid.parent is not None:
            return grid
        grid.children = grid.get_children()
        return grid.children[np.random.randint(len(grid.children))]
    return grid


def playout(grid):
    playout_node = deepcopy(grid)
    while not playout_node.is_terminal():
        av_pos = playout_node.available_positions()
        pos = av_pos[np.random.randint(len(av_pos))]
        playout_node.play_move(pos)
    reward = playout_node.score_grid()
    del playout_node
    return reward


def backpropagation(grid, reward):
    if grid.parent is None:
        grid.results.append(reward)
        return "Done"
    grid.results.append(reward)
    backpropagation(grid.parent, -reward)


def get_action(grid, value=1):
    for i in range(len(grid.available_positions())):
        leaf = selection(grid)
        expanded = expansion(leaf)
        for iter_playout in range(100):
            reward = playout(expanded)
            _ = backpropagation(expanded, value * reward)

    ucbs = [ucb_score(child, grid) for child in grid.children]
    candidate_id = np.random.choice(np.flatnonzero(ucbs == np.max(ucbs)))
    return grid.children[candidate_id]


def main():
    grid = Grid()
    game_over = False
    turn = 0

    draw_grid(grid.grid)
    pygame.display.update()

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                if turn == 0:
                    pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)

            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))

                # Player 1 Input
                if turn == 0:
                    posx = event.pos[0]
                    col = int(posx // SQUARESIZE)

                    if is_valid_location(grid.grid, col):
                        row = get_next_open_row(grid.grid, col)
                        grid.grid = drop_piece(grid.grid, row, col, -1)
                        grid.reset_grid()

                        if grid.win_grid() == -1:
                            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                            font = pygame.font.SysFont("monospace", 75)
                            label = font.render("Player 1 wins!", 1, RED)
                            screen.blit(label, (40, 10))
                            game_over = True

                        turn += 1
                        turn = turn % 2

                        draw_grid(grid.grid)

        # AI (Player 2) Input
        if turn == 1 and not game_over:
            action = get_action(grid, value=1)
            for r in range(ROW_COUNT):
                for c in range(COLUMN_COUNT):
                    if grid.grid[r][c] != action.grid[r][c]:
                        row, col = r, c
            grid.grid = drop_piece(grid.grid, row, col, 1)
            grid.reset_grid()

            if grid.win_grid() == 1:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                font = pygame.font.SysFont("monospace", 75)
                label = font.render("Player 2 wins!", 1, YELLOW)
                screen.blit(label, (40, 10))
                game_over = True

            draw_grid(grid.grid)
            turn += 1
            turn = turn % 2

        if game_over:
            pygame.time.wait(3000)


if __name__ == "__main__":
    main()
