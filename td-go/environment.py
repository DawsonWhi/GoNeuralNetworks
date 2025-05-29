# go environment that stores the state of the game for the agent and gives out the reward

import agent
from agent import Agent
from collections import namedtuple
from typing import List, Optional, Set, Dict

BOARDSIZE = 19
Position = namedtuple("Position", ["x", "y"])


# class Environment(object, object):
#     def __init__(self, width=BOARDSIZE, height=BOARDSIZE):
#         self.width = width
#         self.height = height
#         self.board = [0.0 for _ in range(width * height)]

#     # Index 1d array as 2d coordinates
#     def getIndex(self, x, y) -> int:
#         return self.width * y + x



class Stone:
    def __init__(self, color: str, position: Position):
        self.color = color
        self.position = position
        self.group = None  # Will be set when added to a group

    def __str__(self):
        return self.color

class StoneGroup:
    def __init__(self, color: str):
        self.color = color
        self.stones = set()
        self.liberties = set()
    
    def add_stone(self, stone: Stone):
        #if stone.group:
         #   stone.group.remove_stone(stone)
        self.stones.add(stone)
        stone.group = self
    
    def remove_stone(self, stone: Stone):
        if stone in self.stones:
            self.stones.remove(stone)
            stone.group = None
    
    def merge(self, other_group):
        if self.color != other_group.color:
            raise ValueError("Cannot merge groups of different colors")
        for stone in other_group.stones:
            self.add_stone(stone)
        other_group.stones = set()
    
    def calculate_liberties(self, board: 'GoBoard'):
        """Calculate all liberties for this group"""
        self.liberties = set()
        for stone in self.stones:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Orthogonal neighbors
                pos = Position(stone.position.x + dx, stone.position.y + dy)
                if board.is_valid_position(pos) and board.get_stone(pos) is None:
                    self.liberties.add(pos)
    
    def has_liberties(self, board: 'GoBoard') -> bool:
        self.calculate_liberties(board)
        return len(self.liberties) > 0
    
    def __len__(self):
        return len(self.stones)

class GoBoard:
    def __init__(self, size: int = BOARDSIZE):
        self.winner = None
        self.size = size
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.groups = []
        self.previous_state = None  # For ko rule
    
    def place_stone(self, position: Position, color: str) -> bool:
        """Place a stone and handle all Go rules, including captures and ko"""
        if not self.is_valid_position(position) or self.get_stone(position) is not None:
            return False
        
        # Create new stone and temporary group
        new_stone = Stone(color, position)
        new_group = StoneGroup(color)
        new_group.add_stone(new_stone)
        self.board[position.x][position.y] = new_stone
        
        # Find adjacent groups
        adjacent_groups = self._get_adjacent_groups(position)
        
        # Merge with friendly groups
        for group in adjacent_groups:
            if group.color == color:
                new_group.merge(group)
                self.groups.remove(group)
        self.groups.append(new_group)
        
        # Check for captures in opponent groups
        captured_groups = []
        for group in self._get_adjacent_groups(position):
            if group.color != color and not group.has_liberties(self):
                captured_groups.append(group)
        
        # Check for ko
        if len(captured_groups) == 1 and len(captured_groups[0].stones) == 1:
            captured_pos = next(iter(captured_groups[0].stones)).position
            if self.previous_state and self.previous_state == (captured_pos, color):
                # Ko violation - undo the move
                self._remove_group(new_group)
                self.board[position.x][position.y] = None
                return False
        
        # Perform captures
        for group in captured_groups:
            self._remove_group(group)
        
        # Check if new move has liberties (suicide prevention)
        if not new_group.has_liberties(self) and not captured_groups:
            self._remove_group(new_group)
            self.board[position.x][position.y] = None
            return False
        
        # Update previous state for ko
        if len(captured_groups) == 1 and len(captured_groups[0].stones) == 1:
            self.previous_state = (position, color)
        else:
            self.previous_state = None
        
        return True
    
    def _get_adjacent_groups(self, position: Position) -> List[StoneGroup]:
        """Get all unique groups adjacent to a position"""
        groups = set()
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            x, y = position.x + dx, position.y + dy
            if self.is_valid_position(Position(x, y)):
                stone = self.get_stone(Position(x, y))
                if stone and stone.group and stone.group not in groups:
                    groups.add(stone.group)
        return list(groups)
    
    def _remove_group(self, group: StoneGroup):
        """Remove a group from the board"""
        for stone in group.stones:
            self.board[stone.position.x][stone.position.y] = None
        if group in self.groups:
            self.groups.remove(group)
    
    def is_valid_position(self, position: Position) -> bool:
        return 0 <= position.x < self.size and 0 <= position.y < self.size
    
    def get_stone(self, position: Position) -> Optional[Stone]:
        if not self.is_valid_position(position):
            return None
        return self.board[position.x][position.y]
    
    def display(self):
        """Print a simple ASCII representation of the board"""
        for y in range(self.size):
            row = []
            for x in range(self.size):
                stone = self.board[x][y]
                row.append(str(stone) if stone else '.')
            print(' '.join(row))
    
    def check_liberties(self, position: Position) -> int:
        """Legacy method - prefer using group-based liberty checking"""
        stone = self.get_stone(position)
        if not stone or not stone.group:
            return 0
        stone.group.calculate_liberties(self)
        return len(stone.group.liberties)



def get_neighbors(row, col, board):
    """Get the 4 neighbors (up, down, left, right)"""
    neighbors = []
    # check all directions
    if row > 0:
        neighbors.append((row-1, col))  # up
    if row < len(board)-1:
        neighbors.append((row+1, col))  # down
    if col > 0:
        neighbors.append((row, col-1))  # left
    if col < len(board[0])-1:
        neighbors.append((row, col+1))  # right
    return neighbors

def is_surrounded_by_color(row, col, color, board):
    """Check if an empty spot is completely surrounded by one color"""
    if board[row][col] != None:  # not empty
        return False
    
    print("test")

    # check direct neighbors
    for nr, nc in get_neighbors(row, col, board):
        if board[nr][nc] != color and board[nr][nc] != None:
            print("test 2")
            return False  # false if it found diff color
    return True

def count_territory(color, board):
    """Count empty spaces surrounded by your color"""
    territory = 0
    for row in range(len(board)):
        for col in range(len(board[0])):
            if board[row][col] == None:  # empty space
                print(row,col)
                if is_surrounded_by_color(row, col, color, board):
                    territory += 1
    return territory

def has_eyes(row, col, board):
    """Super simple eye check - does this stone have empty space next to it?"""
    # count empty neighbors, if >=2 it has an "eye"
    empty_count = 0
    for nr, nc in get_neighbors(row, col):
        if board[nr][nc] == 0:
            empty_count += 1
    return empty_count >= 2

def capture_stones_without_eyes(color, board):
    """Find opponent stones in your territory that don't have eyes"""
    opponent = 2 if color == 1 else 1  # opposite color
    captured = 0
    
    # checks each stone
    for row in range(len(board)):
        for col in range(len(board[0])):
            if board[row][col] == opponent:  # opponent stone
                # check for neighbors
                my_neighbors = 0
                total_neighbors = None
                for nr, nc in get_neighbors(row, col, board):
                    total_neighbors += 1
                    if board[nr][nc] == color:
                        my_neighbors += 1
                
                # if most neighbors are mine, piece has no eyes, capture
                if my_neighbors >= total_neighbors - 1 and not has_eyes(row, col):
                    board[row][col] = 0  # remove stone
                    captured += 1
    
    return captured

def calculate_score(p_board):
    """Calculate final scores"""

    board = p_board.board

    #print(board)

    # black score
    black_territory = count_territory('b', board)
    black_captures = capture_stones_without_eyes('b', board)
    black_total = black_territory + black_captures + captured_white
    
    # white score  
    white_territory = count_territory('w', board)
    white_captures = capture_stones_without_eyes('w', board)
    white_total = white_territory + white_captures + captured_black + 6.5  # komi bonus
    
    print(f"Black: {black_total} points")
    print(f"  - Territory: {black_territory}")
    print(f"  - Captured in territory: {black_captures}")
    print(f"  - Previously captured: {captured_white}")
    
    print(f"White: {white_total} points")
    print(f"  - Territory: {white_territory}")
    print(f"  - Captured in territory: {white_captures}")
    print(f"  - Previously captured: {captured_black}")
    print(f"  - Komi bonus: 6.5")
    

    if black_total > white_total:
        print(f"Black wins by {black_total - white_total} points!")
    elif white_total > black_total:
        print(f"White wins by {white_total - black_total} points!")
    else:
        print("It's a tie! (very rare)")
    
    return black_total, white_total



#TEST IT
board_obj = GoBoard(5)

# Example usage
if __name__ == "__main__":
    
    
    # Test basic placement
    board_obj.place_stone(Position(0, 0), 'b')
    board_obj.place_stone(Position(1, 0), 'b')
    board_obj.place_stone(Position(1, 1), 'b')
    board_obj.place_stone(Position(0, 2), 'b')
    board_obj.place_stone(Position(1, 3), 'b')
    board_obj.place_stone(Position(0, 4), 'b')
    print("After basic placement:")
    board_obj.display()
    
    # Test capture
    board_obj.place_stone(Position(2, 1), 'w')
    board_obj.place_stone(Position(4, 1), 'w')
    board_obj.place_stone(Position(1, 2), 'w')
    board_obj.place_stone(Position(2, 2), 'w')
    board_obj.place_stone(Position(3, 2), 'w')
    board_obj.place_stone(Position(2, 3), 'w')
    board_obj.place_stone(Position(1, 4), 'w')
    board_obj.place_stone(Position(2, 4), 'w')
    board_obj.place_stone(Position(3, 4), 'w')
    print("\nAfter capture:")
    board_obj.display()

# 0 = empty, 1 = black, 2 = white 

# track captured stones
captured_black = 0
captured_white = 0

# test
print("\nBoard:\n")
board_obj.display()

print("\nScoring...\n")
calculate_score(board_obj)