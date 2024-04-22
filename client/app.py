import numpy as np
import socketio

import threading  # Import threading module to create a blocking mechanism

sio = socketio.Client()
sio.connect('http://localhost:5000')
sio.emit('joinRoom', ["room"])

print('my sid is', sio.sid)

turns = 0
x_won = False
o_won = False

board = np.array([[0,0,0],[0,0,0],[0,0,0]])
magic_square = np.array([[4,9,2], [3,5,7], [8,1,6]])

def ui():
    symbol_map = {
        0: "   ",
        1: " x ",
        2: " o "
    }

    print("\n\n\n\n")

    print(f"{symbol_map.get(board[0, 0], "?")} | {symbol_map.get(board[0, 1], "?")} | {symbol_map.get(board[0, 2], "?")}")
    print("- - + - - + - -")
    print(f"{symbol_map.get(board[1, 0], "?")} | {symbol_map.get(board[1, 1], "?")} | {symbol_map.get(board[1, 2], "?")}")
    print("- - + - - + - -")
    print(f"{symbol_map.get(board[2, 0], "?")} | {symbol_map.get(board[2, 1], "?")} | {symbol_map.get(board[2, 2], "?")}")

    print("\n")

def user_input(turn):
    # if turn is 0, it's "x" turn, if it's 1, it's "o" turn
    global board

    print("Example: (1,2 means first column, second row)")

    choice = ""
    if turn == 0: choice = input("X turn: ")
    else: choice = input("O turn: ")

    column = int(choice.split(',')[0])-1
    row = int(choice.split(',')[1])-1
    
    if board[row,column] == 0:
        board[row,column] = turn+1
    else:
        ui()
        print("Invalid turn")
        user_input(turn)

def check_win_condition():
    global x_won, o_won

    magic_board = board * magic_square

    diagonal=0;
    reverse_diagonal=0;

    for i in range(3):
        # diagonals
        diagonal += magic_board[i,i]
        reverse_diagonal += magic_board[2-i,i]

        # columns
        if magic_board[i,:].sum() == 15:
            x_won = True
        elif magic_board[i,:].sum() == 30:
            o_won = True

        # rows
        if magic_board[:,i].sum() == 15:
            x_won = True
        elif magic_board[:,i].sum() == 30:
            o_won = True

    if diagonal == 15 or reverse_diagonal == 15:
        x_won = True
    elif diagonal == 30 or reverse_diagonal == 30:
        o_won = True

def end_game():
    global turns, x_won, o_won, board
    if turns == 9:
        print("Draw!")
    elif x_won:
        print("X won!")
    elif o_won:
        print("O won!")

    choice = input("Play again? (Y | N): ")
    if choice.upper() == "Y":
        turns = 0
        x_won = False
        o_won = False
        board = np.array([[0,0,0],[0,0,0],[0,0,0]])
        
        game()

def game():
    global turns
    
    while(turns != 9 and not x_won and not o_won):
        ui()
        user_input(turns % 2)
        check_win_condition()
        turns += 1

    end_game()

# Define a function to handle user input for quitting the game
def quit_game():
    while True:
        choice = input()
        if choice.lower() == "quit":
            print("Quitting the game...")
            event.clear()
            exit()

# Start the thread to handle user input for quitting the game
quit_thread = threading.Thread(target=quit_game)
quit_thread.start()

event = threading.Event()

@sio.on('startMatch')
def receiveMessage():
    print("started")
    game()
    