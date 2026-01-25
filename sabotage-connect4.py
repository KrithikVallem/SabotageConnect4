from os import system
from dataclasses import dataclass
from typing import Optional

# https://stackoverflow.com/a/287944
class COLOR:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    ENDC = '\033[0m'

def getColored(text: str, color: COLOR) -> str:
    return color + text + COLOR.ENDC

def clear_screen():
    system("clear||cls")

class PIECE:
    NORMAL = '●'
    SABOTAGE = '◎'
    EMPTY = '○'

class Player:
    number: int
    name: str
    team_color: COLOR
    piece: str
    piece_color: COLOR
    is_sabotage: bool

    def __init__(self, number: int, name: str, team_color: COLOR, is_sabotage: bool = False, is_empty: bool = False):
        self.number = number
        self.name = name
        self.team_color = team_color
        self.is_sabotage = is_sabotage
    
        self.piece_color = self.get_enemy_color(team_color) if is_sabotage else team_color
        self.piece = PIECE.EMPTY if is_empty else PIECE.SABOTAGE if is_sabotage else PIECE.NORMAL

    def get_enemy_color(self, team_color: COLOR) -> COLOR:
        if team_color == COLOR.RED:
            return COLOR.YELLOW
        elif team_color == COLOR.YELLOW:
            return COLOR.RED
        else:
            raise ValueError("Invalid team color")

    def get_team_name(self, team_color: COLOR) -> str:
        if team_color == COLOR.RED:
            return "Red"
        elif team_color == COLOR.YELLOW:
            return "Yellow"
        else:
            raise ValueError("Invalid team color")

    def get_descriptive_name(self) -> str:
        return (getColored(self.name, self.team_color) 
                + getColored(f', has {self.get_team_name(self.piece_color)} {self.piece} Pieces', self.piece_color))

class SabotageConnect4:
    ROWS: int = 6
    COLUMNS: int = 7
    WINNING_LENGTH: int = 4

    EMPTY_SPACE = Player(-1, "Empty Space", team_color=COLOR.BLUE, is_empty=True)
    # Players is in order of moves, so that modulus can be used to determine current player
    # Keep player number equal to its index in the list
    PLAYERS = [
        Player(0, "Red Team Normal", team_color=COLOR.RED),
        Player(1, "Yellow Team Spy", team_color=COLOR.YELLOW, is_sabotage=True),
        Player(2, "Yellow Team Normal", team_color=COLOR.YELLOW),
        Player(3, "Red Team Spy", team_color=COLOR.RED, is_sabotage=True),
    ]

    # Valid Inputs
    UNDO_INPUT: str = 'UNDO'
    QUIT_INPUT: str = 'QUIT'
    COLUMN_INPUTS: set[str] = set(str(i) for i in range(COLUMNS))

    board: list[list[Player]] = []
    moves: list[tuple[int, int]] = []
    error_message: str = ''

    def __init__(self):
        self.board = [
            [self.EMPTY_SPACE for _ in range(self.COLUMNS)] 
            for _ in range(self.ROWS)
        ]
        self.run_game()

    def run_game(self):        
        while True:
            # Clear screen & display board
            clear_screen()
            self.display_board()
            print()

            # Check for winner
            winning_player = self.get_winning_player()
            if winning_player is not None:
                # Empty space returns means a tie, as board is full with no winner
                if winning_player.number == self.EMPTY_SPACE.number:
                    print(getColored("It's a Tie!", COLOR.GREEN))
                    break

                # use piece color to determine winning team
                winning_team_name = winning_player.get_team_name(winning_player.piece_color)
                print(getColored(f'{winning_team_name} Team Wins!', winning_player.piece_color))
                break

            # Display error message if there is one
            if self.error_message != '':
                print(getColored(self.error_message, COLOR.MAGENTA))
                self.error_message = ''

            current_player = self.get_current_player()
            print("Current player is " + current_player.get_descriptive_name())
            
            user_input = input("Enter column number, UNDO, or QUIT: ")
            user_input = user_input.strip().upper()
            
            if user_input == self.QUIT_INPUT:
                print(getColored("Thanks for playing Sabotage Connect 4!", COLOR.BLUE))
                break
            elif user_input == self.UNDO_INPUT:
                self.undo_move()
                continue
            elif user_input not in self.COLUMN_INPUTS:
                self.error_message = f'Column must be between 0 and {self.COLUMNS - 1}!'
                continue
            else:
                self.make_move(user_input)
                continue
        

    def display_board(self):
        for row in self.board:
            for player in row:
                # empty space
                if player.number == self.EMPTY_SPACE.number:
                    print(getColored(self.EMPTY_SPACE.piece, self.EMPTY_SPACE.piece_color), end=' ')
                    continue

                print(getColored(player.piece, player.piece_color), end=' ')

            
            # newline after each row
            print()

        # Column names at the bottom
        for col_num in range(self.COLUMNS):
            print(getColored(str(col_num), COLOR.GREEN), end=' ')
        print()
    
    def undo_move(self):
        if len(self.moves) == 0:
            self.error_message = 'No moves to undo!'
            return

        row, col = self.moves.pop()
        self.board[row][col] = self.EMPTY_SPACE

    def make_move(self, column):
        column = int(column)

        # iterate from bottom to top of column to find first empty space
        for row in reversed(range(self.ROWS)):
            if self.board[row][column].number == self.EMPTY_SPACE.number:
                current_player = self.get_current_player()
                self.board[row][column] = current_player
                self.moves.append((row, column))
                return
        
        # Column is full, force user to make another choice by returning False
        self.error_message = 'That column is full!'

    # Get current player based on number of moves made
    def get_current_player(self) -> Player:
        current_player_num = len(self.moves) % len(self.PLAYERS)
        return self.PLAYERS[current_player_num]
    
    # Check entire board for a winner (self.WINNING_LENGTH pieces in a row/col/diagonal, usually 4)
    def get_winning_player(self) -> Optional[Player]:
        board_filled = True

        for row in range(self.ROWS):
            for col in range(self.COLUMNS):
                starting_player = self.board[row][col]

                # Skip empty spaces
                if starting_player.number == self.EMPTY_SPACE.number:
                    board_filled = False
                    continue

                # need to check piece color for this logic
                # not team color, because sabotage pieces count as enemy pieces

                # Check right
                if col + self.WINNING_LENGTH <= self.COLUMNS:
                    if all(self.board[row][col + offset].piece_color == starting_player.piece_color 
                           for offset in range(self.WINNING_LENGTH)):
                        return starting_player

                # Check down
                if row + self.WINNING_LENGTH <= self.ROWS:
                    if all(self.board[row + offset][col].piece_color == starting_player.piece_color 
                           for offset in range(self.WINNING_LENGTH)):
                        return starting_player

                # Check diagonal down-right
                if row + self.WINNING_LENGTH <= self.ROWS and col + self.WINNING_LENGTH <= self.COLUMNS:
                    if all(self.board[row + offset][col + offset].piece_color == starting_player.piece_color 
                           for offset in range(self.WINNING_LENGTH)):
                        return starting_player

                # Check diagonal down-left
                if row + self.WINNING_LENGTH <= self.ROWS and col - self.WINNING_LENGTH >= -1:
                    if all(self.board[row + offset][col - offset].piece_color == starting_player.piece_color 
                           for offset in range(self.WINNING_LENGTH)):
                        return starting_player
                    
        # Indicate a tie with the empty space player
        if board_filled:
            return self.EMPTY_SPACE
        
        return None

if __name__ == "__main__":
    SabotageConnect4()
