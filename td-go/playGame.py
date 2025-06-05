from environment import *
from players import Player
from scoring import compute_game_result
from collections import namedtuple
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model, load_model
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
import logging
tf.get_logger().setLevel(logging.ERROR)
WINDOW_LENGTH = 40
WINDOW_STEP = 3
BEAM_SIZE = 8
NEXT_COORDINATES = 4
MAX_LENGTH = 50
INPUT_FILE_NAME = 'GoExampleData.txt'
load_model = tf.keras.models.load_model('saved_model.h5')

file = open(INPUT_FILE_NAME, 'r', encoding='utf-8')
text = file.read()
file.close()
text = text.replace('\n', ' ')
text = text.replace('  ', ' ')
text = text.replace('B', ' ')
text = text.replace('W', ' ')
text = text.replace(';', ' ')



class Game:


    #Takes a Position and color of player and returns a string to give to the neural net
    def input_to_move(self, move, color):
        row = move[0] + 97
        col = move[1] + 97
        move_string = color.upper() + "[" + chr(row) + chr(col) + "]" 
        return move_string

    #Takes the string outputted by the neural net, parses it, and returns a Position
    def move_to_input(self, move) -> Position:
        for index, char in enumerate(move):
            row = move[index+1]
            col = move[index+2]
            if char == "[" and row.islower() and row.isalpha() and col.islower() and col.isalpha():
                return Position(ord(row)-97, ord(col)-97)

                

    def get_formatted_move(self, boardsize: int) -> Position:
        Position = namedtuple("Position", ["x", "y"])
        while True:
            user_input = input(f"Enter your move as 'row,col' (1-{boardsize}) or 'pass': ")
            if user_input.lower() == "pass":
                return Position(-1, -1)
            try:
                row_str, col_str = user_input.strip().split(",")
                row, col = int(row_str) - 1 , int(col_str) -1
                if 0 <= row < boardsize and 0 <= col < boardsize:
                    return Position(row, col)
                else:
                    print(f"Both numbers must be between 1 and {boardsize}.")
            except ValueError:
                print("Invalid format. Please enter as row,col (e.g., 3,4).")

    def get_bot_move(self, prev_move, player) -> Position:
        translate_prev_move = self.input_to_move(prev_move, player.color)
        move = ai_predict(translate_prev_move)
        return self.move_to_input(move)



    def play_game(self, player1, player2, BOARDSIZE=19):
        board = GoBoard(BOARDSIZE)
        current_player = player1
        game_over = False
        valid_move = False
        pass_flag = 0
        prev_move = Position(-1, -1)

        while not game_over | (pass_flag == 2):  # Game continues until two consecutive passes

            while(not valid_move): # valid_move is True when a valid move is made
                board.display()
                print(f"{current_player.name}'s turn ({current_player.color})")
                if current_player.is_human:
                    move = self.get_formatted_move(BOARDSIZE)
                    valid_move = board.place_stone(move, current_player.color)
                    if move.x == -1 and move.y == -1:
                        print(f"{current_player.name} passes.")
                        valid_move = True
                        pass_flag += 1
                    else:
                        pass_flag = 0
                else:
                    move = self.get_bot_move(prev_move, current_player)
                    valid_move = board.place_stone(move, current_player.color)
                    if move.x == -1 and move.y == -1:
                        print(f"{current_player.name} passes.")
                        valid_move = True
                        pass_flag += 1
                    else:
                        pass_flag = 0

            prev_move = move

            if current_player == player1:
                current_player = player2
            else:
                current_player = player1
            valid_move = False
        result = compute_game_result(board)
        print("Game over!")
        print(result)

def ai_predict(input_string):
    input_string = input_string.replace('W', ' ')
    input_string = input_string.replace('B', ' ')
    unique_chars = list(set(text))
    char_to_index = dict((ch, index) for index, ch 
                        in enumerate(unique_chars))
    index_to_char = dict((index, ch) for index, ch 
                        in enumerate(unique_chars))
    encoding_width = len(char_to_index)
    next_move = input_string
    one_hots = []
    for i, char in enumerate(next_move):
        x = np.zeros(encoding_width)
        x[char_to_index[char]] = 1
        one_hots.append(x)
    beams = [(np.log(1.0), next_move, one_hots)]
    for i in range(NEXT_COORDINATES):
        minibatch_list = []
        # Create minibatch from one-hot encodings, and predict.
        for triple in beams:
            minibatch_list.append(triple[2])
        minibatch = np.array(minibatch_list)
        y_predict = load_model.predict(minibatch, verbose=0)
        new_beams = []
        for j, softmax_vec in enumerate(y_predict):
            triple = beams[j]
            # Create BEAM_SIZE new beams from each existing beam.
            for k in range(BEAM_SIZE):
                char_index = np.argmax(softmax_vec)
                new_prob = triple[0] + np.log(
                    softmax_vec[char_index])
                new_letters = triple[1] + index_to_char[char_index]
                x = np.zeros(encoding_width)
                x[char_index] = 1
                new_one_hots = triple[2].copy()
                new_one_hots.append(x)
                new_beams.append((new_prob, new_letters,
                                new_one_hots))
                softmax_vec[char_index] = 0
        # Prune tree to only keep BEAM_SIZE most probable beams.
        new_beams.sort(key=lambda tup: tup[0], reverse=True)
        beams = new_beams[0:BEAM_SIZE]
    output = str(beams[1])
    return output

if __name__ == "__main__":
    player1 = Player(Player.black)
    player1.set_human_or_ai(True)
    player2 = Player(Player.white)
    player2.set_human_or_ai(False)
    test_game = Game()
    test_game.play_game(player1, player2, BOARDSIZE=5)