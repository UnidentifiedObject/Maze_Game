import pygame
import random
import sys
from collections import deque

# --- Constants ---
CELL_SIZE = 20
MAZE_WIDTH = 25   # Number of cells horizontally
MAZE_HEIGHT = 25  # Number of cells vertically
SCREEN_WIDTH = CELL_SIZE * MAZE_WIDTH
SCREEN_HEIGHT = CELL_SIZE * MAZE_HEIGHT
FPS = 60
player_pos = [0, 0]  # [x, y]

goal_pos = [MAZE_WIDTH - 1, MAZE_HEIGHT - 1]
game_won = False



# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (0, 255, 0)
SOLUTION_COLOR = (255, 0, 0)

# --- Directions ---
DIRS = {
    'N': (0, -1),
    'S': (0, 1),
    'E': (1, 0),
    'W': (-1, 0)
}
OPPOSITE = {
    'N': 'S',
    'S': 'N',
    'E': 'W',
    'W': 'E'
}

# --- Maze Cell ---
class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.walls = {'N': True, 'S': True, 'E': True, 'W': True}
        self.visited = False

# --- Maze Generator ---
def generate_maze(width, height):
    grid = [[Cell(x, y) for y in range(height)] for x in range(width)]

    def visit(cx, cy):
        grid[cx][cy].visited = True
        directions = list(DIRS.keys())
        random.shuffle(directions)
        for direction in directions:
            nx, ny = cx + DIRS[direction][0], cy + DIRS[direction][1]
            if 0 <= nx < width and 0 <= ny < height and not grid[nx][ny].visited:
                grid[cx][cy].walls[direction] = False
                grid[nx][ny].walls[OPPOSITE[direction]] = False
                visit(nx, ny)

    visit(0, 0)
    return grid

# --- Maze Renderer ---
def draw_maze(screen, grid):
    pygame.draw.rect(
        screen,
        PLAYER_COLOR,
        (
            player_pos[0] * CELL_SIZE + 4,
            player_pos[1] * CELL_SIZE + 4,
            CELL_SIZE - 8,
            CELL_SIZE - 8
        )
    )

    for x in range(MAZE_WIDTH):
        for y in range(MAZE_HEIGHT):
            cell = grid[x][y]
            px = x * CELL_SIZE
            py = y * CELL_SIZE
            if cell.walls['N']:
                pygame.draw.line(screen, WHITE, (px, py), (px + CELL_SIZE, py))
            if cell.walls['S']:
                pygame.draw.line(screen, WHITE, (px, py + CELL_SIZE), (px + CELL_SIZE, py + CELL_SIZE))
            if cell.walls['E']:
                pygame.draw.line(screen, WHITE, (px + CELL_SIZE, py), (px + CELL_SIZE, py + CELL_SIZE))
            if cell.walls['W']:
                pygame.draw.line(screen, WHITE, (px, py), (px, py + CELL_SIZE))


def solve_maze(grid, width, height):
        start = (0, 0)
        end = (width - 1, height - 1)
        queue = deque([start])
        visited = {start: None}

        while queue:
            x, y = queue.popleft()
            if (x, y) == end:
                break

            for direction, (dx, dy) in DIRS.items():
                if not grid[x][y].walls[direction]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                        visited[(nx, ny)] = (x, y)
                        queue.append((nx, ny))

        # Reconstruct path
        path = []
        current = end
        while current:
            path.append(current)
            current = visited[current]
        path.reverse()
        return path


# --- Main ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Maze Game")
    clock = pygame.time.Clock()
    global player_pos
    grid = generate_maze(MAZE_WIDTH, MAZE_HEIGHT)
    goal_pos = [MAZE_WIDTH - 1, MAZE_HEIGHT - 1]
    solution_path = None
    show_solution = False
    last_move_time = 0
    move_delay = 150  # milliseconds between moves
    game_won = False

    running = True
    while running:
        screen.fill(BLACK)
        draw_maze(screen, grid)

        # Draw solution path if toggled on
        if show_solution and solution_path:
            for (x, y) in solution_path:
                pygame.draw.rect(
                    screen,
                    SOLUTION_COLOR,
                    (x * CELL_SIZE + 6, y * CELL_SIZE + 6, CELL_SIZE - 12, CELL_SIZE - 12)
                )

        # Draw player
        pygame.draw.rect(
            screen,
            PLAYER_COLOR,
            (
                player_pos[0] * CELL_SIZE + 4,
                player_pos[1] * CELL_SIZE + 4,
                CELL_SIZE - 8,
                CELL_SIZE - 8
            )
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    if not show_solution:
                        if solution_path is None:
                            solution_path = solve_maze(grid, MAZE_WIDTH, MAZE_HEIGHT)
                    show_solution = not show_solution

                elif event.key == pygame.K_r:
                    # Restart game
                    grid = generate_maze(MAZE_WIDTH, MAZE_HEIGHT)
                    player_pos = [0, 0]
                    solution_path = None
                    show_solution = False
                    game_won = False

        # Handle smooth player movement on key hold, only if game not won
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()
        x, y = player_pos

        if not game_won and current_time - last_move_time > move_delay:
            if keys[pygame.K_UP] and not grid[x][y].walls['N']:
                player_pos[1] -= 1
                last_move_time = current_time
            elif keys[pygame.K_DOWN] and not grid[x][y].walls['S']:
                player_pos[1] += 1
                last_move_time = current_time
            elif keys[pygame.K_LEFT] and not grid[x][y].walls['W']:
                player_pos[0] -= 1
                last_move_time = current_time
            elif keys[pygame.K_RIGHT] and not grid[x][y].walls['E']:
                player_pos[0] += 1
                last_move_time = current_time

        # Check if player reached goal
        if player_pos == goal_pos:
            game_won = True

        # Show Win message
        if game_won:
            font = pygame.font.SysFont(None, 72)
            text = font.render("You Win!", True, (255, 215, 0))  # Gold
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()