import numpy as np
import socketio
import threading
import os

def cls():
    os.system('cls' if os.name=='nt' else 'clear')
cls()

sio = socketio.Client()
port = input("Port (default: 5000): ")
sio.connect('http://localhost:5000')

room_id = input("Room id: ")
sio.emit('joinRoom', [room_id])

turns = 0
x_won = False
o_won = False

# 0 is X, 1 is O
my_role = 0

wait_turn_event = threading.Event()
game_started_event = threading.Event()
stop_event = threading.Event()

board = np.array([[0,0,0],[0,0,0],[0,0,0]])
magic_square = np.array([[4,9,2], [3,5,7], [8,1,6]])

def ui():
    symbol_map = {
        0: "   ",
        1: " x ",
        2: " o "
    }

    cls()
    
    # information about your role
    print("You're", end=" ")
    if my_role == 0: print("X") 
    else: print("O")

    print("\n\n\n")

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
    if turn == my_role: 
        choice = input("Your turn: \n")

        try:
            column = int(choice.split(',')[0])-1
            row = int(choice.split(',')[1])-1

            if board[row,column] == 0:
                board[row,column] = turn+1
                sio.emit("sendTurn", [column+1, row+1]);
            else:
                invalid_user_input(turn)
        except:
            invalid_user_input(turn)
    
    else:
        print("Opponent's turn")
        wait_turn_event.wait()

def invalid_user_input(turn):
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
    if turns == 9:
        print("Draw!")
    elif x_won:
        print("X won!")
    elif o_won:
        print("O won!")
    if my_role == 0:
        choice = input("Play again? (Y | N): ")
        if choice.upper() == "Y":
            sio.emit("playAgain")
            reset_game()

def reset_game():
    global turns, x_won, o_won, board, my_role

    # reset every aspect of the match
    turns = 0
    x_won = False
    o_won = False
    board = np.array([[0,0,0],[0,0,0],[0,0,0]])
    
    # change roles
    if my_role == 0: my_role = 1
    else: my_role = 0

    game()

def game():
    global turns
    
    while(turns != 9 and not x_won and not o_won):
        ui()
        user_input(turns % 2)
        check_win_condition()
        turns += 1

    # render the ui one last time to see the final board before the end
    ui()
    end_game()

@sio.on('startMatch')
def startMatch():
    game_started_event.set() 
    game()
    
@sio.on('stopMatch')
def stopMatch():
    print("User left the game...")
    stop_event.set()

@sio.on('getRole')
def getRole(role):
    global my_role
    my_role = role

@sio.on('receiveTurn')
def receiveTurn(turn):
    global turns
    column = int(turn[0])-1
    row = int(turn[1])-1
    board[row,column] = (turns % 2)+1
    wait_turn_event.set()
    wait_turn_event.clear()
    
def wait_for_game_start():
    print("Waiting for the match to start...")
    game_started_event.wait()
    print("Match has started!")
    while not stop_event.is_set():
        pass  # keep thread alive

@sio.on('playAgain')
def playAgain():
    reset_game()

thread = threading.Thread(target=wait_for_game_start)
thread.start()