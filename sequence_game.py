"""
Sequence Game Engine
A complete implementation of the Sequence board game.
"""

import random
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
from copy import deepcopy

# Card suits and ranks
SUITS = ['S', 'H', 'D', 'C']  # Spades, Hearts, Diamonds, Clubs
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Q', 'K']  # No Jacks on board
JACK_RANKS = ['J']

# Special Jack types
# Two-eyed Jacks (Diamonds, Clubs) - Wild, place anywhere
# One-eyed Jacks (Spades, Hearts) - Remove opponent's chip
TWO_EYED_JACKS = ['JD', 'JC']
ONE_EYED_JACKS = ['JS', 'JH']

# Standard Sequence board layout (10x10)
# 'XX' represents corner wild spaces
# Each non-Jack card appears exactly twice on the board
BOARD_LAYOUT = [
    ['XX', '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', 'XX'],
    ['6C', '5C', '4C', '3C', '2C', 'AH', 'KH', 'QH', '10H', '10S'],
    ['7C', 'AS', '2D', '3D', '4D', '5D', '6D', '7D', '9H', 'QS'],
    ['8C', 'KS', '6C', '5C', '4C', '3C', '2C', '8D', '8H', 'KS'],
    ['9C', 'QS', '7C', '6H', '5H', '4H', 'AH', '9D', '7H', 'AS'],
    ['10C', '10S', '8C', '7H', '2H', '3H', 'KH', '10D', '6H', '2D'],
    ['QC', '9S', '9C', '8H', '9H', '10H', 'QH', 'QD', '5H', '3D'],
    ['KC', '8S', '10C', 'QC', 'KC', 'AC', 'AD', 'KD', '4H', '4D'],
    ['AC', '7S', '6S', '5S', '4S', '3S', '2S', 'AS', '3H', '5D'],
    ['XX', 'AD', 'KD', 'QD', '10D', '9D', '8D', '7D', '6D', 'XX'],
]


class ChipColor(Enum):
    EMPTY = 0
    BLUE = 1
    GREEN = 2
    WILD = 3  # Corner spaces


@dataclass
class Card:
    rank: str
    suit: str

    def __str__(self):
        return f"{self.rank}{self.suit}"

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.rank == other.rank and self.suit == other.suit
        return False

    def is_two_eyed_jack(self) -> bool:
        return str(self) in TWO_EYED_JACKS

    def is_one_eyed_jack(self) -> bool:
        return str(self) in ONE_EYED_JACKS

    def is_jack(self) -> bool:
        return self.rank == 'J'


@dataclass
class Move:
    card: Card
    row: int
    col: int
    is_removal: bool = False  # True if using one-eyed jack to remove

    def __str__(self):
        action = "remove" if self.is_removal else "place"
        return f"{action} {self.card} at ({self.row}, {self.col})"


@dataclass
class GameState:
    board: list  # 10x10 grid of ChipColor
    player_hands: dict  # player_id -> list of Cards
    deck: list  # remaining cards in deck
    discard_pile: list  # discarded cards
    current_player: int
    sequences: dict  # player_id -> list of sequence coordinates
    chips_on_board: dict  # player_id -> set of (row, col) positions
    winner: Optional[int] = None
    turn_number: int = 0

    def copy(self):
        return deepcopy(self)


class SequenceGame:
    """Main game engine for Sequence."""

    def __init__(self, num_players: int = 2):
        self.num_players = num_players
        self.board_layout = BOARD_LAYOUT
        self.state = None
        self.move_history = []
        self.sequences_to_win = 2 if num_players == 2 else 1

    def initialize_game(self) -> GameState:
        """Set up a new game."""
        # Initialize board (all empty except corners which are wild)
        board = [[ChipColor.EMPTY for _ in range(10)] for _ in range(10)]
        for row, col in [(0, 0), (0, 9), (9, 0), (9, 9)]:
            board[row][col] = ChipColor.WILD

        # Create deck (2 standard decks, 104 cards total including Jacks)
        deck = []
        for _ in range(2):  # Two decks
            for suit in SUITS:
                for rank in RANKS:
                    deck.append(Card(rank, suit))
                # Add Jacks
                deck.append(Card('J', suit))

        random.shuffle(deck)

        # Determine cards per player
        cards_per_player = {2: 7, 3: 6, 4: 6, 6: 5, 8: 4, 9: 4, 10: 3, 12: 3}
        hand_size = cards_per_player.get(self.num_players, 7)

        # Deal cards
        player_hands = {}
        for player in range(self.num_players):
            player_hands[player] = [deck.pop() for _ in range(hand_size)]

        self.state = GameState(
            board=board,
            player_hands=player_hands,
            deck=deck,
            discard_pile=[],
            current_player=0,
            sequences={i: [] for i in range(self.num_players)},
            chips_on_board={i: set() for i in range(self.num_players)},
            winner=None,
            turn_number=0
        )
        self.move_history = []

        return self.state

    def get_chip_color(self, player_id: int) -> ChipColor:
        """Get the chip color for a player."""
        return ChipColor.BLUE if player_id == 0 else ChipColor.GREEN

    def get_board_card(self, row: int, col: int) -> str:
        """Get the card at a board position."""
        return self.board_layout[row][col]

    def find_card_positions(self, card: Card) -> list:
        """Find all board positions matching a card."""
        positions = []
        card_str = str(card)
        for row in range(10):
            for col in range(10):
                if self.board_layout[row][col] == card_str:
                    positions.append((row, col))
        return positions

    def is_position_available(self, row: int, col: int) -> bool:
        """Check if a position is available for placing a chip."""
        if self.board_layout[row][col] == 'XX':  # Corner - always available conceptually but already wild
            return False
        return self.state.board[row][col] == ChipColor.EMPTY

    def is_dead_card(self, card: Card) -> bool:
        """Check if a card is dead (both positions occupied)."""
        if card.is_jack():
            return False  # Jacks are never dead
        positions = self.find_card_positions(card)
        return all(self.state.board[r][c] != ChipColor.EMPTY for r, c in positions)

    def get_valid_moves(self, player_id: int) -> list:
        """Get all valid moves for a player."""
        moves = []
        hand = self.state.player_hands[player_id]
        player_color = self.get_chip_color(player_id)

        for card in hand:
            if card.is_two_eyed_jack():
                # Can place on any empty non-corner space
                for row in range(10):
                    for col in range(10):
                        if self.is_position_available(row, col):
                            moves.append(Move(card, row, col))

            elif card.is_one_eyed_jack():
                # Can remove any opponent's chip (not part of a sequence)
                for opp_id in range(self.num_players):
                    if opp_id == player_id:
                        continue
                    for row, col in self.state.chips_on_board[opp_id]:
                        if not self._is_chip_in_completed_sequence(row, col, opp_id):
                            moves.append(Move(card, row, col, is_removal=True))

            else:
                # Regular card - find matching positions
                if self.is_dead_card(card):
                    continue
                for row, col in self.find_card_positions(card):
                    if self.is_position_available(row, col):
                        moves.append(Move(card, row, col))

        return moves

    def _is_chip_in_completed_sequence(self, row: int, col: int, player_id: int) -> bool:
        """Check if a chip is part of a completed sequence."""
        for sequence in self.state.sequences[player_id]:
            if (row, col) in sequence:
                return True
        return False

    def make_move(self, move: Move) -> bool:
        """Execute a move and return True if successful."""
        player_id = self.state.current_player
        player_color = self.get_chip_color(player_id)

        # Validate move
        if move.card not in self.state.player_hands[player_id]:
            return False

        # Execute move
        if move.is_removal:
            # One-eyed jack - remove opponent's chip
            opponent_id = None
            for opp in range(self.num_players):
                if opp != player_id and (move.row, move.col) in self.state.chips_on_board[opp]:
                    opponent_id = opp
                    break

            if opponent_id is None:
                return False

            self.state.board[move.row][move.col] = ChipColor.EMPTY
            self.state.chips_on_board[opponent_id].remove((move.row, move.col))
        else:
            # Place chip
            self.state.board[move.row][move.col] = player_color
            self.state.chips_on_board[player_id].add((move.row, move.col))

        # Remove card from hand and add to discard
        self.state.player_hands[player_id].remove(move.card)
        self.state.discard_pile.append(move.card)

        # Draw new card if deck not empty
        if self.state.deck:
            self.state.player_hands[player_id].append(self.state.deck.pop())

        # Record move
        self.move_history.append({
            'player': player_id,
            'move': move,
            'turn': self.state.turn_number
        })

        # Check for new sequences
        if not move.is_removal:
            self._check_for_sequences(player_id)

        # Check for winner
        if len(self.state.sequences[player_id]) >= self.sequences_to_win:
            self.state.winner = player_id

        # Next turn
        self.state.turn_number += 1
        self.state.current_player = (self.state.current_player + 1) % self.num_players

        return True

    def _check_for_sequences(self, player_id: int):
        """Check if player has formed any new sequences."""
        player_color = self.get_chip_color(player_id)
        chips = self.state.chips_on_board[player_id]

        # Directions: horizontal, vertical, diagonal-down-right, diagonal-down-left
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        new_sequences = []

        for row in range(10):
            for col in range(10):
                for dr, dc in directions:
                    sequence = self._check_sequence_from(row, col, dr, dc, player_color, player_id)
                    if sequence and not self._is_sequence_already_counted(sequence, player_id):
                        new_sequences.append(sequence)

        # Only add sequences that don't overlap too much with existing ones
        for seq in new_sequences:
            if self._can_add_sequence(seq, player_id):
                self.state.sequences[player_id].append(seq)

    def _check_sequence_from(self, start_row: int, start_col: int,
                             dr: int, dc: int, player_color: ChipColor,
                             player_id: int) -> Optional[list]:
        """Check for a sequence of 5 starting from a position in a direction."""
        sequence = []

        for i in range(5):
            row = start_row + i * dr
            col = start_col + i * dc

            if not (0 <= row < 10 and 0 <= col < 10):
                return None

            cell = self.state.board[row][col]
            if cell == player_color or cell == ChipColor.WILD:
                sequence.append((row, col))
            else:
                return None

        return sequence

    def _is_sequence_already_counted(self, sequence: list, player_id: int) -> bool:
        """Check if this exact sequence is already counted."""
        seq_set = set(sequence)
        for existing in self.state.sequences[player_id]:
            if set(existing) == seq_set:
                return True
        return False

    def _can_add_sequence(self, new_seq: list, player_id: int) -> bool:
        """Check if a sequence can be added (allows one chip overlap with existing)."""
        new_set = set(new_seq)
        for existing in self.state.sequences[player_id]:
            overlap = len(new_set & set(existing))
            # Allow max 1 chip overlap for two sequences (9 chips total for 2 sequences)
            if overlap > 1:
                return False
        return True

    def is_game_over(self) -> bool:
        """Check if the game is over."""
        if self.state.winner is not None:
            return True

        # Check if any player can make a move
        for player in range(self.num_players):
            if self.get_valid_moves(player):
                return False

        return True  # No valid moves for anyone

    def get_winner(self) -> Optional[int]:
        """Get the winning player, or None if no winner yet."""
        return self.state.winner

    def get_board_display(self) -> str:
        """Get a string representation of the current board."""
        symbols = {
            ChipColor.EMPTY: '.',
            ChipColor.BLUE: 'B',
            ChipColor.GREEN: 'G',
            ChipColor.WILD: '*'
        }

        lines = []
        lines.append("  " + " ".join(f"{i}" for i in range(10)))
        for row in range(10):
            line = f"{row} "
            for col in range(10):
                line += symbols[self.state.board[row][col]] + " "
            lines.append(line)

        return "\n".join(lines)


def create_full_deck() -> list:
    """Create a full deck with all cards including Jacks."""
    deck = []
    for suit in SUITS:
        for rank in RANKS:
            deck.append(Card(rank, suit))
        deck.append(Card('J', suit))
    return deck
