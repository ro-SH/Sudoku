import os
import pygame
import random
import time
import pickle
from copy import deepcopy
from tkinter import Tk, messagebox

WIDTH = 435
HEIGHT = 595
DISPLAY = (WIDTH, HEIGHT)

VERTICAL_OFFSET = 95
HORIZONTAL_OFFSET = 15

LINE_WIDTH = 2
CELL_WIDTH = 45
BOARD_SIZE = 9

MENU_BG_COLOR = (255, 255, 255)
GAME_BG_COLOR = (255, 255, 255)
MENU_BUTTON_COLOR = (255, 255, 255)
MENU_EXTRA_BUTTON_COLOR = (44, 41, 255)

MENU_BUTTON_TEXT = ('Continue', 'New Game')

OVER_COLOR = (245, 245, 245)
EXTRA_OVER_COLOR = (152, 150, 255)

TITLE_FONT = 'candara'
TITLE_COLOR = (0, 0, 0)

MAIN_LINES_COLOR = (0, 0, 0)
EXTRA_LINES_COLOR = (153, 153, 153)

GUESSED_COLOR = (40, 40, 66)

DIGITS_COLOR = (0, 0, 0)
CLICKED_COLOR = (152, 150, 255)
OUTLINE_COLOR = (210, 210, 210)
EQUAL_COLOR = (160, 160, 160)
DIGITS_FONT = 'candara'
DIGITS_FONT_SIZE = 40
ADDITIONAL_TEXT_FONT_SIZE = 20

MAX_MISTAKES = 3

DIFFICULTIES = ('Easy', 'Medium', 'Hard')
DIFFICULTY_CELLS = {
    'Easy': (30, 35),
    'Medium': (25, 29),
    'Hard': (20, 24)
}


class Button:

    def __init__(self, x, y, width, height, color, outline=None, text='', text_color=DIGITS_COLOR,
                 font=DIGITS_FONT, font_size=DIGITS_FONT_SIZE):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.outline = outline
        self.text = text
        self.text_color = text_color
        self.font = font
        self.font_size = font_size

    def draw(self, win):
        if self.outline:
            pygame.draw.rect(win, self.outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)

        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)

        if self.text:
            font = pygame.font.SysFont(self.font, self.font_size)
            text = font.render(self.text, 1, self.text_color)
            win.blit(text, (self.x + self.width // 2 - text.get_width() // 2,
                            self.y + self.height // 2 - text.get_height() // 2))

    def is_over(self, pos):
        if self.x <= pos[0] <= self.x + self.width:
            if self.y <= pos[1] <= self.y + self.height:
                return True

        return False


class SudokuGame:

    keys_dict = {
        pygame.K_0: 0,
        pygame.K_1: 1,
        pygame.K_2: 2,
        pygame.K_3: 3,
        pygame.K_4: 4,
        pygame.K_5: 5,
        pygame.K_6: 6,
        pygame.K_7: 7,
        pygame.K_8: 8,
        pygame.K_9: 9,
    }

    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode(DISPLAY)
        pygame.display.set_caption('Sudoku')

        self.logo = pygame.image.load('img/sudoku_logo.png')
        self.icon = pygame.image.load('icons/sudoku_icon.ico')
        pygame.display.set_icon(self.icon)

        self.menu_title_font = pygame.font.SysFont(TITLE_FONT, 50)
        self.menu_title = self.menu_title_font.render("Sudoku Game", 1, TITLE_COLOR)
        self.play_title_font = pygame.font.SysFont(TITLE_FONT, 40)
        self.play_title = self.play_title_font.render("Sudoku Game", 1, TITLE_COLOR)

        self.playing = False
        self.solving = True
        self.choosing_diffculty = False

        self.menu_buttons = [Button(WIDTH // 4, HEIGHT - (HEIGHT - HEIGHT // 2 - self.menu_title.get_height() // 2) // 2 - HORIZONTAL_OFFSET // 2 - HEIGHT // 8 + i * (HEIGHT // 8 + HORIZONTAL_OFFSET), WIDTH // 2,
                                    HEIGHT // 8, MENU_BUTTON_COLOR, MENU_EXTRA_BUTTON_COLOR,
                                    MENU_BUTTON_TEXT[i], MENU_EXTRA_BUTTON_COLOR, DIGITS_FONT, 30)
                             for i in range(2)]

        self.difficulty_buttons = [Button(WIDTH // 4, HEIGHT // 2 + self.menu_title.get_height() // 2 + i * HEIGHT // 9 + (i + 1) * HORIZONTAL_OFFSET,
                                          WIDTH // 2, HEIGHT // 9, MENU_BUTTON_COLOR, MENU_EXTRA_BUTTON_COLOR,
                                          DIFFICULTIES[i], MENU_EXTRA_BUTTON_COLOR, DIGITS_FONT, 30)
                                   for i in range(3)]

        self.board = [[0 for j in range(BOARD_SIZE)] for i in range(BOARD_SIZE)]

        self.correct_board = [[0 for j in range(BOARD_SIZE)] for i in range(BOARD_SIZE)]

        self.buttons_board = [[Button(HORIZONTAL_OFFSET + LINE_WIDTH + CELL_WIDTH * j,
                                      VERTICAL_OFFSET + LINE_WIDTH + CELL_WIDTH * i,
                                      CELL_WIDTH - LINE_WIDTH, CELL_WIDTH - LINE_WIDTH, GAME_BG_COLOR)
                               for j in range(BOARD_SIZE)]
                              for i in range(BOARD_SIZE)
        ]

        self.solve_button = Button(HORIZONTAL_OFFSET,
                                   HEIGHT - VERTICAL_OFFSET + HORIZONTAL_OFFSET,
                                   CELL_WIDTH * 3 + LINE_WIDTH,
                                   VERTICAL_OFFSET - 2 * HORIZONTAL_OFFSET, CLICKED_COLOR,
                                   None, "Solve", GAME_BG_COLOR,
                                   DIGITS_FONT, ADDITIONAL_TEXT_FONT_SIZE
        )

        self.exit_button = Button(WIDTH - HORIZONTAL_OFFSET - CELL_WIDTH * 3,
                                  HEIGHT - VERTICAL_OFFSET + HORIZONTAL_OFFSET,
                                  CELL_WIDTH * 3 + LINE_WIDTH,
                                  VERTICAL_OFFSET - 2 * HORIZONTAL_OFFSET, CLICKED_COLOR,
                                  None, 'Exit', GAME_BG_COLOR,
                                  DIGITS_FONT, ADDITIONAL_TEXT_FONT_SIZE)

        self.additional_text_font = pygame.font.SysFont(DIGITS_FONT, ADDITIONAL_TEXT_FONT_SIZE)
        self.clicked = (-1, -1)
        self.mistakes = 0
        self.difficulty = None
        self.start_time = None
        self.current_time = None
        self.highscores = self.get_highscores()

        self.func = {
            0: self.transpose,
            1: self.swap_rows_in_area,
            2: self.swap_cols_in_area,
            3: self.swap_horizontal_areas,
            4: self.swap_vertical_areas
        }

    def create_board(self, difficulty):
        temp_board = []
        self.initialize(temp_board)
        for i in range(35):
            self.func[random.randint(0, 4)](temp_board)
        self.correct_board = deepcopy(temp_board)

        open_cells = BOARD_SIZE * BOARD_SIZE - random.randint(DIFFICULTY_CELLS[difficulty][0],
                                                              DIFFICULTY_CELLS[difficulty][1])
        count = 0
        while count < open_cells:
            pos = (random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1))
            if temp_board[pos[0]][pos[1]]:
                temp_board[pos[0]][pos[1]] = 0
                count += 1
        if count == open_cells and self.solve(deepcopy(temp_board), False):
            self.board = deepcopy(temp_board)
        else:
            self.create_board()

    def initialize(self, board):
        for i in range(BOARD_SIZE):
            board.append([])
            for j in range(BOARD_SIZE):
                if not i % 3:
                    board[i].append(i // 3 + 1 + j)
                else:
                    try:
                        board[i].append(board[i - 1][j + 3])
                    except IndexError:
                        board[i].append(board[i - 1][j - 6])
                if board[i][j] > 9:
                    board[i][j] -= 9

    def transpose(self, board):
        board = list(map(list, zip(*board)))

    def swap_rows_in_area(self, board):
        first, second = self.find_random_lines()
        for j in range(BOARD_SIZE):
            board[first][j], board[second][j] = board[second][j], board[first][j]

    def swap_cols_in_area(self, board):
        first, second = self.find_random_lines()
        for i in range(BOARD_SIZE):
            board[i][first], board[i][second] = board[i][second], board[i][first]

    def swap_horizontal_areas(self, board):
        first, second = self.find_random_areas()
        for i in range(3):
            for j in range(BOARD_SIZE):
                board[first * 3 + i][j], board[second * 3 + i][j] = board[second * 3 + i][j], board[first * 3 + i][j]

    def swap_vertical_areas(self, board):
        first, second = self.find_random_areas()
        for i in range(BOARD_SIZE):
            for j in range(3):
                board[i][first * 3 + j], board[i][second * 3 + j] = board[i][second * 3 + j], board[i][first * 3 + j]

    def find_random_areas(self):
        first = random.randint(0, 2)
        second = None
        while second is None or second == first:
            second = random.randint(0, 2)
        return (first, second)

    def find_random_lines(self):
        area = random.randint(0, 2)
        first = random.randint(area * 3, area * 3 + 2)
        second = None
        while second is None or second == first:
            second = random.randint(area * 3, area * 3 + 2)
        return (first, second)

    def save_game(self):
        data = {
            'difficulty': self.difficulty,
            'time': self.format_time(self.current_time),
            'mistakes': self.mistakes,
            'board': self.board
        }
        with open('last_game.pickle', 'wb') as file:
            pickle.dump(data, file)

    def solve(self, board=None, display=True):
        if display and board is None:
            board = self.board
        pos = self.find_next(board)
        if pos is None:
            return True
        else:
            row, col = pos[0], pos[1]
            for value in range(1, 10):
                if self.isValid(board, value, row, col):
                    board[row][col] = value
                    if display:
                        self.buttons_board[row][col].text = str(value)
                        self.buttons_board[row][col].draw(self.window)
                        # pygame.time.delay(20)
                        pygame.display.update()
                        if self.solve():
                            return True
                    else:
                        if self.solve(board, False):
                            return True

                    board[row][col] = 0

        return False

    def find_next(self, board):
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if board[i][j] == 0:
                    return (i, j)
        return None

    def isValid(self, board, value, row, col):
        for i in range(BOARD_SIZE):
            if board[row][i] == value or board[i][col] == value:
                return False

        left_border = 3 * (row // 3)
        up_border = 3 * (col // 3)
        for i in range(left_border, left_border + 3):
            for j in range(up_border, up_border + 3):
                if board[i][j] == value:
                    return False
        return True

    def change_highlighting(self, pos=(-1, -1)):
        if not self.clicked == (-1, -1):
            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE):
                    self.buttons_board[i][j].color = GAME_BG_COLOR
        self.clicked = (pos[0], pos[1])
        if not self.clicked == (-1, -1):
            for i in range(BOARD_SIZE):
                self.buttons_board[self.clicked[0]][i].color = OUTLINE_COLOR
                self.buttons_board[i][self.clicked[1]].color = OUTLINE_COLOR
            for i in range(3 * (self.clicked[0] // 3), 3 * (self.clicked[0] // 3) + 3):
                for j in range(3 * (self.clicked[1] // 3), 3 * (self.clicked[1] // 3) + 3):
                    self.buttons_board[i][j].color = OUTLINE_COLOR
            if self.buttons_board[self.clicked[0]][self.clicked[1]].text:
                for i in range(BOARD_SIZE):
                    for j in range(BOARD_SIZE):
                        if self.buttons_board[i][j].text == self.buttons_board[self.clicked[0]][self.clicked[1]].text:
                            self.buttons_board[i][j].color = EQUAL_COLOR
            self.buttons_board[self.clicked[0]][self.clicked[1]].color = CLICKED_COLOR

    def draw_menu_window(self):
        self.window.fill(MENU_BG_COLOR)

        self.window.blit(self.logo, (WIDTH // 2 - self.logo.get_width() // 2, HEIGHT // 9))

        self.window.blit(self.menu_title, (WIDTH // 2 - self.menu_title.get_width() // 2,
                                           HEIGHT // 2 - self.menu_title.get_height() // 2))

        if self.choosing_diffculty:
            for button in self.difficulty_buttons:
                button.draw(self.window)
            for difficulty, time in self.highscores.items():
                for button in self.difficulty_buttons:
                    if button.text == difficulty:
                        if time is None:
                            text = self.additional_text_font.render("No highscore yet", 1, EXTRA_LINES_COLOR)
                        else:
                            text = self.additional_text_font.render(self.format_time(time), 1, EXTRA_LINES_COLOR)
                        self.window.blit(text, ((2 * button.x + button.width) // 2 - text.get_width() // 2, button.y + button.height * 2 // 3))

        else:
            for button in self.menu_buttons:
                if not (button.text == MENU_BUTTON_TEXT[0] and not self.isSaved()):
                    button.draw(self.window)

        pygame.display.update()

    def draw_cells(self):
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                self.buttons_board[i][j].draw(self.window)

    def draw_board(self):
        for i in range(BOARD_SIZE + 1):
            if i % 3:
                pygame.draw.line(self.window, EXTRA_LINES_COLOR,
                                 [HORIZONTAL_OFFSET + CELL_WIDTH * i, VERTICAL_OFFSET],
                                 [HORIZONTAL_OFFSET + CELL_WIDTH * i, HEIGHT - VERTICAL_OFFSET],
                                 LINE_WIDTH)

        for i in range(BOARD_SIZE + 1):
            if i % 3:
                pygame.draw.line(self.window, EXTRA_LINES_COLOR,
                                 [HORIZONTAL_OFFSET, VERTICAL_OFFSET + CELL_WIDTH * i],
                                 [WIDTH - HORIZONTAL_OFFSET, VERTICAL_OFFSET + CELL_WIDTH * i],
                                 LINE_WIDTH)

        for i in range(0, BOARD_SIZE + 1, 3):
            pygame.draw.line(self.window, MAIN_LINES_COLOR,
                             [HORIZONTAL_OFFSET + CELL_WIDTH * i, VERTICAL_OFFSET],
                             [HORIZONTAL_OFFSET + CELL_WIDTH * i, HEIGHT - VERTICAL_OFFSET],
                             LINE_WIDTH)

        for i in range(0, BOARD_SIZE + 1, 3):
            pygame.draw.line(self.window, MAIN_LINES_COLOR,
                             [HORIZONTAL_OFFSET, VERTICAL_OFFSET + CELL_WIDTH * i],
                             [WIDTH - HORIZONTAL_OFFSET, VERTICAL_OFFSET + CELL_WIDTH * i],
                             LINE_WIDTH)

    def draw_game_window(self):
        self.window.fill(GAME_BG_COLOR)

        self.window.blit(self.play_title, (WIDTH // 2 - self.play_title.get_width() // 2,
                                           VERTICAL_OFFSET // 2 - self.play_title.get_height() // 2))

        mistakes_text = self.additional_text_font.render(f"Mistakes: {self.mistakes}/{MAX_MISTAKES}",
                                                         0, EXTRA_LINES_COLOR)
        self.window.blit(mistakes_text, (WIDTH - mistakes_text.get_width() - 2 * HORIZONTAL_OFFSET, VERTICAL_OFFSET - ADDITIONAL_TEXT_FONT_SIZE))

        difficulty_text = self.additional_text_font.render(self.difficulty, 0, EXTRA_LINES_COLOR)
        self.window.blit(difficulty_text, (2 * HORIZONTAL_OFFSET, VERTICAL_OFFSET - ADDITIONAL_TEXT_FONT_SIZE))

        time_text = self.additional_text_font.render(self.format_time(self.current_time), 0 , EXTRA_LINES_COLOR)
        self.window.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, VERTICAL_OFFSET - ADDITIONAL_TEXT_FONT_SIZE))

        self.draw_cells()
        self.draw_board()

        self.solve_button.draw(self.window)
        self.exit_button.draw(self.window)
        pygame.display.update()

    def format_time(self, time):
        secs = time % 60
        mins = time // 60
        result = f"{mins}:{secs}"
        if mins < 10:
            result = "0"+result
        if secs < 10:
            result = result[:-1] + "0" + result[-1]
        return result

    def time_from_str(self, time_str):
        time = list(map(int, time_str.split(':')))
        return time[0] * 60 + time[1]

    def fill_buttons(self):
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.board[i][j]:
                    self.buttons_board[i][j].text = str(self.board[i][j])
                else:
                    self.buttons_board[i][j].text = ''

    def start_new_game(self, difficulty):
        self.solving = True
        self.playing = True
        self.mistakes = 0
        self.clicked = (-1, -1)
        self.difficulty = difficulty
        self.create_board(difficulty)

        self.fill_buttons()

        self.start_time = time.time()
        self.current_time = self.start_time

    def isSaved(self):
        if os.path.getsize('last_game.pickle') > 0:
            return True
        return False

    def continue_game(self):
        try:
            with open("last_game.pickle", 'rb') as file:
                data = pickle.load(file)
            self.solving = True
            self.difficulty = data['difficulty']
            if self.difficulty not in DIFFICULTIES:
                raise ValueError
            self.current_time = time.time()
            self.start_time = self.current_time - self.time_from_str(data['time'])
            self.mistakes = data['mistakes']
            if self.mistakes > 2:
                raise ValueError
            self.board = data['board']
            if not len(self.board) == BOARD_SIZE:
                raise ValueError
            for row in self.board:
                if not len(row) == BOARD_SIZE:
                    raise ValueError
                for el in row:
                    if not 0 <= el <= 9:
                        raise ValueError
            self.fill_buttons()
            with open("last_game.pickle", 'wb') as file:
                pass
        except:
            raise ValueError('Wrong data')
            return False
        return True

    def get_highscores(self):
        try:
            # with open('highscores.txt') as file:
            #     result = {}
            #     for i in range(3):
            #         highscore = file.readline().split()[1]
            #         if highscore == '-':
            #             result[DIFFICULTIES[i]] = None
            #         else:
            #             result[DIFFICULTIES[i]] = self.time_from_str(highscore)
            #     return result
            with open('highscores.pickle', 'rb') as file:
                data = pickle.load(file)
            if not len(data) == 3:
                raise ValueError
            for difficulty, time in data.items():
                if difficulty not in DIFFICULTIES:
                    raise ValueError
            return data
        except:
            raise ValueError('Wrong data')

    def update_highscores(self):
        # with open('highscores.txt', 'w') as file:
        #     for difficulty, time in self.highscores.items():
        #         file.write(f'{difficulty}: ')
        #         if time is None:
        #             file.write('-')
        #         else:
        #             file.write(self.format_time(time))
        #         file.write('\n')
        with open('highscores.pickle', 'wb') as file:
            pickle.dump(self.highscores, file)

    def start(self):
        running = True

        while running:
            pos = pygame.mouse.get_pos()
            if self.playing and self.find_next(self.board):
                self.current_time = round(time.time() - self.start_time)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.playing and self.find_next(self.board) is not None:
                        self.save_game()
                    running = False
                    break

                if self.playing:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        for row in range(BOARD_SIZE):
                            for col in range(BOARD_SIZE):
                                if self.buttons_board[row][col].is_over(pos):
                                    self.change_highlighting((row, col))
                        if self.solve_button.is_over(pos):
                            self.solve()
                            self.solving = False
                            self.change_highlighting()
                        elif self.exit_button.is_over(pos):
                            if self.find_next(self.board) is not None:
                                self.save_game()
                            self.playing = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key in self.keys_dict:
                            if self.keys_dict[event.key] == self.correct_board[self.clicked[0]][self.clicked[1]]:
                                self.board[self.clicked[0]][self.clicked[1]] = self.keys_dict[event.key]
                                self.buttons_board[self.clicked[0]][self.clicked[1]].text = str(self.keys_dict[event.key])
                                self.buttons_board[self.clicked[0]][self.clicked[1]].text_color = GUESSED_COLOR
                                if self.find_next(self.board) is None and self.solving:
                                    if self.highscores[self.difficulty] is None or self.current_time < self.highscores[self.difficulty]:
                                        self.highscores[self.difficulty] = self.current_time
                                        self.update_highscores()
                                    Tk().wm_withdraw()
                                    result = messagebox.askyesno('Victory', f'You\'ve won on {self.difficulty} difficulty in {self.format_time(self.current_time)}.\nWould you like to play again?')
                                    self.playing = False
                                    if result:
                                        self.choosing_diffculty = True
                            else:
                                if not self.board[self.clicked[0]][self.clicked[1]]:
                                    self.mistakes += 1
                                    if self.mistakes == MAX_MISTAKES:
                                        Tk().wm_withdraw()
                                        result = messagebox.askyesno('Loss', f'You\'ve lost\nWould you like to play again?')
                                        self.playing = False
                                        if result:
                                            self.choosing_diffculty = True
                        elif event.key == pygame.K_LEFT and self.clicked[1] > 0:
                            self.change_highlighting((self.clicked[0], self.clicked[1] - 1))
                        elif event.key == pygame.K_RIGHT and -1 < self.clicked[1] < 8:
                            self.change_highlighting((self.clicked[0], self.clicked[1] + 1))
                        elif event.key == pygame.K_UP and self.clicked[0] > 0:
                            self.change_highlighting((self.clicked[0] - 1, self.clicked[1]))
                        elif event.key == pygame.K_DOWN and -1 < self.clicked[0] < 8:
                            self.change_highlighting((self.clicked[0] + 1, self.clicked[1]))
                elif self.choosing_diffculty:
                    if event.type == pygame.MOUSEMOTION:
                        for button in self.difficulty_buttons:
                            if button.is_over(pos) and self.choosing_diffculty:
                                button.color = OVER_COLOR
                                button.text_color = EXTRA_OVER_COLOR
                                button.outline = EXTRA_OVER_COLOR
                            else:
                                button.color = MENU_BUTTON_COLOR
                                button.text_color = MENU_EXTRA_BUTTON_COLOR
                                button.outline = MENU_EXTRA_BUTTON_COLOR
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        for button in self.difficulty_buttons:
                            if self.choosing_diffculty and button.is_over(pos):
                                self.choosing_diffculty = False
                                self.start_new_game(button.text)
                else:
                    if event.type == pygame.MOUSEMOTION:
                        for button in self.menu_buttons:
                            if button.is_over(pos) and not self.choosing_diffculty:
                                button.color = OVER_COLOR
                                button.text_color = EXTRA_OVER_COLOR
                                button.outline = EXTRA_OVER_COLOR
                            else:
                                button.color = MENU_BUTTON_COLOR
                                button.text_color = MENU_EXTRA_BUTTON_COLOR
                                button.outline = MENU_EXTRA_BUTTON_COLOR
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        for button in self.menu_buttons:
                            if not self.choosing_diffculty and button.is_over(pos):
                                if button.text == MENU_BUTTON_TEXT[0] and self.isSaved():
                                    self.continue_game()
                                    self.playing = True
                                    pass
                                elif button.text == MENU_BUTTON_TEXT[1]:
                                    self.choosing_diffculty = True

            if self.playing:
                self.draw_game_window()
            else:
                self.draw_menu_window()

        pygame.quit()


def main():
    SudokuGame().start()

if __name__ == '__main__':
    main()
