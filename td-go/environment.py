# go environment that stores the state of the game for the agent and gives out the reward

import agent
from agent import Agent
from collections import namedtuple
from typing import List, Optional, Set, Dict
from players import Player, Point
from scoring import compute_game_result

BOARDSIZE = 19
Position = namedtuple("Position", ["x", "y"])


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

    def calculate_liberties(self, board: "GoBoard"):
        """Calculate all liberties for this group"""
        self.liberties = set()
        for stone in self.stones:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Orthogonal neighbors
                pos = Position(stone.position.x + dx, stone.position.y + dy)
                if board.is_valid_position(pos) and board.get_stone(pos) is None:
                    self.liberties.add(pos)

    def has_liberties(self, board: "GoBoard") -> bool:
        self.calculate_liberties(board)
        return len(self.liberties) > 0

    def __len__(self):
        return len(self.stones)


class GoBoard:
    def __init__(self, size: int = BOARDSIZE):
        self.winner = None
        self.size = size
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.num_rows = size
        self.num_cols = size
        self.groups = []
        self.previous_state = None  # For ko rule
        self._grid = {}

    def get_color(self, point: Position) -> Optional[str]:
        if not (0 <= point.x < self.size and 0 <= point.y < self.size):
            return None
        stone = self.board[point.x][point.y]
        return stone.color if stone else None

    def _replace_group(self, new_group):
        for stone in new_group.stones:
            self._grid[stone.position] = new_group

    def _remove_group(self, group: StoneGroup):
        for stone in group.stones:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor_pos = Position(stone.position.x + dx, stone.position.y + dy)
                if self.is_valid_position(neighbor_pos):
                    neighbor_group = self._grid.get(neighbor_pos)
                    if neighbor_group and neighbor_group != group:
                        neighbor_group.liberties.add(stone.position)
            self._grid.pop(stone.position, None)

    def is_on_grid(self, point: Point) -> bool:
        return 1 <= point.row < self.size and 1 <= point.col < self.size

    def get(self, point: Point) -> Optional[Stone]:
        if not self.is_on_grid(point):
            return None
        stone = self.board[point.row-1][point.col-1]  # Convert to 0-based
        if stone is None:
            return None
        return Player.black if stone.color == 'b' else Player.white

    def place_stone(self, position: Position, color: str) -> bool:
        """Place a stone and handle all Go rules, including captures and ko"""
        if not self.is_valid_position(position) or self.get_stone(position) is not None:
            return False

        # Create new stone and temporary group
        new_stone = Stone(color, position)
        new_group = StoneGroup(color)
        new_group.add_stone(new_stone)
        self.board[position.x][position.y] = new_stone
        self._grid[position] = new_group

        adjacent_groups = self._get_adjacent_groups(position)

        # Merge with friendly groups
        for group in adjacent_groups:
            if group.color == color:
                new_group.merge(group)
                self.groups.remove(group)
                self._replace_group(new_group)
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
                self._grid.pop(position, None)
                return False

        # Perform captures
        for group in captured_groups:
            self._remove_group(group)

        # Check if new move has liberties (suicide prevention)
        if not new_group.has_liberties(self) and not captured_groups:
            self._remove_group(new_group)
            self.board[position.x][position.y] = None
            self._grid.pop(position, None)
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
            self._grid.pop(stone.position, None)
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
                row.append(str(stone) if stone else ".")
            print(" ".join(row))



def get_neighbors(row, col, board):
    """Get the 4 neighbors (up, down, left, right)"""
    neighbors = []
    # check all directions
    if row > 0:
        neighbors.append((row - 1, col))  # up
    if row < len(board) - 1:
        neighbors.append((row + 1, col))  # down
    if col > 0:
        neighbors.append((row, col - 1))  # left
    if col < len(board[0]) - 1:
        neighbors.append((row, col + 1))  # right
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


# TEST IT
board_obj = GoBoard(5)

# Example usage
if __name__ == "__main__":
    # Test basic placement
    board_obj.place_stone(Position(0, 0), "b")
    board_obj.place_stone(Position(1, 0), "b")
    board_obj.place_stone(Position(1, 1), "b")
    board_obj.place_stone(Position(0, 2), "b")
    board_obj.place_stone(Position(1, 3), "b")
    board_obj.place_stone(Position(0, 4), "b")
    print("After basic placement:")
    board_obj.display()

    # Test capture
    board_obj.place_stone(Position(2, 1), "w")
    board_obj.place_stone(Position(4, 1), "w")
    board_obj.place_stone(Position(1, 2), "w")
    board_obj.place_stone(Position(2, 2), "w")
    board_obj.place_stone(Position(3, 2), "w")
    board_obj.place_stone(Position(2, 3), "w")
    board_obj.place_stone(Position(1, 4), "w")
    board_obj.place_stone(Position(2, 4), "w")
    board_obj.place_stone(Position(3, 4), "w")
    board_obj.place_stone(Position(3, 1), "b")
    board_obj.place_stone(Position(3, 0), "w")
    board_obj.place_stone(Position(2, 0), "w")
    board_obj.place_stone(Position(0, 1), "w")
    print("\nAfter capture:")
    board_obj.display()

    gameResult = compute_game_result(board_obj)
    print(gameResult)
