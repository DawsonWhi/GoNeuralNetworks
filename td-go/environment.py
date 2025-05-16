# go envrionment that stores the state of the game for the agent and gives out the reward
# go envrionment that stores the state of the game for the agent and gives out the reward
import numpy as np


#letter list
letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']
numbers = [str(i) for i in range(1,20)]

#make the board and fill with 0s.
board = np.zeros((19,19))

"""
for i in range(19):
    row = []
    for j in range(19):
        row.append(0)
    board.append(row)
"""
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
                return True
        else: move = input("Invlaid move. Try again: ")


#game!!
playing = True
while playing:
    #Makes playing false if 'EXIT' was entered.
    if not turn(1): playing = False
    if not turn(2): playing = False


print(board)
