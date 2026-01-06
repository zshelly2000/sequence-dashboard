"""
Sequence Game Simulation Runner
Runs 1,000 games between two AI bots and collects detailed statistics.
"""

import json
import random
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional
from collections import defaultdict
import time

from sequence_game import SequenceGame, ChipColor
from sequence_bot import SequenceBot


@dataclass
class MoveRecord:
    game_id: int
    turn_number: int
    player_id: int
    card: str
    row: int
    col: int
    is_removal: bool
    offensive_score: float
    defensive_score: float
    total_score: float
    creates_sequence: bool
    blocks_opponent: bool
    sequence_potential: int
    reasoning: str
    player_chip_count: int
    opponent_chip_count: int
    player_sequences: int
    opponent_sequences: int
    cards_remaining_in_deck: int


@dataclass
class GameRecord:
    game_id: int
    winner: Optional[int]
    total_turns: int
    player1_strategy: str
    player2_strategy: str
    player1_sequences: int
    player2_sequences: int
    player1_chips_placed: int
    player2_chips_placed: int
    duration_seconds: float
    first_sequence_turn: Optional[int]
    first_sequence_player: Optional[int]
    jacks_used_player1: int
    jacks_used_player2: int
    blocking_moves_player1: int
    blocking_moves_player2: int
    average_offensive_score_p1: float
    average_offensive_score_p2: float
    average_defensive_score_p1: float
    average_defensive_score_p2: float


class SimulationRunner:
    """Runs multiple games and collects statistics."""

    def __init__(self, num_games: int = 1000,
                 player1_strategy: str = "balanced",
                 player2_strategy: str = "balanced"):
        self.num_games = num_games
        self.player1_strategy = player1_strategy
        self.player2_strategy = player2_strategy
        self.move_records = []
        self.game_records = []
        self.position_heatmap = [[0 for _ in range(10)] for _ in range(10)]
        self.winning_position_heatmap = [[0 for _ in range(10)] for _ in range(10)]
        self.first_move_positions = defaultdict(int)
        self.sequence_directions = defaultdict(int)
        self.card_play_frequency = defaultdict(int)
        self.winning_card_frequency = defaultdict(int)

    def run_single_game(self, game_id: int) -> GameRecord:
        """Run a single game and collect data."""
        start_time = time.time()

        game = SequenceGame(num_players=2)
        game.initialize_game()

        bot1 = SequenceBot(player_id=0, strategy=self.player1_strategy)
        bot2 = SequenceBot(player_id=1, strategy=self.player2_strategy)
        bots = [bot1, bot2]

        # Game statistics
        jacks_used = [0, 0]
        blocking_moves = [0, 0]
        offensive_scores = [[], []]
        defensive_scores = [[], []]
        chips_placed = [0, 0]
        first_sequence_turn = None
        first_sequence_player = None
        prev_sequences = [0, 0]

        turn = 0
        max_turns = 500  # Safety limit

        while not game.is_game_over() and turn < max_turns:
            current_player = game.state.current_player
            bot = bots[current_player]

            # Get move with analysis
            evaluation = bot.get_move_with_analysis(game)

            if evaluation is None:
                break

            move = evaluation.move

            # Record move data
            opponent_id = 1 - current_player
            move_record = MoveRecord(
                game_id=game_id,
                turn_number=turn,
                player_id=current_player,
                card=str(move.card),
                row=move.row,
                col=move.col,
                is_removal=move.is_removal,
                offensive_score=evaluation.offensive_score,
                defensive_score=evaluation.defensive_score,
                total_score=evaluation.score,
                creates_sequence=evaluation.creates_sequence,
                blocks_opponent=evaluation.blocks_opponent,
                sequence_potential=evaluation.sequence_potential,
                reasoning=evaluation.reasoning,
                player_chip_count=len(game.state.chips_on_board[current_player]),
                opponent_chip_count=len(game.state.chips_on_board[opponent_id]),
                player_sequences=len(game.state.sequences[current_player]),
                opponent_sequences=len(game.state.sequences[opponent_id]),
                cards_remaining_in_deck=len(game.state.deck)
            )
            self.move_records.append(move_record)

            # Update statistics
            if move.card.is_jack():
                jacks_used[current_player] += 1

            if evaluation.blocks_opponent:
                blocking_moves[current_player] += 1

            offensive_scores[current_player].append(evaluation.offensive_score)
            defensive_scores[current_player].append(evaluation.defensive_score)

            if not move.is_removal:
                chips_placed[current_player] += 1
                self.position_heatmap[move.row][move.col] += 1
                self.card_play_frequency[str(move.card)] += 1

                if turn == 0:
                    self.first_move_positions[(move.row, move.col)] += 1

            # Execute move
            game.make_move(move)

            # Check for first sequence
            for player in range(2):
                if len(game.state.sequences[player]) > prev_sequences[player]:
                    if first_sequence_turn is None:
                        first_sequence_turn = turn
                        first_sequence_player = player

                        # Record sequence direction
                        new_seq = game.state.sequences[player][-1]
                        direction = self._get_sequence_direction(new_seq)
                        self.sequence_directions[direction] += 1

                    prev_sequences[player] = len(game.state.sequences[player])

            turn += 1

        # Game complete - record results
        end_time = time.time()
        winner = game.get_winner()

        # Update winning position heatmap
        if winner is not None:
            for row, col in game.state.chips_on_board[winner]:
                self.winning_position_heatmap[row][col] += 1

            # Track winning cards
            for move_rec in self.move_records[-turn:]:
                if move_rec.game_id == game_id and move_rec.player_id == winner:
                    self.winning_card_frequency[move_rec.card] += 1

        game_record = GameRecord(
            game_id=game_id,
            winner=winner,
            total_turns=turn,
            player1_strategy=self.player1_strategy,
            player2_strategy=self.player2_strategy,
            player1_sequences=len(game.state.sequences[0]),
            player2_sequences=len(game.state.sequences[1]),
            player1_chips_placed=chips_placed[0],
            player2_chips_placed=chips_placed[1],
            duration_seconds=end_time - start_time,
            first_sequence_turn=first_sequence_turn,
            first_sequence_player=first_sequence_player,
            jacks_used_player1=jacks_used[0],
            jacks_used_player2=jacks_used[1],
            blocking_moves_player1=blocking_moves[0],
            blocking_moves_player2=blocking_moves[1],
            average_offensive_score_p1=sum(offensive_scores[0]) / len(offensive_scores[0]) if offensive_scores[0] else 0,
            average_offensive_score_p2=sum(offensive_scores[1]) / len(offensive_scores[1]) if offensive_scores[1] else 0,
            average_defensive_score_p1=sum(defensive_scores[0]) / len(defensive_scores[0]) if defensive_scores[0] else 0,
            average_defensive_score_p2=sum(defensive_scores[1]) / len(defensive_scores[1]) if defensive_scores[1] else 0,
        )

        self.game_records.append(game_record)
        return game_record

    def _get_sequence_direction(self, sequence: list) -> str:
        """Determine the direction of a sequence."""
        if len(sequence) < 2:
            return "unknown"

        r1, c1 = sequence[0]
        r2, c2 = sequence[1]
        dr, dc = r2 - r1, c2 - c1

        if dr == 0:
            return "horizontal"
        elif dc == 0:
            return "vertical"
        elif dr == dc:
            return "diagonal_down_right"
        else:
            return "diagonal_down_left"

    def run_all_games(self, verbose: bool = True) -> dict:
        """Run all simulations and return summary statistics."""
        print(f"Starting {self.num_games} game simulations...")
        print(f"Player 1 Strategy: {self.player1_strategy}")
        print(f"Player 2 Strategy: {self.player2_strategy}")
        print("-" * 50)

        start_time = time.time()

        for i in range(self.num_games):
            self.run_single_game(i)

            if verbose and (i + 1) % 100 == 0:
                elapsed = time.time() - start_time
                avg_time = elapsed / (i + 1)
                remaining = avg_time * (self.num_games - i - 1)
                print(f"Completed {i + 1}/{self.num_games} games "
                      f"({elapsed:.1f}s elapsed, ~{remaining:.1f}s remaining)")

        total_time = time.time() - start_time
        print(f"\nAll {self.num_games} games completed in {total_time:.2f} seconds")

        return self.generate_summary()

    def generate_summary(self) -> dict:
        """Generate summary statistics from all games."""
        wins = [0, 0, 0]  # [player1, player2, draws]
        total_turns = []
        first_seq_turns = []

        for record in self.game_records:
            if record.winner == 0:
                wins[0] += 1
            elif record.winner == 1:
                wins[1] += 1
            else:
                wins[2] += 1

            total_turns.append(record.total_turns)
            if record.first_sequence_turn is not None:
                first_seq_turns.append(record.first_sequence_turn)

        summary = {
            'total_games': self.num_games,
            'player1_wins': wins[0],
            'player2_wins': wins[1],
            'draws': wins[2],
            'player1_win_rate': wins[0] / self.num_games * 100,
            'player2_win_rate': wins[1] / self.num_games * 100,
            'draw_rate': wins[2] / self.num_games * 100,
            'average_game_length': sum(total_turns) / len(total_turns) if total_turns else 0,
            'min_game_length': min(total_turns) if total_turns else 0,
            'max_game_length': max(total_turns) if total_turns else 0,
            'average_first_sequence_turn': sum(first_seq_turns) / len(first_seq_turns) if first_seq_turns else 0,
            'total_moves_recorded': len(self.move_records),
            'position_heatmap': self.position_heatmap,
            'winning_position_heatmap': self.winning_position_heatmap,
            'first_move_positions': dict(self.first_move_positions),
            'sequence_directions': dict(self.sequence_directions),
            'card_play_frequency': dict(self.card_play_frequency),
            'winning_card_frequency': dict(self.winning_card_frequency),
        }

        return summary

    def save_results(self, output_dir: str = "."):
        """Save all results to JSON files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save game records
        games_file = f"{output_dir}/game_records_{timestamp}.json"
        with open(games_file, 'w') as f:
            json.dump([asdict(r) for r in self.game_records], f, indent=2)
        print(f"Saved game records to {games_file}")

        # Save move records (can be large)
        moves_file = f"{output_dir}/move_records_{timestamp}.json"
        with open(moves_file, 'w') as f:
            json.dump([asdict(r) for r in self.move_records], f)
        print(f"Saved move records to {moves_file}")

        # Save summary
        summary = self.generate_summary()
        # Convert tuple keys to strings for JSON
        summary['first_move_positions'] = {
            f"{k[0]},{k[1]}": v for k, v in self.first_move_positions.items()
        }
        summary_file = f"{output_dir}/summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"Saved summary to {summary_file}")

        return {
            'games_file': games_file,
            'moves_file': moves_file,
            'summary_file': summary_file,
            'timestamp': timestamp
        }


def run_strategy_comparison():
    """Run simulations comparing different strategies."""
    strategies = ["balanced", "aggressive", "defensive"]
    results = {}

    for s1 in strategies:
        for s2 in strategies:
            print(f"\n{'='*60}")
            print(f"Running: {s1} vs {s2}")
            print('='*60)

            runner = SimulationRunner(
                num_games=100,  # Fewer games for comparison
                player1_strategy=s1,
                player2_strategy=s2
            )
            summary = runner.run_all_games(verbose=False)
            results[f"{s1}_vs_{s2}"] = {
                'p1_win_rate': summary['player1_win_rate'],
                'p2_win_rate': summary['player2_win_rate'],
                'draw_rate': summary['draw_rate'],
                'avg_length': summary['average_game_length']
            }

            print(f"Results: P1({s1})={summary['player1_win_rate']:.1f}%, "
                  f"P2({s2})={summary['player2_win_rate']:.1f}%, "
                  f"Draws={summary['draw_rate']:.1f}%")

    return results


if __name__ == "__main__":
    # Run main simulation
    print("=" * 60)
    print("SEQUENCE GAME SIMULATION")
    print("1,000 Games Between Two Optimal Bots")
    print("=" * 60)

    runner = SimulationRunner(num_games=1000)
    summary = runner.run_all_games()

    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)
    print(f"Total Games: {summary['total_games']}")
    print(f"Player 1 Wins: {summary['player1_wins']} ({summary['player1_win_rate']:.1f}%)")
    print(f"Player 2 Wins: {summary['player2_wins']} ({summary['player2_win_rate']:.1f}%)")
    print(f"Draws: {summary['draws']} ({summary['draw_rate']:.1f}%)")
    print(f"\nAverage Game Length: {summary['average_game_length']:.1f} turns")
    print(f"Shortest Game: {summary['min_game_length']} turns")
    print(f"Longest Game: {summary['max_game_length']} turns")
    print(f"Average Turn for First Sequence: {summary['average_first_sequence_turn']:.1f}")

    print("\nSequence Directions:")
    for direction, count in summary['sequence_directions'].items():
        print(f"  {direction}: {count}")

    # Save results
    files = runner.save_results()
    print(f"\nResults saved with timestamp: {files['timestamp']}")
