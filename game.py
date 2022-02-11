import sys
import pygame
from pygame.locals import *
import json
import random
import time

# init font
pygame.font.init()
pygame.init()
WIN_WIDTH = 600
WIN_HEIGHT = 900
HEAD_FONT = pygame.font.SysFont('georgiabold', 40)
N_FONT = pygame.font.SysFont('georgiabold', 35)
DARK = pygame.Color("#000000")
WHITE = pygame.Color("#FFFFFF")
GRAY = pygame.Color("#818384")
PRESENT_COLOR = pygame.Color("#b59f3b")
CORRECT_COLOR = pygame.Color("#538d4e")
ABSENT_COLOR = pygame.Color("#3a3a3c")
keyboard = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
GRID_HEIGHT = 72
GRID_WIDTH = 72
BUTTON_WIDTH = 50
GRID_GAP = 5
ALPHABET = "abcdefghijklmnopqrstuvwxyz"
GAME_OVER = False
game_result = ""


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_pos(self):
        return self.x, self.y


class KeyBoard:
    def __init__(self, pos, window):
        self.gap = 5
        self.keyboard_pos = pos
        self.win = window
        self.pos = [
            self.keyboard_pos,
            Point(self.keyboard_pos.x + 0.5 * BUTTON_WIDTH, self.keyboard_pos.y + BUTTON_WIDTH + self.gap),
            Point(self.keyboard_pos.x + self.gap + 1.5 * BUTTON_WIDTH, self.keyboard_pos.y + (BUTTON_WIDTH + self.gap)*2)
        ]
        self.buttons = {}
        for p, row in zip(self.pos, keyboard):
            for index in range(len(row)):
                self.buttons[row[index]] = Button(row[index], Point(p.x + index * (self.gap + BUTTON_WIDTH), p.y))

        self.Delete = Button("DELETE", Point(self.pos[0].x, self.pos[2].y), key_type="function")
        self.Enter = Button("ENTER", Point(self.buttons['M'].pos.x + BUTTON_WIDTH + self.gap, self.pos[2].y),
                            key_type="function")
        self.buttons["DELETE"] = self.Delete
        self.buttons["ENTER"] = self.Enter

    def draw(self):
        for B in self.buttons.values():
            B.draw(self.win)

    def update(self):
        for B in self.buttons.values():
            if B.key_type == "normal":
                B.update_status()
        self.draw()

    def game_over(self):
        for B in self.buttons.values():
            B.border_color = DARK
            B.word = ""
            B.draw(self.win)


class Button:
    def __init__(self, word, pos, key_type="normal"):
        self.word = word
        self.pos = pos
        self.key_type = key_type
        if self.key_type == "normal":
            self.width = BUTTON_WIDTH
            self.height = BUTTON_WIDTH
            self.text = pygame.font.SysFont('georgiabold', 25)
        if self.key_type == "function":
            self.width = BUTTON_WIDTH * 1.5
            self.height = BUTTON_WIDTH
            self.text = pygame.font.SysFont('georgiabold', 15)
        self.rect = Rect(self.pos.x, self.pos.y, self.width, self.height)
        self.border_color = GRAY

    def update_status(self):
        if ALPHABET_ANS[self.word] == "CORRECT":
            self.border_color = CORRECT_COLOR

        elif ALPHABET_ANS[self.word] == "PRESENT":
            self.border_color = PRESENT_COLOR

        elif ALPHABET_ANS[self.word] == "ABSENT":
            self.border_color = ABSENT_COLOR
        else:
            self.border_color = GRAY

    def draw(self, win):
        text_surface = self.text.render(self.word, True, WHITE)
        text_width, text_height = text_surface.get_size()
        pygame.draw.rect(win, self.border_color, self.rect, border_radius=10)
        p_w = (self.width - text_width) / 2
        p_h = (self.height - text_height) / 2
        win.blit(text_surface, (self.pos.x + p_w, self.pos.y + p_h))


class Table:
    def __init__(self, start_pos, win):
        self.x, self.y = start_pos.get_pos()
        self.grid_list = [
            [Grid(Point(self.x + x * (GRID_GAP + GRID_WIDTH), self.y + y * (GRID_GAP + GRID_WIDTH))) for x in range(5)]
            for y in range(6)]
        self.current_row = 0
        self.current_col = -1
        self.win = win

    def draw(self):
        for row in self.grid_list:
            for grid in row:
                grid.draw(self.win)

    def guess(self, word, result):
        if self.current_row == 6:
            print("GAME OVER")
        else:
            for index, grid in enumerate(self.grid_list[self.current_row]):
                time.sleep(0.4)
                grid.update_word(word[index])
                grid.update_status(result[index])
                grid.draw(self.win)
                pygame.display.update()
            self.current_row += 1
            self.current_col = -1

    def type_word(self, word):
        if self.current_col < 4:
            self.current_col += 1
            grid = self.grid_list[self.current_row][self.current_col]
            grid.update_word(word)
            grid.draw(self.win)

    def delete_word(self):
        if self.current_col >= 0:
            grid = self.grid_list[self.current_row][self.current_col]
            grid.delete()
            grid.draw(self.win)
            self.current_col -= 1

    def game_over(self):
        ## 清空文字
        for row in self.grid_list[0:self.current_row]:
            for grid in row:
                grid.word = ""
        ## 清空未使用表格
        for row in self.grid_list[self.current_row:]:
            for grid in row:
                grid.word = ""
                grid.border_color = DARK
        self.draw()


class Grid:
    def __init__(self, pos):
        self.border_color = GRAY
        self.border_size = 2
        self.width = GRID_WIDTH
        self.win_pos = pos
        self.bg = pygame.Surface((self.width, self.width))
        self.bd = self.bg.convert()
        self.rect = Rect(0, 0, self.width, self.width)
        self.word = ""
        self.text = pygame.font.SysFont('georgiabold', 40)

    def draw(self, win):
        text_surface = self.text.render(self.word, True, WHITE)
        text_width, text_height = text_surface.get_size()
        # 沒有顏色填充
        if self.border_size:
            pygame.draw.rect(self.bg, self.border_color, self.rect, self.border_size)
        # 顏色填充
        else:
            pygame.draw.rect(self.bg, self.border_color, self.rect)
        self.bg.blit(text_surface, ((self.width - text_width) // 2, (self.width - text_height) // 2))
        win.blit(self.bg, self.win_pos.get_pos())

    def update_word(self, word):
        self.word = word

    def update_status(self, result):
        if result == "PRESENT":
            self.border_color = PRESENT_COLOR
        elif result == "ABSENT":
            self.border_color = ABSENT_COLOR
        else:
            self.border_color = CORRECT_COLOR
        self.border_size = None

    def delete(self):
        self.border_color = GRAY
        pygame.draw.rect(self.bg, DARK, self.rect)
        self.word = ""


def draw_window():
    pygame.display.set_caption('WORDLE')
    window_surface = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    window_surface.fill(DARK)
    return window_surface


def window_init(window):
    text_surface = HEAD_FONT.render('WORDLE', True, WHITE)
    text_width, text_height = text_surface.get_size()
    window.blit(text_surface, ((WIN_WIDTH - text_width) // 2, 5))
    pygame.draw.line(window, WHITE, (0, 7 + text_height), (WIN_WIDTH, 7 + text_height), 1)


def game_over_text():
    text = N_FONT.render(game_result, True, WHITE)
    text_width, text_height = text.get_size()
    window.blit(text, ((WIN_WIDTH - text_width) // 2, 600))
    text = N_FONT.render(f'Answer : {ANSWER}', True, CORRECT_COLOR)
    text_width, text_height = text.get_size()
    window.blit(text, ((WIN_WIDTH - text_width) // 2, 650))
    text = N_FONT.render(f'Guess times : {table.current_row}', True, PRESENT_COLOR)
    text_width, text_height = text.get_size()
    window.blit(text, ((WIN_WIDTH - text_width) // 2, 700))


def check(guess):
    result = ["" for i in range(5)]
    active = {k: ANSWER.count(k) for k in list(set(ANSWER))}
    for i in range(len(ANSWER)):
        if ANSWER[i] == guess[i]:
            ALPHABET_ANS[guess[i]] = "CORRECT"
            active[guess[i]] -= 1
            result[i] = "CORRECT"

    for i in range(len(ANSWER)):
        if result[i] == "":
            if guess[i] in ANSWER and active[guess[i]]:
                if ALPHABET_ANS[guess[i]] != "CORRECT":
                    ALPHABET_ANS[guess[i]] = "PRESENT"
                result[i] = "PRESENT"
                active[guess[i]] -= 1
            else:
                if ALPHABET_ANS[guess[i]] not in ["CORRECT", "PRESENT"]:
                    ALPHABET_ANS[guess[i]] = "ABSENT"
                result[i] = "ABSENT"

    return result


def guess_input(word):
    result = check(word)
    table.guess(word, result)
    key_board.update()
    global game_result
    if table.current_row == 6:
        game_result = "GAME OVER"
        return True
    for r in result:
        if r != "CORRECT":
            game_result = "Success"
            return False
    return True





with open('Wordle_pygame/voc.json') as f:
    WORD_LIST = json.load(f)['wordle']["vocab"]
ANSWER = random.choice(WORD_LIST).upper()
ALPHABET_ANS = {t.upper(): "normal" for t in ALPHABET}
#print(ANSWER)

window = draw_window()
window_init(window)
TABLE_POS = Point(x=(WIN_WIDTH - GRID_WIDTH * 5 - GRID_GAP * 4) / 2, y=125)
KEYBOARD_POS = Point(x=27.5, y=650)
table = Table(TABLE_POS, window)
key_board = KeyBoard(KEYBOARD_POS, window)
table.draw()
key_board.draw()
pygame.display.update()
text = ""
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        # keyboard input
        if event.type == pygame.KEYDOWN:
            if not GAME_OVER:
                if event.key == pygame.K_RETURN:
                    if len(text) == 5:
                        if text.lower() in WORD_LIST:
                            GAME_OVER = guess_input(text)
                            text = ""
                        else:
                            for i in range(len(text)):
                                table.delete_word()
                                text = ""
                elif event.key == pygame.K_BACKSPACE:
                    if len(text) > 0:
                        table.delete_word()
                        text = text[:-1]
                elif len(text) < 5 and event.unicode.isalpha():
                    t = event.unicode.upper()
                    table.type_word(t)
                    text += t
        # Mouseclick input
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not GAME_OVER:
                for b in key_board.buttons.values():
                    if b.rect.collidepoint(event.pos):
                        if b.word == "ENTER":
                            if len(text) == 5:
                                if text.lower() in WORD_LIST:
                                    GAME_OVER = guess_input(text)
                                    text = ""
                                else:
                                    for i in range(len(text)):
                                        table.delete_word()
                                        text = ""
                        elif b.word == "DELETE":
                            if len(text) > 0:
                                table.delete_word()
                                text = text[:-1]
                        elif len(text) < 5:
                            t = b.word.upper()
                            table.type_word(t)
                            text += t
        if GAME_OVER:
            table.game_over()
            key_board.game_over()
            game_over_text()
    pygame.display.update()
