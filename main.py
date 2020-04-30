def solve(board):
    pos = find_next(board)
    if pos is None:
        return True
    else:
        row, col = pos[0], pos[1]
        for value in range(1, 10):
            if isValid(board, value, row, col):
                board[row][col] = value

                if solve(board):
                    return True

                board[row][col] = 0

    return False

def find_next(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return (i, j)
    return None

def isValid(board, value, row, col):
    for i in range(9):
        if board[row][i] == value or board[i][col] == value:
            return False

    left_border = 3 * (row // 3)
    up_border = 3 * (col // 3)
    for i in range(left_border, left_border + 3):
        for j in range(up_border, up_border + 3):
            if board[i][j] == value:
                return False
    return True

def print_board(board):
    for i in range(9):
        if i and i % 3 == 0:
            print('- - - + - - - + - - -')
        for j in range(9):
            if j and j % 3 == 0:
                print('|', end=' ')
            if j == 8:
                print(board[i][j])
            else:
                print(board[i][j], end=' ')

board = [
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

solve(board)
print_board(board)
