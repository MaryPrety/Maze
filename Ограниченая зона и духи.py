import pygame
import sys
import random
import heapq

# Инициализация Pygame
pygame.init()

# Размеры экрана и ячеек
WIDTH, HEIGHT = 1000, 800
CELL_SIZE = 32

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RAVE_GREEN = (129, 222, 96)
BACKGROUND_COLOR = (101, 79, 109)
WALL_COLOR = (44, 190, 178)
GOAL_COLOR = (0, 255, 255)  # Неоновый голубой цвет
NEON_PINK = (255, 0, 255)  # Неоновый розовый цвет
NEON_PURPLE = (128, 0, 128)  # Неоновый фиолетовый цвет

# Загрузка изображений и звуков скримеров
scream_images = [pygame.image.load(f'scream{i}.png') for i in range(1, 6)]
scream_sounds = [pygame.mixer.Sound(f'scream{i}.wav') for i in range(1, 6)]

# Загрузка мелодии при достижении финиша
congratulations_music = pygame.mixer.Sound('congratulations_music.wav')

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze")

# Загрузка шрифта
font_path = 'Mostera St.ttf'  # Убедитесь, что шрифт в том же каталоге
font = pygame.font.Font(font_path, 36)

# Класс для ячейки лабиринта
class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

    def draw(self):
        x, y = self.x * CELL_SIZE, self.y * CELL_SIZE
        if self.walls['top']:
            pygame.draw.line(screen, WALL_COLOR, (x, y), (x + CELL_SIZE, y), 5)
        if self.walls['right']:
            pygame.draw.line(screen, WALL_COLOR, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), 5)
        if self.walls['bottom']:
            pygame.draw.line(screen, WALL_COLOR, (x + CELL_SIZE, y + CELL_SIZE), (x, y + CELL_SIZE), 5)
        if self.walls['left']:
            pygame.draw.line(screen, WALL_COLOR, (x, y + CELL_SIZE), (x, y), 5)

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

# Загрузка спрайтов игрока
def load_player_sprites():
    sprites = {
        'up': pygame.image.load('player_up.png'),
        'down': pygame.image.load('player_down.png'),
        'left': pygame.image.load('player_left.png'),
        'right': pygame.image.load('player_right.png'),
        'cry': pygame.image.load('player_cry.png')
    }
    return sprites

# Начальные координаты игрока и цели
player_x, player_y = 0, 0
goal_x, goal_y = (WIDTH // CELL_SIZE) - 1, (HEIGHT // CELL_SIZE) - 1

# Генерация лабиринта и загрузка спрайтов
maze = generate_maze(WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE)
player_sprites = load_player_sprites()
current_sprite = player_sprites['down']
cry_mode = False  # Режим крика

# Класс для духов
class Spirit:
    def __init__(self, x, y, path):
        self.start_x, self.start_y = x, y
        self.x, self.y = x, y
        self.path = path  # Список точек, по которым будет двигаться дух
        self.path_index = 0  # Индекс текущей точки в пути
        self.sprite = pygame.image.load('spirit.png')  # Загрузка скина для духа
        self.speed = 0.1  # Уменьшенная скорость

    def move(self):
        if self.path_index < len(self.path):
            next_x, next_y = self.path[self.path_index]
            if self.x < next_x:
                self.x += self.speed
            elif self.x > next_x:
                self.x -= self.speed
            elif self.y < next_y:
                self.y += self.speed
            elif self.y > next_y:
                self.y -= self.speed

            if abs(self.x - next_x) < 0.1 and abs(self.y - next_y) < 0.1:
                self.path_index += 1
                if self.path_index >= len(self.path):
                    self.path_index = 0

    def draw(self):
        screen.blit(self.sprite, (int(self.x * CELL_SIZE), int(self.y * CELL_SIZE)))

# Создание духов
# Определяем круговые пути для духов
spirit_paths = [
    [(1, 1), (1, 5), (5, 5)],
    
    [(10, 10), (10, 15), (15, 15)],
    [(20, 20), (20, 24), (24, 24)],
    
]
spirits = [Spirit(path[0][0], path[0][1], path) for path in spirit_paths]  # Увеличено количество духов

# Загрузка изображений жизней
heart_images = [pygame.image.load(f'heart{i}.png') for i in range(3)]
broken_heart_image = pygame.image.load('broken_heart.png')
sick_heart_image = pygame.image.load('sick_heart.png')

def draw_maze():
    for row in maze:
        for cell in row:
            cell.draw()

def draw_player():
    screen.blit(current_sprite, (player_x * CELL_SIZE, player_y * CELL_SIZE))

def draw_goal():
    # Вспыхивающая анимация неонового голубо-зеленого света
    time_ms = pygame.time.get_ticks() % 1000
    if time_ms < 500:
        glow_intensity = int(255 * (time_ms / 500))
        color = (0, glow_intensity, glow_intensity)
    else:
        glow_intensity = int(255 * ((1000 - time_ms) / 500))
        color = (0, glow_intensity, glow_intensity)

    pygame.draw.rect(screen, color, (goal_x * CELL_SIZE, goal_y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_spirits():
    for spirit in spirits:
        spirit.draw()

def draw_shortest_path(path):
    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]
        # Мигающие стрелки неоновой расцветки
        arrow_color = NEON_PINK if (pygame.time.get_ticks() // 500) % 2 == 0 else NEON_PURPLE
        if (x1, y1) != (player_x, player_y):  # Проверка, чтобы стрелки не перекрывали персонажа
            if x2 > x1:
                pygame.draw.polygon(screen, arrow_color, [(x1 * CELL_SIZE + CELL_SIZE // 2, y1 * CELL_SIZE + CELL_SIZE // 2),
                                                          (x1 * CELL_SIZE + CELL_SIZE // 2 + 10, y1 * CELL_SIZE + CELL_SIZE // 2 - 5),
                                                          (x1 * CELL_SIZE + CELL_SIZE // 2 + 10, y1 * CELL_SIZE + CELL_SIZE // 2 + 5)])
            elif x2 < x1:
                pygame.draw.polygon(screen, arrow_color, [(x1 * CELL_SIZE + CELL_SIZE // 2, y1 * CELL_SIZE + CELL_SIZE // 2),
                                                          (x1 * CELL_SIZE + CELL_SIZE // 2 - 10, y1 * CELL_SIZE + CELL_SIZE // 2 - 5),
                                                          (x1 * CELL_SIZE + CELL_SIZE // 2 - 10, y1 * CELL_SIZE + CELL_SIZE // 2 + 5)])
            elif y2 > y1:
                pygame.draw.polygon(screen, arrow_color, [(x1 * CELL_SIZE + CELL_SIZE // 2, y1 * CELL_SIZE + CELL_SIZE // 2),
                                                          (x1 * CELL_SIZE + CELL_SIZE // 2 - 5, y1 * CELL_SIZE + CELL_SIZE // 2 + 10),
                                                          (x1 * CELL_SIZE + CELL_SIZE // 2 + 5, y1 * CELL_SIZE + CELL_SIZE // 2 + 10)])
            elif y2 < y1:
                pygame.draw.polygon(screen, arrow_color, [(x1 * CELL_SIZE + CELL_SIZE // 2, y1 * CELL_SIZE + CELL_SIZE // 2),
                                                          (x1 * CELL_SIZE + CELL_SIZE // 2 - 5, y1 * CELL_SIZE + CELL_SIZE // 2 - 10),
                                                          (x1 * CELL_SIZE + CELL_SIZE // 2 + 5, y1 * CELL_SIZE + CELL_SIZE // 2 - 10)])

def draw_timer(time_left):
    text = font.render(f"Time left: {time_left} ms", True, WHITE)
    screen.blit(text, (10, HEIGHT - 80))

def draw_congratulations():
    text = font.render("Congratulations! You reached the goal!", True, WHITE)
    # Переливающаяся анимация
    time_ms = pygame.time.get_ticks() % 1000
    if time_ms < 500:
        glow_intensity = int(255 * (time_ms / 500))
        color = (glow_intensity, glow_intensity, glow_intensity)
    else:
        glow_intensity = int(255 * ((1000 - time_ms) / 500))
        color = (glow_intensity, glow_intensity, glow_intensity)
    text.fill(color, special_flags=pygame.BLEND_RGB_ADD)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

def draw_hearts(hp, timer_started):
    if timer_started:
        return  # Не рисуем сердечки, если таймер запущен

    for i in range(hp):
        if i < 3:
            screen.blit(heart_images[i], (10 + i * 50, HEIGHT - 60))
        else:
            screen.blit(sick_heart_image, (10 + i * 50, HEIGHT - 60))

def mode_2():
    global player_x, player_y, current_sprite, maze, cry_mode
    clock = pygame.time.Clock()
    game_over = False
    cry_timer = 0  # Таймер для режима крика
    show_reference_path = False
    timer_started = False
    timer_start_time = 0
    countdown_time = 30000  # Таймер обратного отсчета в миллисекундах (30 секунд)
    path = []  # Путь для кратчайшего маршрута
    scream_caught = False  # Флаг для отслеживания поимки скримера
    player_hp = 3  # Здоровье игрока

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    show_reference_path = True
                    timer_started = True
                    timer_start_time = pygame.time.get_ticks()  # Запуск таймера
                    path = find_shortest_path(maze, player_x, player_y, goal_x, goal_y)  # Найти кратчайший путь

                if not cry_mode:
                    new_x, new_y = player_x, player_y
                    if event.key == pygame.K_UP:
                        new_y -= 1
                        current_sprite = player_sprites['up']
                    elif event.key == pygame.K_DOWN:
                        new_y += 1
                        current_sprite = player_sprites['down']
                    elif event.key == pygame.K_LEFT:
                        new_x -= 1
                        current_sprite = player_sprites['left']
                    elif event.key == pygame.K_RIGHT:
                        new_x += 1
                        current_sprite = player_sprites['right']

                    # Проверка на столкновение со стеной
                    if 0 <= new_x < len(maze[0]) and 0 <= new_y < len(maze):
                        if ((new_x == player_x and new_y == player_y - 1 and not maze[player_y][player_x].walls['top']) or
                            (new_x == player_x and new_y == player_y + 1 and not maze[player_y][player_x].walls['bottom']) or
                            (new_x == player_x - 1 and new_y == player_y and not maze[player_y][player_x].walls['left']) or
                            (new_x == player_x + 1 and new_y == player_y and not maze[player_y][player_x].walls['right'])):
                            player_x, player_y = new_x, new_y

                            # Проверка достижения цели
                            if player_x == goal_x and player_y == goal_y:
                                game_over = True

                        else:
                            current_sprite = player_sprites['cry']  # Активация крика
                            cry_mode = True
                            cry_timer = pygame.time.get_ticks()  # Устанавливаем таймер

        # Таймер для возврата к обычному спрайту
        if cry_mode and pygame.time.get_ticks() - cry_timer > 500:
            cry_mode = False
            current_sprite = player_sprites['down']  # Возврат к обычному спрайту

        # Логика таймера обратного отсчета
        if timer_started:
            elapsed_time = pygame.time.get_ticks() - timer_start_time
            time_left = max(0, countdown_time - elapsed_time)
            if time_left <= 0:
                print("Time's up!")
                screen.fill(BLACK)  # Заливаем экран черным цветом
                scream_index = random.randint(0, 4)  # Выбираем случайный скример
                screen.blit(scream_images[scream_index], (WIDTH // 2 - scream_images[scream_index].get_width() // 2, HEIGHT // 2 - scream_images[scream_index].get_height() // 2))
                scream_sounds[scream_index].play()  # Воспроизведение звука скримера
                pygame.display.flip()
                pygame.time.delay(2000)  # Задержка перед выходом
                pygame.quit()
                sys.exit()

        # Логика духов
        for spirit in spirits:
            spirit.move()
            if int(spirit.x) == player_x and int(spirit.y) == player_y:
                player_x, player_y = 0, 0  # Возврат игрока в начало
                player_hp -= 1  # Снятие одного HP за столкновение с духом

        # Проверка на потерю всех HP
        if player_hp <= 0:
            print("Game Over! You ran out of HP.")
            screen.fill(BLACK)
            scream_index = random.randint(0, 4)
            screen.blit(scream_images[scream_index], (WIDTH // 2 - scream_images[scream_index].get_width() // 2, HEIGHT // 2 - scream_images[scream_index].get_height() // 2))
            scream_sounds[scream_index].play()
            pygame.display.flip()
            pygame.time.delay(2000)
            pygame.quit()
            sys.exit()

        # Отрисовка лабиринта
        screen.fill(BACKGROUND_COLOR)
        for row in range(max(0, player_y - 4), min(len(maze), player_y + 5)):
            for col in range(max(0, player_x - 4), min(len(maze[0]), player_x + 5)):
                maze[row][col].draw()
        draw_player()
        draw_goal()
        draw_spirits()  # Отрисовка духов после отрисовки лабиринта

        # Отображение кратчайшего пути, если нужно
        if show_reference_path:
            draw_shortest_path(path)

        # Отображение таймера обратного отсчета
        if timer_started:
            draw_timer(time_left)

        # Отображение жизней
        draw_hearts(player_hp, timer_started)

        # Поздравление при достижении финиша
        if game_over:
            congratulations_screen()

        pygame.display.flip()
        clock.tick(60)

def congratulations_screen():
    screen.fill(BLACK)
    draw_congratulations()
    congratulations_music.play()  # Воспроизведение мелодии при достижении финиша
    pygame.display.flip()
    pygame.time.delay(5000)  # Задержка перед закрытием окна
    pygame.quit()
    sys.exit()

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def find_shortest_path(maze, start_x, start_y, goal_x, goal_y):
    open_set = []
    heapq.heappush(open_set, (0, (start_x, start_y)))
    came_from = {}
    g_score = {(x, y): float('inf') for y in range(len(maze)) for x in range(len(maze[0]))}
    g_score[(start_x, start_y)] = 0
    f_score = {(x, y): float('inf') for y in range(len(maze)) for x in range(len(maze[0]))}
    f_score[(start_x, start_y)] = heuristic((start_x, start_y), (goal_x, goal_y))

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == (goal_x, goal_y):
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < len(maze[0]) and 0 <= neighbor[1] < len(maze):
                if dx == 0 and dy == 1 and not maze[current[1]][current[0]].walls['bottom']:
                    tentative_g_score = g_score[current] + 1
                elif dx == 1 and dy == 0 and not maze[current[1]][current[0]].walls['right']:
                    tentative_g_score = g_score[current] + 1
                elif dx == 0 and dy == -1 and not maze[current[1]][current[0]].walls['top']:
                    tentative_g_score = g_score[current] + 1
                elif dx == -1 and dy == 0 and not maze[current[1]][current[0]].walls['left']:
                    tentative_g_score = g_score[current] + 1
                else:
                    continue

                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, (goal_x, goal_y))
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []

# Запуск второго режима
mode_2()
