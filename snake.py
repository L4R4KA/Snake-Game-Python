import pygame
import time
import random
import json
import os
import sys

# --- ИНИЦИАЛИЗАЦИЯ И ЦВЕТА ---
pygame.init()

# Цвета (Палитра)
BACKGROUND_COLOR = (20, 20, 30)
GRID_COLOR = (40, 40, 60)
BUTTON_FACE = (30, 30, 40)
BUTTON_GLOW = (150, 200, 255)
BUTTON_TEXT = (220, 230, 255)
SNAKE_DARK = (20, 40, 20)
SNAKE_LIGHT = (50, 90, 50)
SNAKE_HIGHLIGHT = (90, 140, 90)
APPLE_DARK = (80, 0, 0)
APPLE_BASE = (150, 30, 30)
APPLE_HIGHLIGHT = (220, 80, 80)
STEM_COLOR = (50, 30, 10)
ACHIEVEMENT_BG = (60, 60, 80)
ACHIEVEMENT_TEXT = (255, 255, 200)

# --- ЭТОЙ СТРОКИ НЕ ХВАТАЛО В ВАШЕМ КОДЕ ---
DARK_GRAY = (50, 50, 50) 

# --- ПУТИ И НАСТРОЙКИ ---
ACHIEVEMENT_FILE = "achievements.json"
ACHIEVEMENT_GOALS = [5, 10, 15, 20, 25, 30]
ACHIEVEMENT_NAMES = {5: "Первый шаг", 10: "Юная змейка", 15: "Хищник", 20: "Император", 25: "Божество", 30: "Бесконечность"}

infoObject = pygame.display.Info()
DIS_WIDTH, DIS_HEIGHT = infoObject.current_w, infoObject.current_h
BLOCK_SIZE = 30
FPS = 15

dis = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption('Змейка - Night Mode')
clock = pygame.time.Clock()

# --- ШРИФТЫ ---
font_style = pygame.font.SysFont("bahnschrift", 35)
score_font = pygame.font.SysFont("comicsansms", 45)
menu_font = pygame.font.SysFont("comicsansms", 80)
button_font = pygame.font.Font('freesansbold.ttf', 70)
author_font = pygame.font.SysFont("arial", 20)
achi_font_big = pygame.font.Font('freesansbold.ttf', 50)
achi_font_small = pygame.font.Font('freesansbold.ttf', 30)

# --- ФУНКЦИИ РИСОВАНИЯ ---
def draw_grid():
    for x in range(0, DIS_WIDTH, BLOCK_SIZE): pygame.draw.line(dis, GRID_COLOR, (x, 0), (x, DIS_HEIGHT), 1)
    for y in range(0, DIS_HEIGHT, BLOCK_SIZE): pygame.draw.line(dis, GRID_COLOR, (0, y), (DIS_WIDTH, y), 1)

def draw_detailed_apple(foodx, foody):
    pygame.draw.ellipse(dis, APPLE_DARK, [foodx + 6, foody + 6, BLOCK_SIZE, BLOCK_SIZE])
    pygame.draw.ellipse(dis, APPLE_BASE, [foodx + 2, foody + 2, BLOCK_SIZE - 4, BLOCK_SIZE - 4])
    pygame.draw.ellipse(dis, APPLE_HIGHLIGHT, [foodx + 8, foody, BLOCK_SIZE - 12, BLOCK_SIZE // 2 - 2])
    pygame.draw.rect(dis, STEM_COLOR, [foodx + 12, foody - 10, 6, 12], border_radius=3)
    pygame.draw.polygon(dis, STEM_COLOR, [[foodx + 12, foody - 10], [foodx + 8, foody - 18], [foodx + 16, foody - 18]])

def draw_detailed_snake(block_size, snake_list):
    if not snake_list: return
    for index in range(len(snake_list) - 1, -1, -1):
        x, y = snake_list[index]
        pygame.draw.rect(dis, SNAKE_DARK, [x + 3, y + 3, block_size, block_size], border_radius=5)
        pygame.draw.rect(dis, SNAKE_LIGHT, [x, y, block_size, block_size], border_radius=5)
        pygame.draw.polygon(dis, SNAKE_HIGHLIGHT, [[x, y], [x + block_size, y], [x + block_size - 3, y + 3], [x + 3, y + 3]])
        pygame.draw.polygon(dis, SNAKE_DARK, [[x, y], [x, y + block_size], [x + 3, y + block_size - 3], [x + 3, y + 3]])
        pygame.draw.polygon(dis, SNAKE_LIGHT, [[x + 5, y + 5], [x + block_size - 5, y + 5], [x + block_size, y + block_size], [x, y + block_size]])
        if index == len(snake_list) - 1:
            eye_offset = block_size // 4
            pygame.draw.circle(dis, (10, 10, 10), [x + eye_offset, y + eye_offset], 5)
            pygame.draw.circle(dis, SNAKE_HIGHLIGHT, [x + eye_offset - 2, y + eye_offset - 2], 2)

def our_score(score):
    shadow = score_font.render(f"Длина: {score}", True, (10, 10, 20))
    dis.blit(shadow, [12, 12])
    text = score_font.render(f"Длина: {score}", True, SNAKE_HIGHLIGHT)
    dis.blit(text, [10, 10])

def draw_author():
    # Теперь DARK_GRAY определена, ошибки не будет
    dis.blit(author_font.render("Автор: Лирика | tg: Xeofenow", True, DARK_GRAY), [10, DIS_HEIGHT - 30])

def draw_button(text, x, y, w, h, mouse, click):
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        for i in range(4, 0, -1): pygame.draw.rect(dis, BUTTON_GLOW, (x - i, y - i, w + i*2, h + i*2), border_radius=15 + i)
    else:
        pygame.draw.rect(dis, (50, 50, 50), (x - 3, y - 3, w + 6, h + 6), border_radius=18)
        pygame.draw.rect(dis, (100, 100, 100), (x - 2, y - 2, w + 4, h + 4), border_radius=17)
        pygame.draw.rect(dis, BUTTON_GLOW, (x - 1, y - 1, w + 2, h + 2), border_radius=16)
    pygame.draw.rect(dis, BUTTON_FACE, (x, y, w, h), border_radius=15)
    txt = button_font.render(text, True, BUTTON_TEXT)
    dis.blit(txt, txt.get_rect(center=(x + w/2, y + h/2)))
    return (click[0] == 1 and x + w > mouse[0] > x and y + h > mouse[1] > y)

# --- МЕНЮ И ДАННЫЕ ---
def load_achievements():
    if not os.path.exists(ACHIEVEMENT_FILE): return {str(g): False for g in ACHIEVEMENT_GOALS}
    try: 
        with open(ACHIEVEMENT_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    except: return {str(g): False for g in ACHIEVEMENT_GOALS}

def save_achievements(data):
    try: 
        with open(ACHIEVEMENT_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)
    except: pass

def check_achievement(length, unlocked_list):
    unlocked_now = []
    for goal in ACHIEVEMENT_GOALS:
        key = str(goal)
        if length >= goal and not unlocked_list.get(key, False):
            unlocked_list[key] = True
            unlocked_now.append((goal, ACHIEVEMENT_NAMES[goal]))
    if unlocked_now: save_achievements(unlocked_list)
    return unlocked_now

def achievements_menu(achievements_data):
    while True:
        dis.fill(BACKGROUND_COLOR); draw_grid()
        title = menu_font.render("ДОСТИЖЕНИЯ", True, SNAKE_HIGHLIGHT)
        dis.blit(title, title.get_rect(center=(DIS_WIDTH / 2, 80)))
        if draw_button("Назад", 20, DIS_HEIGHT - 80, 200, 60, pygame.mouse.get_pos(), pygame.mouse.get_pressed()): return
        start_y = 150
        for i, goal in enumerate(ACHIEVEMENT_GOALS):
            key = str(goal)
            color = SNAKE_HIGHLIGHT if achievements_data.get(key) else (80, 80, 80)
            txt = achi_font_small.render(f"{goal}: {ACHIEVEMENT_NAMES[goal]}", True, color)
            dis.blit(txt, (50, start_y + i * 40))
        draw_author()
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        pygame.display.update(); clock.tick(15)

def main_menu(achievements_data):
    while True:
        dis.fill(BACKGROUND_COLOR); draw_grid()
        title = menu_font.render("Змейка", True, SNAKE_HIGHLIGHT)
        dis.blit(title, title.get_rect(center=(DIS_WIDTH / 2, DIS_HEIGHT / 3 - 100)))
        mouse = pygame.mouse.get_pos(); click = pygame.mouse.get_pressed()
        if draw_button("Играть", DIS_WIDTH / 2 - 200, DIS_HEIGHT / 2, 400, 100, mouse, click): return "game"
        if draw_button("Достижения", DIS_WIDTH / 2 - 200, DIS_HEIGHT / 2 + 120, 400, 100, mouse, click): achievements_menu(achievements_data)
        if draw_button("Выход^-^", DIS_WIDTH / 2 - 200, DIS_HEIGHT / 2 + 240, 400, 100, mouse, click): 
            pygame.quit(); sys.exit()
        draw_author()
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        pygame.display.update(); clock.tick(15)

def game_over_screen():
    while True:
        dis.fill(BACKGROUND_COLOR); draw_grid()
        over = menu_font.render("Game Over", True, SNAKE_HIGHLIGHT)
        dis.blit(over, over.get_rect(center=(DIS_WIDTH / 2, DIS_HEIGHT / 3)))
        mouse = pygame.mouse.get_pos(); click = pygame.mouse.get_pressed()
        if draw_button("Play^_0", DIS_WIDTH / 2 - 200, DIS_HEIGHT / 2, 400, 100, mouse, click): return "game"
        if draw_button("Меню", DIS_WIDTH / 2 - 200, DIS_HEIGHT / 2 + 120, 400, 100, mouse, click): return "menu"
        if draw_button("Выход^-^", DIS_WIDTH / 2 - 200, DIS_HEIGHT / 2 + 240, 400, 100, mouse, click): 
            pygame.quit(); sys.exit()
        draw_author()
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        pygame.display.update(); clock.tick(15)

# --- ОСНОВНОЙ ЦИКЛ ИГРЫ ---
def game_loop(achievements_data):
    x1, y1 = DIS_WIDTH // 2, DIS_HEIGHT // 2
    x1_change = y1_change = 0
    snake_list = []
    Length_of_snake = 1
    
    def spawn_food():
        while True:
            fx = round(random.randrange(0, DIS_WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
            fy = round(random.randrange(0, DIS_HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
            if [fx, fy] not in snake_list: return fx, fy

    foodx, foody = spawn_food()
    ach_popup_active = False
    ach_text = ""
    ach_start = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x1_change == 0: x1_change, y1_change = -BLOCK_SIZE, 0
                elif event.key == pygame.K_RIGHT and x1_change == 0: x1_change, y1_change = BLOCK_SIZE, 0
                elif event.key == pygame.K_UP and y1_change == 0: x1_change, y1_change = 0, -BLOCK_SIZE
                elif event.key == pygame.K_DOWN and y1_change == 0: x1_change, y1_change = 0, BLOCK_SIZE
                elif event.key == pygame.K_ESCAPE: return "menu"

        x1 += x1_change; y1 += y1_change

        if len(snake_list) >= Length_of_snake and snake_list: del snake_list[0]
        new_head = [x1, y1]
        snake_list.append(new_head)

        if (x1 // BLOCK_SIZE == foodx // BLOCK_SIZE) and (y1 // BLOCK_SIZE == foody // BLOCK_SIZE):
            Length_of_snake += 1
            foodx, foody = spawn_food()
            new_ach = check_achievement(Length_of_snake, achievements_data)
            if new_ach:
                ach_popup_active = True
                ach_start = time.time()
                ach_text = f"{new_ach[-1][1]} (x{new_ach[-1][0]})"

        if x1 >= DIS_WIDTH or x1 < 0 or y1 >= DIS_HEIGHT or y1 < 0: return "game_over"
        for segment in snake_list[:-1]: 
            if segment == new_head: return "game_over"

        dis.fill(BACKGROUND_COLOR); draw_grid(); draw_detailed_apple(foodx, foody)
        draw_detailed_snake(BLOCK_SIZE, snake_list)
        our_score(Length_of_snake - 1); draw_author()

        if ach_popup_active:
            draw_achievement_popup(ach_text)
            if time.time() - ach_start > 3: ach_popup_active = False

        pygame.display.update(); clock.tick(FPS)

def draw_achievement_popup(text):
    width, height = 400, 120
    x, y = DIS_WIDTH - width - 20, 20
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    pygame.draw.rect(dis, ACHIEVEMENT_BG, (x, y, width, height), border_radius=15)
    pygame.draw.rect(dis, BUTTON_GLOW, (x, y, width, height), width=3, border_radius=15)
    title = achi_font_big.render("Достижение!", True, ACHIEVEMENT_TEXT)
    msg = achi_font_small.render(text, True, ACHIEVEMENT_TEXT)
    dis.blit(title, title.get_rect(center=(x + width/2, y + 35)))
    dis.blit(msg, msg.get_rect(center=(x + width/2, y + 75)))

# --- ЗАПУСК ---
if __name__ == "__main__":
    achievements = load_achievements()
    state = "menu"
    
    while True:
        if state == "menu":
            state = main_menu(achievements)
        elif state == "game":
            state = game_loop(achievements)
        elif state == "game_over":
            state = game_over_screen()
        elif state == "exit":
            break