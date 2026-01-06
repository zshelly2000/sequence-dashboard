"""
Sequence AI Bot
An optimal-play bot for the Sequence board game.
"""

import random
from dataclasses import dataclass
from typing import Optional
from sequence_game import (
    SequenceGame, GameState, Move, Card, ChipColor,
    TWO_EYED_JACKS, ONE_EYED_JACKS
)


@dataclass
class MoveEvaluation:
    move: Move
    score: float
    offensive_score: float
    defensive_score: float
    sequence_potential: int
    blocks_opponent: bool
    creates_sequence: bool
    reasoning: str


class SequenceBot:
    """
    An AI bot that plays Sequence optimally.

    Strategy priorities:
    1. Complete a winning sequence if possible
    2. Block opponent's winning sequences
    3. Extend existing partial sequences
    4. Create new sequence opportunities
    5. Strategic use of Jacks
    6. Maximize flexibility (cards that fit multiple sequences)
    """

    def __init__(self, player_id: int, strategy: str = "balanced"):
        self.player_id = player_id
        self.strategy = strategy  # "balanced", "aggressive", "defensive"

        # Strategy weights
        self.weights = self._get_strategy_weights()

    def _get_strategy_weights(self) -> dict:
        """Get scoring weights based on strategy."""
        if self.strategy == "aggressive":
            return {
                'win_sequence': 10000,
                'extend_4': 500,
                'extend_3': 100,
                'extend_2': 30,
                'new_potential': 15,
                'corner_use': 25,
                'block_win': 5000,
                'block_4': 300,
                'block_3': 60,
                'block_2': 15,
                'jack_save': 10,
                'center_bonus': 5,
                'flexibility': 8,
            }
        elif self.strategy == "defensive":
            return {
                'win_sequence': 10000,
                'extend_4': 400,
                'extend_3': 80,
                'extend_2': 25,
                'new_potential': 10,
                'corner_use': 20,
                'block_win': 8000,
                'block_4': 500,
                'block_3': 100,
                'block_2': 30,
                'jack_save': 15,
                'center_bonus': 3,
                'flexibility': 5,
            }
        else:  # balanced
            return {
                'win_sequence': 10000,
                'extend_4': 450,
                'extend_3': 90,
                'extend_2': 28,
                'new_potential': 12,
                'corner_use': 22,
                'block_win': 6000,
                'block_4': 400,
                'block_3': 80,
                'block_2': 20,
                'jack_save': 12,
                'center_bonus': 4,
                'flexibility': 7,
            }

    def get_move(self, game: SequenceGame) -> Optional[Move]:
        """Get the best move for the current game state."""
        valid_moves = game.get_valid_moves(self.player_id)

        if not valid_moves:
            return None

        evaluations = [self._evaluate_move(game, move) for move in valid_moves]

        # Sort by score, highest first
        evaluations.sort(key=lambda e: e.score, reverse=True)

        # Add small random factor to break ties
        top_score = evaluations[0].score
        top_moves = [e for e in evaluations if e.score >= top_score - 0.5]

        return random.choice(top_moves).move

    def get_move_with_analysis(self, game: SequenceGame) -> Optional[MoveEvaluation]:
        """Get the best move with full analysis."""
        valid_moves = game.get_valid_moves(self.player_id)

        if not valid_moves:
            return None

        evaluations = [self._evaluate_move(game, move) for move in valid_moves]
        evaluations.sort(key=lambda e: e.score, reverse=True)

        return evaluations[0]

    def _evaluate_move(self, game: SequenceGame, move: Move) -> MoveEvaluation:
        """Evaluate a move and return its score."""
        offensive_score = 0.0
        defensive_score = 0.0
        reasoning_parts = []
        creates_sequence = False
        blocks_opponent = False
        sequence_potential = 0

        if move.is_removal:
            # Evaluate one-eyed jack (removal) move
            defensive_score, blocks_opponent, reasoning = self._evaluate_removal(game, move)
            reasoning_parts.append(reasoning)
        else:
            # Evaluate placement move
            offensive_score, creates_sequence, seq_pot, off_reasoning = self._evaluate_placement_offensive(game, move)
            sequence_potential = seq_pot
            reasoning_parts.append(off_reasoning)

            defensive_score, blocks_opponent, def_reasoning = self._evaluate_placement_defensive(game, move)
            reasoning_parts.append(def_reasoning)

        # Jack card consideration
        jack_penalty = 0
        if move.card.is_jack():
            # Penalize using jacks early (they're valuable)
            remaining_cards = len(game.state.deck)
            if remaining_cards > 50:
                jack_penalty = self.weights['jack_save']
                reasoning_parts.append(f"Jack save penalty: -{jack_penalty}")

        # Calculate total score
        total_score = offensive_score + defensive_score - jack_penalty

        return MoveEvaluation(
            move=move,
            score=total_score,
            offensive_score=offensive_score,
            defensive_score=defensive_score,
            sequence_potential=sequence_potential,
            blocks_opponent=blocks_opponent,
            creates_sequence=creates_sequence,
            reasoning=" | ".join(reasoning_parts)
        )

    def _evaluate_placement_offensive(self, game: SequenceGame, move: Move) -> tuple:
        """Evaluate offensive value of a placement move."""
        score = 0.0
        reasoning_parts = []
        creates_sequence = False
        sequence_potential = 0

        row, col = move.row, move.col
        player_color = game.get_chip_color(self.player_id)

        # Check all directions for sequence building
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for dr, dc in directions:
            line_info = self._analyze_line(game, row, col, dr, dc, player_color)

            if line_info['can_complete_sequence']:
                score += self.weights['win_sequence']
                creates_sequence = True
                reasoning_parts.append("Wins game!")

            if line_info['extends_4']:
                score += self.weights['extend_4']
                creates_sequence = True
                reasoning_parts.append(f"Extends 4 to sequence ({dr},{dc})")
            elif line_info['extends_3']:
                score += self.weights['extend_3']
                sequence_potential += 3
                reasoning_parts.append(f"Extends 3 ({dr},{dc})")
            elif line_info['extends_2']:
                score += self.weights['extend_2']
                sequence_potential += 2
                reasoning_parts.append(f"Extends 2 ({dr},{dc})")
            elif line_info['new_potential']:
                score += self.weights['new_potential']
                sequence_potential += 1

        # Corner adjacency bonus
        corner_adjacent = self._is_corner_adjacent(row, col)
        if corner_adjacent:
            score += self.weights['corner_use']
            reasoning_parts.append("Near corner")

        # Center control bonus
        center_dist = abs(row - 4.5) + abs(col - 4.5)
        if center_dist < 3:
            score += self.weights['center_bonus'] * (3 - center_dist)
            reasoning_parts.append(f"Center control: +{self.weights['center_bonus'] * (3 - center_dist):.1f}")

        # Flexibility bonus - position that helps multiple potential sequences
        if sequence_potential >= 3:
            score += self.weights['flexibility'] * sequence_potential
            reasoning_parts.append(f"High flexibility: {sequence_potential}")

        return score, creates_sequence, sequence_potential, " | ".join(reasoning_parts) if reasoning_parts else "Basic move"

    def _evaluate_placement_defensive(self, game: SequenceGame, move: Move) -> tuple:
        """Evaluate defensive value of a placement move."""
        score = 0.0
        reasoning_parts = []
        blocks_opponent = False

        row, col = move.row, move.col

        # Check if this blocks opponent
        for opp_id in range(game.num_players):
            if opp_id == self.player_id:
                continue

            opp_color = game.get_chip_color(opp_id)
            directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

            for dr, dc in directions:
                line_info = self._analyze_line(game, row, col, dr, dc, opp_color)

                if line_info['blocks_win']:
                    score += self.weights['block_win']
                    blocks_opponent = True
                    reasoning_parts.append("Blocks opponent win!")
                elif line_info['blocks_4']:
                    score += self.weights['block_4']
                    blocks_opponent = True
                    reasoning_parts.append(f"Blocks 4-chain ({dr},{dc})")
                elif line_info['blocks_3']:
                    score += self.weights['block_3']
                    blocks_opponent = True
                    reasoning_parts.append(f"Blocks 3-chain ({dr},{dc})")
                elif line_info['blocks_2']:
                    score += self.weights['block_2']
                    blocks_opponent = True

        return score, blocks_opponent, " | ".join(reasoning_parts) if reasoning_parts else ""

    def _evaluate_removal(self, game: SequenceGame, move: Move) -> tuple:
        """Evaluate a removal (one-eyed jack) move."""
        score = 0.0
        reasoning_parts = []
        blocks_opponent = True

        row, col = move.row, move.col

        # Find which opponent owns this chip
        for opp_id in range(game.num_players):
            if opp_id == self.player_id:
                continue
            if (row, col) in game.state.chips_on_board[opp_id]:
                opp_color = game.get_chip_color(opp_id)

                # Check how important this chip is to opponent
                directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

                for dr, dc in directions:
                    line_info = self._analyze_line_for_removal(game, row, col, dr, dc, opp_color)

                    if line_info['breaks_4']:
                        score += self.weights['block_win']
                        reasoning_parts.append("Breaks 4-chain!")
                    elif line_info['breaks_3']:
                        score += self.weights['block_4']
                        reasoning_parts.append(f"Breaks 3-chain ({dr},{dc})")
                    elif line_info['breaks_2']:
                        score += self.weights['block_3']
                        reasoning_parts.append(f"Breaks 2-chain ({dr},{dc})")

                break

        return score, blocks_opponent, " | ".join(reasoning_parts) if reasoning_parts else "Basic removal"

    def _analyze_line(self, game: SequenceGame, row: int, col: int,
                      dr: int, dc: int, player_color: ChipColor) -> dict:
        """Analyze a line through a position for sequence potential."""
        result = {
            'can_complete_sequence': False,
            'extends_4': False,
            'extends_3': False,
            'extends_2': False,
            'new_potential': False,
            'blocks_win': False,
            'blocks_4': False,
            'blocks_3': False,
            'blocks_2': False,
        }

        # Look at the 5-cell window that includes this position
        # Position can be at any of the 5 spots in a potential sequence
        for offset in range(-4, 1):
            sequence_cells = []
            valid = True

            for i in range(5):
                r = row + (offset + i) * dr
                c = col + (offset + i) * dc

                if not (0 <= r < 10 and 0 <= c < 10):
                    valid = False
                    break

                sequence_cells.append((r, c))

            if not valid:
                continue

            # Count our chips, opponent chips, empty, wild in this window
            our_count = 0
            opp_count = 0
            empty_count = 0
            wild_count = 0
            target_is_empty = False

            for r, c in sequence_cells:
                cell = game.state.board[r][c]
                if (r, c) == (row, col):
                    target_is_empty = True  # This is where we're placing
                    continue

                if cell == player_color:
                    our_count += 1
                elif cell == ChipColor.WILD:
                    wild_count += 1
                elif cell == ChipColor.EMPTY:
                    empty_count += 1
                else:
                    opp_count += 1

            # This line can form a sequence if no opponent chips
            if opp_count == 0 and target_is_empty:
                total_friendly = our_count + wild_count

                if total_friendly == 4:
                    result['can_complete_sequence'] = True
                    result['extends_4'] = True
                elif total_friendly == 3:
                    result['extends_3'] = True
                elif total_friendly == 2:
                    result['extends_2'] = True
                elif total_friendly >= 1:
                    result['new_potential'] = True

            # Check if this blocks opponent
            if our_count == 0 and target_is_empty:
                opp_total = opp_count + wild_count
                if opp_total == 4 and empty_count == 0:
                    result['blocks_win'] = True
                    result['blocks_4'] = True
                elif opp_total == 3:
                    result['blocks_3'] = True
                elif opp_total == 2:
                    result['blocks_2'] = True

        return result

    def _analyze_line_for_removal(self, game: SequenceGame, row: int, col: int,
                                  dr: int, dc: int, opp_color: ChipColor) -> dict:
        """Analyze impact of removing a chip from a line."""
        result = {
            'breaks_4': False,
            'breaks_3': False,
            'breaks_2': False,
        }

        # Check if this chip is part of opponent's building sequence
        for offset in range(-4, 1):
            sequence_cells = []
            valid = True

            for i in range(5):
                r = row + (offset + i) * dr
                c = col + (offset + i) * dc

                if not (0 <= r < 10 and 0 <= c < 10):
                    valid = False
                    break

                sequence_cells.append((r, c))

            if not valid:
                continue

            # Count opponent's presence in this window
            opp_count = 0
            includes_target = False

            for r, c in sequence_cells:
                if (r, c) == (row, col):
                    includes_target = True
                    opp_count += 1  # Count the target
                    continue

                cell = game.state.board[r][c]
                if cell == opp_color or cell == ChipColor.WILD:
                    opp_count += 1

            if includes_target:
                if opp_count >= 4:
                    result['breaks_4'] = True
                elif opp_count >= 3:
                    result['breaks_3'] = True
                elif opp_count >= 2:
                    result['breaks_2'] = True

        return result

    def _is_corner_adjacent(self, row: int, col: int) -> bool:
        """Check if position is adjacent to a corner."""
        corners = [(0, 0), (0, 9), (9, 0), (9, 9)]
        for cr, cc in corners:
            if abs(row - cr) <= 1 and abs(col - cc) <= 1:
                if (row, col) != (cr, cc):  # Not the corner itself
                    return True
        return False

    def get_hand_analysis(self, game: SequenceGame) -> dict:
        """Analyze the current hand for strategic insights."""
        hand = game.state.player_hands[self.player_id]

        analysis = {
            'total_cards': len(hand),
            'two_eyed_jacks': sum(1 for c in hand if c.is_two_eyed_jack()),
            'one_eyed_jacks': sum(1 for c in hand if c.is_one_eyed_jack()),
            'dead_cards': sum(1 for c in hand if game.is_dead_card(c)),
            'high_value_cards': 0,  # Cards with multiple good placements
        }

        for card in hand:
            if not card.is_jack():
                positions = game.find_card_positions(card)
                available = sum(1 for r, c in positions if game.is_position_available(r, c))
                if available == 2:
                    analysis['high_value_cards'] += 1

        return analysis
