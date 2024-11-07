import pygame
import heapq
from collections import deque
import time

# Инициализация pygame
pygame.init()

# Настройки окна и цвета
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 5, 5
SQUARE_SIZE = WIDTH // COLS

# Цветовая палитра
RAVE_GREEN = (129, 222, 96)
BACKGROUND_COLOR = (102, 51, 153)  # Более фиолетовый цвет
WALL_COLOR = (128, 0, 128)
GOAL_COLOR = (0, 255, 255)
NEON_PINK = (255, 0, 255)
NEON_PURPLE = (44, 190, 178)

# Цвета для маршрутов
BFS_COLOR = (142, 122, 181)  
A_STAR_COLOR = (183, 132, 183)
DIJKSTRA_COLOR = (228, 147, 179)
GREEDY_COLOR = (238, 165, 166)
WAVE_COLOR = (255, 207, 157)

# Пять вариантов лабиринтов
mazes = [
    [
        [0, 1, 0, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 0, 1, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0]
    ],
    [
        [0, 1, 1, 1, 0],
        [0, 0, 0, 1, 0],
        [1, 1, 0, 1, 1],
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0]
    ],
    [
        [0, 0, 0, 1, 0],
        [1, 1, 0, 1, 0],
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0]
    ],
    [
        [0, 0, 1, 1, 0],
        [1, 0, 0, 1, 0],
        [1, 1, 0, 0, 1],
        [0, 0, 1, 0, 0],
        [0, 1, 0, 0, 0]
    ],
    [
        [0, 0, 0, 0, 0],
        [0, 1, 1, 0, 1],
        [0, 0, 0, 0, 0],
        [1, 1, 1, 0, 1],
        [0, 0, 0, 0, 0]
    ]
]

start = (0, 0)
end = (4, 4)

# Вспомогательная функция для отображения лабиринта
def draw_grid(win, maze):
    win.fill(BACKGROUND_COLOR)
    for row in range(ROWS):
        for col in range(COLS):
            color = WALL_COLOR if maze[row][col] == 1 else BACKGROUND_COLOR
            pygame.draw.rect(win, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    pygame.display.update()

# Функция для отображения пути
def draw_path(win, path, color):
    for row, col in path:
        pygame.draw.rect(win, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        pygame.display.update()
        time.sleep(0.1)

# Поиск соседей
def get_neighbors(position, maze):
    row, col = position
    neighbors = []
    for r, c in [(row-1, col), (row+1, col), (row, col-1), (row, col+1)]:
        if 0 <= r < ROWS and 0 <= c < COLS and maze[r][c] == 0:
            neighbors.append((r, c))
    return neighbors

# BFS
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

    if end not in visited:
        return []

    path = []
    step = end
    while step is not None:
        path.append(step)
        step = visited[step]
    path.reverse()
    return path

# A* 
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star(start, end, maze):
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

    if end not in came_from:
        return []

    path = []
    step = end
    while step is not None:
        path.append(step)
        step = came_from.get(step)
    path.reverse()
    return path

# Dijkstra
def dijkstra(start, end, maze):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {start: None}
    g_score = {start: 0}
    while open_set:
        current_distance, current = heapq.heappop(open_set)
        if current == end:
            break
        for neighbor in get_neighbors(current, maze):
            distance = current_distance + 1
            if neighbor not in g_score or distance < g_score[neighbor]:
                g_score[neighbor] = distance
                came_from[neighbor] = current
                heapq.heappush(open_set, (distance, neighbor))

    if end not in came_from:
        return []

    path = []
    step = end
    while step is not None:
        path.append(step)
        step = came_from.get(step)
    path.reverse()
    return path

# Жадный поиск
def greedy_best_first_search(start, end, maze):
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

    if end not in came_from:
        return []

    path = []
    step = end
    while step is not None:
        path.append(step)
        step = came_from.get(step)
    path.reverse()
    return path

# Волновой алгоритм
def wave_algorithm(start, end, maze):
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

    if end not in visited:
        return []

    path = []
    step = end
    while step is not None:
        path.append(step)
        step = visited.get(step)
    path.reverse()
    return path

# Основная функция
def main():
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Поиск кратчайшего пути в лабиринте")
    run = True

    # Перебор всех лабиринтов
    for maze in mazes:
        draw_grid(win, maze)

        # Отображение начальной и конечной точек
        pygame.draw.rect(win, RAVE_GREEN, (start[1] * SQUARE_SIZE, start[0] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        pygame.draw.rect(win, GOAL_COLOR, (end[1] * SQUARE_SIZE, end[0] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

        # Статистика для каждого алгоритма
        algorithms = {
            "BFS": bfs,
            "A*": a_star,
            "Dijkstra": dijkstra,
            "Greedy": greedy_best_first_search,
            "Wave": wave_algorithm
        }
        
        results = {}
        for name, algorithm in algorithms.items():
            start_time = time.perf_counter()  # Используем более точный таймер
            path = algorithm(start, end, maze)
            duration = (time.perf_counter() - start_time) * 1000  # Время в миллисекундах
            results[name] = (len(path), duration)
            if path:
                draw_path(win, path, BFS_COLOR if name == "BFS" else A_STAR_COLOR if name == "A*" else DIJKSTRA_COLOR if name == "Dijkstra" else GREEDY_COLOR if name == "Greedy" else WAVE_COLOR)
            else:
                print(f"{name} не смог найти путь до конечной точки.")
            time.sleep(1)

        # Печать результатов для текущего лабиринта
        print(f"\nЛабиринт:")
        for row in maze:
            print(row)
        print(f"\nРезультаты:")
        for name, (path_length, duration) in results.items():
            print(f"{name} - Длина пути: {path_length}, Время: {duration:.6f} мс")
        print("\n" + "="*30 + "\n")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

    # Итоговое сравнение по всем лабиринтам
    print("\nИтоговое сравнение алгоритмов по всем лабиринтам:\n")
    total_results = {name: {"path_length": 0, "time": 0} for name in algorithms}

    # Суммируем длины путей и время выполнения для каждого алгоритма
    for maze in mazes:
        for name, algorithm in algorithms.items():
            start_time = time.perf_counter()  # Используем более точный таймер
            path = algorithm(start, end, maze)
            duration = (time.perf_counter() - start_time) * 1000  # в мс
            total_results[name]["path_length"] += len(path)
            total_results[name]["time"] += duration

    # Выводим усредненные результаты
    for name, data in total_results.items():
        avg_length = data["path_length"] / len(mazes)
        avg_time = data["time"] / len(mazes)
        print(f"{name} - Средняя длина пути: {avg_length:.2f}, Среднее время: {avg_time:.6f} мс")

    pygame.quit()

main()
