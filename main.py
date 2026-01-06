"""
Main entry point for Sequence Game Simulation and Analysis
Runs 1,000 games between two optimal bots and generates a dashboard.
"""

import sys
import os

def main():
    print("=" * 70)
    print("  SEQUENCE GAME PERFECT BOT SIMULATION")
    print("  1,000 Games | Full Analysis | Visual Dashboard")
    print("=" * 70)
    print()

    # Import modules
    print("Loading game engine and AI bot...")
    from sequence_game import SequenceGame
    from sequence_bot import SequenceBot
    from run_simulations import SimulationRunner
    from dashboard import SequenceDashboard

    # Run simulations
    print("\nStarting simulation of 1,000 games...")
    print("-" * 70)

    runner = SimulationRunner(num_games=1000)
    summary = runner.run_all_games(verbose=True)

    # Print summary
    print("\n" + "=" * 70)
    print("  SIMULATION COMPLETE - SUMMARY STATISTICS")
    print("=" * 70)

    print(f"""
    OVERALL RESULTS
    ---------------
    Total Games Played:     {summary['total_games']}
    Total Moves Recorded:   {summary['total_moves_recorded']:,}

    WINNER BREAKDOWN
    ----------------
    Player 1 (Blue) Wins:   {summary['player1_wins']:>4} ({summary['player1_win_rate']:.1f}%)
    Player 2 (Green) Wins:  {summary['player2_wins']:>4} ({summary['player2_win_rate']:.1f}%)
    Draws:                  {summary['draws']:>4} ({summary['draw_rate']:.1f}%)

    GAME LENGTH STATISTICS
    ----------------------
    Average Game Length:    {summary['average_game_length']:.1f} turns
    Shortest Game:          {summary['min_game_length']} turns
    Longest Game:           {summary['max_game_length']} turns

    SEQUENCE STATISTICS
    -------------------
    Average First Sequence: Turn {summary['average_first_sequence_turn']:.1f}
    """)

    print("    Sequence Directions:")
    for direction, count in summary['sequence_directions'].items():
        pct = count / sum(summary['sequence_directions'].values()) * 100
        print(f"      {direction:25s}: {count:>5} ({pct:.1f}%)")

    # Save data
    print("\n" + "-" * 70)
    print("Saving simulation data...")
    files = runner.save_results()

    # Generate dashboard
    print("\n" + "-" * 70)
    print("Generating visualization dashboard...")

    dashboard = SequenceDashboard(
        [vars(r) if hasattr(r, '__dict__') else r for r in runner.game_records],
        [vars(r) if hasattr(r, '__dict__') else r for r in runner.move_records],
        summary
    )
    dashboard.create_all_visualizations()

    print("\n" + "=" * 70)
    print("  ALL COMPLETE!")
    print("=" * 70)
    print(f"""
    Data files saved:
      - {files['games_file']}
      - {files['moves_file']}
      - {files['summary_file']}

    Dashboard visualizations saved to:
      - dashboard_output/

    Key insights from {summary['total_games']} games:

    1. First-Mover Advantage: Player 1 wins {summary['player1_win_rate']:.1f}% of games

    2. Optimal Game Length: Average game takes {summary['average_game_length']:.0f} turns

    3. Racing vs Blocking: First sequence typically appears around turn
       {summary['average_first_sequence_turn']:.0f}, suggesting a balance of offense
       and defense is critical

    4. Sequence Formation: The distribution of sequence directions shows
       strategic positioning preferences of the optimal bot
    """)


if __name__ == "__main__":
    main()
