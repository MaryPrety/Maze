import pygame
import sys
import random
import time

# Инициализация Pygame
pygame.init()

# Размеры экрана и ячеек
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 40

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WALL_COLOR = (44, 190, 178)
PLAYER_COLOR = (0, 255, 0)
GOAL_COLOR = (255, 0, 255)

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dynamic Maze with Random Rotating Walls")

# Класс для ячейки лабиринта с вращающимися стенами
class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

    def draw(self):
        x, y = self.x * CELL_SIZE, self.y * CELL_SIZE
        wall_thickness = 2  # Возвращаем толщину стенок к 2 пикселям
        if self.walls['top']:
            pygame.draw.line(screen, WALL_COLOR, (x, y), (x + CELL_SIZE, y), wall_thickness)
        if self.walls['right']:
            pygame.draw.line(screen, WALL_COLOR, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), wall_thickness)
        if self.walls['bottom']:
            pygame.draw.line(screen, WALL_COLOR, (x + CELL_SIZE, y + CELL_SIZE), (x, y + CELL_SIZE), wall_thickness)
        if self.walls['left']:
            pygame.draw.line(screen, WALL_COLOR, (x, y + CELL_SIZE), (x, y), wall_thickness)

    def rotate_walls(self):
        # Вращение стен на 90 градусов
        self.walls['top'], self.walls['right'], self.walls['bottom'], self.walls['left'] = \
            self.walls['left'], self.walls['top'], self.walls['right'], self.walls['bottom']

# Генерация лабиринта
def generate_maze(width, height):
    maze = [[Cell(x, y) for x in range(width)] for y in range(height)]
    stack = []
    current = maze[0][0]
    current.visited = True
    stack.append(current)

    while stack:
        neighbors = []
        x, y = current.x, current.y

        if y > 0 and not maze[y - 1][x].visited:
            neighbors.append(maze[y - 1][x])
        if y < height - 1 and not maze[y + 1][x].visited:
            neighbors.append(maze[y + 1][x])
        if x > 0 and not maze[y][x - 1].visited:
            neighbors.append(maze[y][x - 1])
        if x < width - 1 and not maze[y][x + 1].visited:
            neighbors.append(maze[y][x + 1])

        if neighbors:
            next_cell = random.choice(neighbors)
            next_cell.visited = True
            # Удаление стен между текущей и следующей ячейкой
            if next_cell.x == current.x:
                if next_cell.y > current.y:
                    current.walls['bottom'] = False
                    next_cell.walls['top'] = False
                else:
                    current.walls['top'] = False
                    next_cell.walls['bottom'] = False
            else:
                if next_cell.x > current.x:
                    current.walls['right'] = False
                    next_cell.walls['left'] = False
                else:
                    current.walls['left'] = False
                    next_cell.walls['right'] = False

            stack.append(next_cell)
            current = next_cell
        else:
            current = stack.pop()

    return maze

# Инициализация игрока и цели
player_pos = [0, 0]
goal_pos = [(WIDTH // CELL_SIZE) - 1, (HEIGHT // CELL_SIZE) - 1]

# Время поворота стен и обновления лабиринта
rotation_interval = 5  # Увеличиваем интервал до 5 секунд
last_maze_update_time = time.time()

def draw_maze(maze):
    for row in maze:
        for cell in row:
            cell.draw()

def draw_player():
    pygame.draw.rect(screen, PLAYER_COLOR, (player_pos[0] * CELL_SIZE, player_pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_goal():
    pygame.draw.rect(screen, GOAL_COLOR, (goal_pos[0] * CELL_SIZE, goal_pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def can_move(maze, new_x, new_y):
    if new_x < 0 or new_x >= len(maze[0]) or new_y < 0 or new_y >= len(maze):
        return False
    cell = maze[player_pos[1]][player_pos[0]]
    new_cell = maze[new_y][new_x]
    if new_x == player_pos[0]:
        if new_y > player_pos[1]:
            return not cell.walls['bottom'] and not new_cell.walls['top']
        else:
            return not cell.walls['top'] and not new_cell.walls['bottom']
    else:
        if new_x > player_pos[0]:
            return not cell.walls['right'] and not new_cell.walls['left']
        else:
            return not cell.walls['left'] and not new_cell.walls['right']

# Основной игровой цикл
def game_loop():
    global last_maze_update_time
    clock = pygame.time.Clock()
    maze = generate_maze(WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE)

    while True:
        screen.fill(BLACK)  # Очистка экрана перед отрисовкой
        
        # Обновление лабиринта каждые 5 секунд
        if time.time() - last_maze_update_time > 5:
            maze = generate_maze(WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE)
            last_maze_update_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                new_x, new_y = player_pos
                if event.key == pygame.K_UP:
                    new_y -= 1
                elif event.key == pygame.K_DOWN:
                    new_y += 1
                elif event.key == pygame.K_LEFT:
                    new_x -= 1
                elif event.key == pygame.K_RIGHT:
                    new_x += 1

                # Проверка возможности движения игрока после вращения стен
                if can_move(maze, new_x, new_y):
                    player_pos[0], player_pos[1] = new_x, new_y

                    # Проверка достижения цели
                    if player_pos == goal_pos:
                        print("Вы достигли цели!")
                        pygame.quit()
                        sys.exit()

        draw_maze(maze)
        draw_player()
        draw_goal()
        pygame.display.flip()
        clock.tick(30)

# Запуск игры
game_loop()
