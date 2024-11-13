import pygame
import heapq
from collections import deque
import time
import sys
import pandas as pd
import matplotlib.pyplot as plt

# Инициализация pygame
pygame.init()

# Настройки окна и цвета
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 5, 5  # Размер сетки лабиринта
SQUARE_SIZE = WIDTH // COLS

# Гармоничная цветовая палитра
BACKGROUND_COLOR = (240, 240, 240)
WALL_COLOR = (70, 70, 70)
START_COLOR = (50, 205, 50)
END_COLOR = (255, 69, 0)
ALGO_COLORS = {
    "BFS": (65, 105, 225),
    "A*": (255, 140, 0),
    "Dijkstra": (186, 85, 211),
    "Greedy": (240, 230, 140),
    "Wave": (173, 255, 47)
}

# Состояние приложения
mazes = []
selected_algorithms = []
selected_mazes = []
maze_index = 0
start, end = (0, 0), (ROWS-1, COLS-1)

# Создание пустого лабиринта
def create_empty_maze():
    return [[0 for _ in range(COLS)] for _ in range(ROWS)]

# Вспомогательная функция для отображения лабиринта
def draw_grid(win, maze, show_path=None, path=[]):
    win.fill(BACKGROUND_COLOR)
    for row in range(ROWS):
        for col in range(COLS):
            color = WALL_COLOR if maze[row][col] == 1 else BACKGROUND_COLOR
            pygame.draw.rect(win, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    pygame.draw.rect(win, START_COLOR, (start[1] * SQUARE_SIZE, start[0] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    pygame.draw.rect(win, END_COLOR, (end[1] * SQUARE_SIZE, end[0] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    if show_path:
        for pos in path:
            pygame.draw.rect(win, ALGO_COLORS[show_path], (pos[1] * SQUARE_SIZE, pos[0] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    pygame.display.update()

# Функция для отображения пути алгоритма
def draw_path(win, path, color):
    for row, col in path:
        pygame.draw.rect(win, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        pygame.display.update()
        time.sleep(0.05)

# Поиск соседей
def get_neighbors(position, maze):
    row, col = position
    neighbors = []
    for r, c in [(row-1, col), (row+1, col), (row, col-1), (row, col+1)]:
        if 0 <= r < ROWS and 0 <= c < COLS and maze[r][c] == 0:
            neighbors.append((r, c))
    return neighbors

# Алгоритмы поиска
def bfs(start, end, maze):
    queue = deque([start])
    visited = {start: None}
    while queue:
        current = queue.popleft()
        if current == end:
            break
        for neighbor in get_neighbors(current, maze):
            if neighbor not in visited:
                queue.append(neighbor)
                visited[neighbor] = current
    path = []
    step = end
    while step:
        path.append(step)
        step = visited.get(step)
    path.reverse()
    return path

def a_star(start, end, maze):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {start: None}
    g_score = {start: 0}
    while open_set:
        _, current = heapq.heappop(open_set)
        if current == end:
            break
        for neighbor in get_neighbors(current, maze):
            tentative_g_score = g_score[current] + 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor, end)
                heapq.heappush(open_set, (f_score, neighbor))
    path = []
    step = end
    while step:
        path.append(step)
        step = came_from.get(step)
    path.reverse()
    return path

def dijkstra(start, end, maze):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {start: None}
    g_score = {start: 0}
    while open_set:
        _, current = heapq.heappop(open_set)
        if current == end:
            break
        for neighbor in get_neighbors(current, maze):
            tentative_g_score = g_score[current] + 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                heapq.heappush(open_set, (tentative_g_score, neighbor))
    path = []
    step = end
    while step:
        path.append(step)
        step = came_from.get(step)
    path.reverse()
    return path

def greedy(start, end, maze):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    open_set = []
    heapq.heappush(open_set, (heuristic(start, end), start))
    came_from = {start: None}
    while open_set:
        _, current = heapq.heappop(open_set)
        if current == end:
            break
        for neighbor in get_neighbors(current, maze):
            if neighbor not in came_from:
                came_from[neighbor] = current
                heapq.heappush(open_set, (heuristic(neighbor, end), neighbor))
    path = []
    step = end
    while step:
        path.append(step)
        step = came_from.get(step)
    path.reverse()
    return path

def wave(start, end, maze):
    queue = deque([start])
    visited = {start: None}
    while queue:
        current = queue.popleft()
        if current == end:
            break
        for neighbor in get_neighbors(current, maze):
            if neighbor not in visited:
                queue.append(neighbor)
                visited[neighbor] = current
    path = []
    step = end
    while step:
        path.append(step)
        step = visited.get(step)
    path.reverse()
    return path

# Основное меню
def main_menu():
    global mazes, maze_index, start, end
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Редактор лабиринта и тестирование алгоритмов")

    run = True
    while run:
        win.fill(BACKGROUND_COLOR)
        font = pygame.font.SysFont(None, 40)
        instructions = [
            "1. Создать лабиринт",
            "2. Запустить тестирование",
            "Esc: Выход"
        ]
        for i, text in enumerate(instructions):
            line = font.render(text, True, (0, 0, 0))
            win.blit(line, (150, 150 + i * 50))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    # Создание лабиринта
                    maze_edit_mode(win)
                elif event.key == pygame.K_2:
                    # Запуск тестирования
                    run_tests(win)
                elif event.key == pygame.K_ESCAPE:
                    run = False

# Режим редактирования лабиринта
def maze_edit_mode(win):
    global mazes, start, end
    maze = create_empty_maze()
    editing = True
    while editing:
        draw_grid(win, maze)
        
        # Инструкции для управления в режиме редактирования
        font = pygame.font.SysFont(None, 24)
        instructions = [
            "ЛКМ: Добавить / удалить стену",
            "ПКМ: Установить начальную точку",
            "С: Установить конечную точку",
            "Enter: Сохранить лабиринт и выйти"
        ]
        for i, text in enumerate(instructions):
            line = font.render(text, True, (0, 0, 0))
            win.blit(line, (10, HEIGHT - (len(instructions) - i) * 20))

        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                editing = False
                pygame.quit()
                sys.exit()
            elif pygame.mouse.get_pressed()[0]:
                x, y = pygame.mouse.get_pos()
                row, col = y // SQUARE_SIZE, x // SQUARE_SIZE
                if (row, col) != start and (row, col) != end:
                    maze[row][col] = 1 if maze[row][col] == 0 else 0
            elif pygame.mouse.get_pressed()[2]:
                x, y = pygame.mouse.get_pos()
                start = y // SQUARE_SIZE, x // SQUARE_SIZE
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    x, y = pygame.mouse.get_pos()
                    end = y // SQUARE_SIZE, x // SQUARE_SIZE
                elif event.key == pygame.K_RETURN:
                    mazes.append(maze)
                    editing = False

# Запуск тестирования
def run_tests(win):
    global selected_algorithms, selected_mazes
    algorithms = {"BFS": bfs, "A*": a_star, "Dijkstra": dijkstra, "Greedy": greedy, "Wave": wave}
    
    # Выбор лабиринтов для тестирования
    if not mazes:
        print("Нет созданных лабиринтов для тестирования.")
        return
    
    selected_mazes = []
    selected_algorithms = []
    
    # Выбор лабиринтов
    print("Выберите лабиринты для тестирования:")
    for i, maze in enumerate(mazes):
        print(f"{i + 1}. Лабиринт {i + 1}")
    
    while True:
        try:
            choices = list(map(int, input("Введите номера лабиринтов через запятую: ").split(',')))
            selected_mazes = [mazes[c - 1] for c in choices]
            break
        except (ValueError, IndexError):
            print("Неверный ввод. Пожалуйста, введите числа через запятую.")
    
    # Выбор алгоритмов
    print("Выберите алгоритмы для тестирования:")
    for i, algo in enumerate(algorithms.keys()):
        print(f"{i + 1}. {algo}")
    
    while True:
        try:
            choices = list(map(int, input("Введите номера алгоритмов через запятую: ").split(',')))
            selected_algorithms = [list(algorithms.keys())[c - 1] for c in choices]
            break
        except (ValueError, IndexError):
            print("Неверный ввод. Пожалуйста, введите числа через запятую.")
    
    # Тестирование
    results = []
    for maze in selected_mazes:
        draw_grid(win, maze)
        for algo_name in selected_algorithms:
            algorithm = algorithms.get(algo_name)
            if algorithm:
                start_time = time.perf_counter()
                path = algorithm(start, end, maze)
                end_time = time.perf_counter()
                draw_path(win, path, ALGO_COLORS[algo_name])
                
                results.append({
                    'Maze': selected_mazes.index(maze) + 1,
                    'Algorithm': algo_name,
                    'Path Length': len(path) if path else 'Путь не найден',
                    'Execution Time (ms)': (end_time - start_time) * 1000
                })
    
    # Создание таблицы и графиков
    df = pd.DataFrame(results)
    print(df)
    
    # Графики
    plt.figure(figsize=(12, 6))
    for algo_name in selected_algorithms:
        algo_data = df[df['Algorithm'] == algo_name]
        plt.plot(algo_data['Maze'], algo_data['Execution Time (ms)'], label=algo_name, marker='o')
    
    plt.xlabel('Лабиринт')
    plt.ylabel('Время выполнения (мс)')
    plt.title('Эффективность алгоритмов по времени выполнения')
    plt.legend()
    plt.show()

    plt.figure(figsize=(12, 6))
    for algo_name in selected_algorithms:
        algo_data = df[df['Algorithm'] == algo_name]
        plt.plot(algo_data['Maze'], algo_data['Path Length'], label=algo_name, marker='o')
    
    plt.xlabel('Лабиринт')
    plt.ylabel('Длина пути')
    plt.title('Эффективность алгоритмов по длине пути')
    plt.legend()
    plt.show()

    font = pygame.font.SysFont(None, 40)
    win.fill(BACKGROUND_COLOR)
    result_text = font.render("Тестирование завершено! Нажмите ESC для выхода.", True, (0, 0, 0))
    win.blit(result_text, (50, HEIGHT // 2))
    pygame.display.update()
    while True:
        event = pygame.event.wait()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            break

main_menu()
pygame.quit()
