from environment import *
from players import Player
from scoring import compute_game_result
from collections import namedtuple

class Game:
        
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

    def play_game(self, player1, player2, BOARDSIZE=19):
        board = GoBoard(BOARDSIZE)
        current_player = player1
        game_over = False
        valid_move = False
        pass_flag = 0

        while not game_over | (pass_flag == 2):  # Game continues until two consecutive passes

            while(not valid_move): # valid_move is True when a valid move is made
                board.display()
                print(f"{current_player.name}'s turn ({current_player.color})")
                move = self.get_formatted_move(BOARDSIZE)
                valid_move = board.place_stone(move, current_player.color)
                if move.x == -1 and move.y == -1:
                    print(f"{current_player.name} passes.")
                    valid_move = True
                    pass_flag += 1
                else:
                    pass_flag = 0

            if current_player == player1:
                current_player = player2
            else:
                current_player = player1
            valid_move = False
        result = compute_game_result(board)
        print("Game over!")
        print(result)

if __name__ == "__main__":
    player1 = Player(Player.black)
    player2 = Player(Player.white)
    test_game = Game()
    test_game.play_game(player1, player2, BOARDSIZE=5)