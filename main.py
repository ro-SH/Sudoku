import pygame

WIDTH = 435
HEIGHT = 595
DISPLAY = (WIDTH, HEIGHT)

CELL_WIDTH = 45
BOARD_SIZE = 9

MENU_BG_COLOR = (255, 255, 255)
GAME_BG_COLOR = (255, 255, 255)

MAIN_LINES_COLOR = (0, 0, 0)
EXTRA_LINES_COLOR = (153, 153, 153)

GUESSED_COLOR = (40, 40, 66)

DIGITS_COLOR = (0, 0, 0)
CLICKED_COLOR = (128, 126, 230)
OUTLINE_COLOR = (186, 186, 186)
EQUAL_COLOR = (140, 140, 140)
DIGITS_FONT = 'comicsans'
DIGITS_FONT_SIZE = 40


class Button:

    def __init__(self, x, y, width, height, color, outline=None, text='', text_color=DIGITS_COLOR, font=DIGITS_FONT, font_size=DIGITS_FONT_SIZE):
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
            win.blit(text, (self.x + self.width // 2 - text.get_width() // 2, self.y + self.height // 2 - text.get_height() // 2))

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

        self.playing = True

        self.board = [
            [0, 0, 0, 9, 0, 0, 3, 0, 0],
            [0, 0, 0, 1, 0, 5, 4, 0, 9],
            [0, 0, 0, 3, 0, 4, 0, 6, 0],
            [9, 0, 5, 8, 2, 0, 0, 0, 0],
            [0, 3, 0, 0, 4, 9, 2, 0, 0],
            [2, 7, 0, 5, 0, 0, 0, 8, 0],
            [7, 0, 0, 0, 0, 0, 0, 3, 0],
            [0, 0, 0, 2, 1, 0, 0, 0, 5],
            [0, 8, 0, 7, 0, 3, 1, 0, 0]
        ]

        self.correct_board = [
            [5, 1, 4, 9, 6, 2, 3, 7, 8],
            [3, 6, 7, 1, 8, 5, 4, 2, 9],
            [8, 2, 9, 3, 7, 4, 5, 6, 1],
            [9, 4, 5, 8, 2, 7, 6, 1, 3],
            [1, 3, 8, 6, 4, 9, 2, 5, 7],
            [2, 7, 6, 5, 3, 1, 9, 8, 4],
            [7, 5, 1, 4, 9, 6, 8, 3, 2],
            [6, 9, 3, 2, 1, 8, 7, 4, 5],
            [4, 8, 2, 7, 5, 3, 1, 9, 6]
        ]

        self.buttons_board = [[Button(17 + CELL_WIDTH * j, 97 + CELL_WIDTH * i, CELL_WIDTH - 2, CELL_WIDTH - 2, GAME_BG_COLOR)
                               for j in range(BOARD_SIZE)]
                              for i in range(BOARD_SIZE)
        ]

        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.board[i][j]:
                    self.buttons_board[i][j].text = str(self.board[i][j])

        self.clicked = (-1, -1)
        self.mistakes = 0


    def draw_menu_window(self):
        self.window.fill(MENU_BG_COLOR)

        pygame.display.update()

    def draw_game_window(self):
        self.window.fill(GAME_BG_COLOR)

        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                self.buttons_board[i][j].draw(self.window)

        for i in range(BOARD_SIZE + 1):
            if i % 3:
                pygame.draw.line(self.window, EXTRA_LINES_COLOR, [15 + 45 * i, 95], [15 + 45 * i, HEIGHT - 95], 2)
        for i in range(BOARD_SIZE + 1):
            if i % 3:
                pygame.draw.line(self.window, EXTRA_LINES_COLOR, [15, 95 + 45 * i], [WIDTH - 15, 95 + 45 * i], 2)
        for i in range(0, BOARD_SIZE + 1, 3):
            pygame.draw.line(self.window, MAIN_LINES_COLOR, [15 + 45 * i, 95], [15 + 45 * i, HEIGHT - 95], 2)
        for i in range(0, BOARD_SIZE + 1, 3):
            pygame.draw.line(self.window, MAIN_LINES_COLOR, [15, 95 + 45 * i], [WIDTH - 15, 95 + 45 * i], 2)

        pygame.display.update()

    def start(self):
        running = True

        while running:
            pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                if self.playing:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        for row_index, row in enumerate(self.buttons_board):
                            for col_index, button in enumerate(row):
                                if button.is_over(pos):
                                    if not self.clicked == (-1, -1):
                                        for i in range(BOARD_SIZE):
                                            for j in range(BOARD_SIZE):
                                                self.buttons_board[i][j].color = GAME_BG_COLOR
                                    self.clicked = (row_index, col_index)
                                    for i in range(BOARD_SIZE):
                                        self.buttons_board[self.clicked[0]][i].color = OUTLINE_COLOR
                                        self.buttons_board[i][self.clicked[1]].color = OUTLINE_COLOR
                                    for i in range(3 * (self.clicked[0] // 3), 3 * (self.clicked[0] // 3) + 3):
                                        for j in range(3 * (self.clicked[1] // 3), 3 * (self.clicked[1] // 3) + 3):
                                            self.buttons_board[i][j].color = OUTLINE_COLOR
                                    if button.text:
                                        for i in range(BOARD_SIZE):
                                            for j in range(BOARD_SIZE):
                                                if self.buttons_board[i][j].text == button.text:
                                                    self.buttons_board[i][j].color = EQUAL_COLOR
                                    button.color = CLICKED_COLOR
                else:
                    pass

            keys = pygame.key.get_pressed()
            if self.playing:
                for key in self.keys_dict:
                    if keys[key]:
                        if self.keys_dict[key] == self.correct_board[self.clicked[0]][self.clicked[1]]:
                            self.buttons_board[self.clicked[0]][self.clicked[1]].text = str(self.keys_dict[key])
                            self.buttons_board[self.clicked[0]][self.clicked[1]].text_color = GUESSED_COLOR
                        else:
                            self.mistakes += 1
                            if self.mistakes == 3:
                                # LOSE
                                pass


            if self.playing:
                self.draw_game_window()
            else:
                self.draw_menu_window()

        pygame.quit()


def main():
    SudokuGame().start()

if __name__ == '__main__':
    main()


# def solve(board):
#     pos = find_next(board)
#     if pos is None:
#         return True
#     else:
#         row, col = pos[0], pos[1]
#         for value in range(1, 10):
#             if isValid(board, value, row, col):
#                 board[row][col] = value

#                 if solve(board):
#                     return True

#                 board[row][col] = 0

#     return False

# def find_next(board):
#     for i in range(9):
#         for j in range(9):
#             if board[i][j] == 0:
#                 return (i, j)
#     return None

# def isValid(board, value, row, col):
#     for i in range(9):
#         if board[row][i] == value or board[i][col] == value:
#             return False

#     left_border = 3 * (row // 3)
#     up_border = 3 * (col // 3)
#     for i in range(left_border, left_border + 3):
#         for j in range(up_border, up_border + 3):
#             if board[i][j] == value:
#                 return False
#     return True

# def print_board(board):
#     for i in range(9):
#         if i and i % 3 == 0:
#             print('- - - + - - - + - - -')
#         for j in range(9):
#             if j and j % 3 == 0:
#                 print('|', end=' ')
#             if j == 8:
#                 print(board[i][j])
#             else:
#                 print(board[i][j], end=' ')

# board = [
#     [0, 0, 0, 9, 0, 0, 3, 0, 0],
#     [0, 0, 0, 1, 0, 5, 4, 0, 9],
#     [0, 0, 0, 3, 0, 4, 0, 6, 0],
#     [9, 0, 5, 8, 2, 0, 0, 0, 0],
#     [0, 3, 0, 0, 4, 9, 2, 0, 0],
#     [2, 7, 0, 5, 0, 0, 0, 8, 0],
#     [7, 0, 0, 0, 0, 0, 0, 3, 0],
#     [0, 0, 0, 2, 1, 0, 0, 0, 5],
#     [0, 8, 0, 7, 0, 3, 1, 0, 0]
# ]

# solve(board)
# print_board(board)
