# go envrionment that stores the state of the game for the agent and gives out the reward
# go envrionment that stores the state of the game for the agent and gives out the reward
import numpy as np
import agent

#letter list
letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']
numbers = [str(i) for i in range(1,20)]

#make the board and fill with 0s.
board = np.zeros((19,19))
BOARDSIZE = 20

"""
for i in range(19):
    row = []
    for j in range(19):
        row.append(0)
    board.append(row)
"""
#defining neighbors, returns list of neighboring points
def adjacent(point):
    neighbors = [(point[0] - 1, point[1]),
                 (point[0] + 1, point[1]),
                 (point[0], point[1] - 1),
                 (point[0], point[1] + 1)]
    return [point for point in neighbors if 0 <= point[0] < BOARDSIZE and 0 <= point[1] < BOARDSIZE]

#finding liberties - needs adaptation
def liberties(spot, board):
    liberties = [point for point in adjacent(spot) if board[point[0]][point[1]] == 0]
    return set(liberties)


def turn(player):
    #get input & place piece
    move = input("gimmie input: ")
    valid = False
    letter = 'z'
    number = 420

    #Input sanitization
    while not valid:

        #check for empty string & parse
        if move =='': pass
        else:
            letter = move[0]
            number = move[1:]

        
        print(letter,number)

        #exit game
        if move == "EXIT": return False
        
        #place piece
        elif letter in letters and number in numbers:
            if board[letters.index(letter)][numbers.index(number)] == 0:
                valid = True
                board[letters.index(letter)][numbers.index(number)] = player
                libertez = liberties([letters.index(letter), numbers.index(number)], board)
                print(libertez)
                
                return True
                print(adjacent([letters.index(letter), numbers.index(number)]))
        else: move = input("Invlaid move. Try again: ")


#game!!
playing = True
while playing:
    #Makes playing false if 'EXIT' was entered.
    if not turn(1): playing = False
    if not turn(2): playing = False


print(board)

