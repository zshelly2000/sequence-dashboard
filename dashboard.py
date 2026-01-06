"""
Sequence Game Analysis Dashboard
Creates beautiful visualizations from simulation data.
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from collections import defaultdict
from datetime import datetime
import os

# Set style for aesthetically pleasing plots
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['figure.titlesize'] = 16
plt.rcParams['figure.dpi'] = 120

# Custom color palette
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'accent': '#F18F01',
    'success': '#C73E1D',
    'background': '#F7F7F7',
    'player1': '#3498db',
    'player2': '#e74c3c',
    'neutral': '#95a5a6',
    'gradient_start': '#667eea',
    'gradient_end': '#764ba2',
}

# Board layout for reference
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


class SequenceDashboard:
    """Creates visualizations from simulation data."""

    def __init__(self, game_records: list, move_records: list, summary: dict):
        self.game_records = game_records
        self.move_records = move_records
        self.summary = summary
        self.output_dir = "dashboard_output"
        os.makedirs(self.output_dir, exist_ok=True)

    def create_all_visualizations(self):
        """Generate all dashboard visualizations."""
        print("Creating dashboard visualizations...")

        # Create individual plots
        self.create_win_rate_chart()
        self.create_game_length_distribution()
        self.create_board_heatmap()
        self.create_winning_positions_heatmap()
        self.create_sequence_direction_chart()
        self.create_card_usage_chart()
        self.create_strategy_evolution()
        self.create_jack_usage_analysis()
        self.create_first_sequence_analysis()
        self.create_blocking_effectiveness()

        # Create combined dashboard
        self.create_combined_dashboard()

        print(f"\nDashboard visualizations saved to: {self.output_dir}/")

    def create_win_rate_chart(self):
        """Create a beautiful pie/donut chart of win rates."""
        fig, ax = plt.subplots(figsize=(8, 8))

        sizes = [
            self.summary['player1_wins'],
            self.summary['player2_wins'],
            self.summary['draws']
        ]
        labels = ['Player 1 (Blue)', 'Player 2 (Green)', 'Draws']
        colors = [COLORS['player1'], COLORS['player2'], COLORS['neutral']]
        explode = (0.02, 0.02, 0.02)

        # Create donut chart
        wedges, texts, autotexts = ax.pie(
            sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=False, startangle=90,
            wedgeprops=dict(width=0.5, edgecolor='white'),
            textprops={'fontsize': 11, 'fontweight': 'bold'}
        )

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(12)

        # Add center circle for donut effect
        centre_circle = plt.Circle((0, 0), 0.35, fc='white')
        ax.add_patch(centre_circle)

        # Add total games in center
        ax.text(0, 0, f'{self.summary["total_games"]}\nGames',
                ha='center', va='center', fontsize=16, fontweight='bold')

        ax.set_title('Win Rate Distribution', fontsize=16, fontweight='bold', pad=20)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/win_rate_chart.png', dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close()

    def create_game_length_distribution(self):
        """Create histogram of game lengths."""
        fig, ax = plt.subplots(figsize=(10, 6))

        lengths = [g['total_turns'] for g in self.game_records]

        # Create gradient effect
        n, bins, patches = ax.hist(lengths, bins=30, edgecolor='white', linewidth=0.5)

        # Color gradient
        cm = plt.cm.get_cmap('viridis')
        bin_centers = 0.5 * (bins[:-1] + bins[1:])
        col = bin_centers - min(bin_centers)
        col /= max(col)
        for c, p in zip(col, patches):
            plt.setp(p, 'facecolor', cm(c))

        ax.axvline(np.mean(lengths), color=COLORS['secondary'], linestyle='--',
                   linewidth=2, label=f'Mean: {np.mean(lengths):.1f}')
        ax.axvline(np.median(lengths), color=COLORS['accent'], linestyle=':',
                   linewidth=2, label=f'Median: {np.median(lengths):.1f}')

        ax.set_xlabel('Game Length (turns)', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title('Distribution of Game Lengths', fontsize=14, fontweight='bold')
        ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)

        # Add statistics box
        stats_text = f'Min: {min(lengths)}\nMax: {max(lengths)}\nStd: {np.std(lengths):.1f}'
        props = dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray')
        ax.text(0.95, 0.75, stats_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', horizontalalignment='right', bbox=props)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/game_length_distribution.png', dpi=150,
                    bbox_inches='tight', facecolor='white')
        plt.close()

    def create_board_heatmap(self):
        """Create heatmap of chip placement frequency."""
        fig, ax = plt.subplots(figsize=(10, 10))

        heatmap_data = np.array(self.summary['position_heatmap'])

        # Custom colormap
        colors_list = ['#ffffff', '#e8f4f8', '#b3d9e8', '#7fc7dc', '#4ab3cf', '#1a9fbb', '#0d7a91']
        cmap = LinearSegmentedColormap.from_list('custom', colors_list)

        im = ax.imshow(heatmap_data, cmap=cmap, interpolation='nearest')

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Placement Frequency', fontsize=11)

        # Add board labels
        for i in range(10):
            for j in range(10):
                card = BOARD_LAYOUT[i][j]
                count = heatmap_data[i][j]

                # Determine text color based on background
                text_color = 'white' if count > heatmap_data.max() * 0.6 else 'black'
                if card == 'XX':
                    text_color = 'gold'

                ax.text(j, i, card, ha='center', va='center',
                        fontsize=7, fontweight='bold', color=text_color)

        ax.set_xticks(np.arange(10))
        ax.set_yticks(np.arange(10))
        ax.set_xticklabels(range(10))
        ax.set_yticklabels(range(10))
        ax.set_title('Board Position Heatmap\n(Chip Placement Frequency)', fontsize=14, fontweight='bold')

        # Add grid
        ax.set_xticks(np.arange(-0.5, 10, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, 10, 1), minor=True)
        ax.grid(which='minor', color='white', linestyle='-', linewidth=2)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/board_heatmap.png', dpi=150,
                    bbox_inches='tight', facecolor='white')
        plt.close()

    def create_winning_positions_heatmap(self):
        """Create heatmap of positions in winning configurations."""
        fig, ax = plt.subplots(figsize=(10, 10))

        heatmap_data = np.array(self.summary['winning_position_heatmap'])

        # Use red/orange colormap for winning positions
        colors_list = ['#ffffff', '#ffe6e6', '#ffb3b3', '#ff8080', '#ff4d4d', '#ff1a1a', '#cc0000']
        cmap = LinearSegmentedColormap.from_list('winning', colors_list)

        im = ax.imshow(heatmap_data, cmap=cmap, interpolation='nearest')

        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Winning Position Frequency', fontsize=11)

        # Add board labels
        for i in range(10):
            for j in range(10):
                card = BOARD_LAYOUT[i][j]
                count = heatmap_data[i][j]

                text_color = 'white' if count > heatmap_data.max() * 0.5 else 'black'
                if card == 'XX':
                    text_color = 'gold'

                ax.text(j, i, card, ha='center', va='center',
                        fontsize=7, fontweight='bold', color=text_color)

        ax.set_xticks(np.arange(10))
        ax.set_yticks(np.arange(10))
        ax.set_xticklabels(range(10))
        ax.set_yticklabels(range(10))
        ax.set_title('Winning Positions Heatmap\n(Positions on Winning Board)', fontsize=14, fontweight='bold')

        ax.set_xticks(np.arange(-0.5, 10, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, 10, 1), minor=True)
        ax.grid(which='minor', color='white', linestyle='-', linewidth=2)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/winning_positions_heatmap.png', dpi=150,
                    bbox_inches='tight', facecolor='white')
        plt.close()

    def create_sequence_direction_chart(self):
        """Create bar chart of sequence directions."""
        fig, ax = plt.subplots(figsize=(10, 6))

        directions = self.summary['sequence_directions']
        labels = list(directions.keys())
        values = list(directions.values())

        # Better labels
        label_map = {
            'horizontal': 'Horizontal',
            'vertical': 'Vertical',
            'diagonal_down_right': 'Diagonal ↘',
            'diagonal_down_left': 'Diagonal ↙'
        }
        labels = [label_map.get(l, l) for l in labels]

        colors = [COLORS['primary'], COLORS['secondary'], COLORS['accent'], COLORS['success']]
        bars = ax.bar(labels, values, color=colors[:len(labels)], edgecolor='white', linewidth=2)

        # Add value labels on bars
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.annotate(f'{val}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontweight='bold', fontsize=12)

        ax.set_ylabel('Number of Sequences', fontsize=12)
        ax.set_title('Sequence Direction Distribution', fontsize=14, fontweight='bold')

        # Add percentage labels
        total = sum(values)
        for bar, val in zip(bars, values):
            pct = val / total * 100
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2,
                    f'{pct:.1f}%', ha='center', va='center', color='white',
                    fontweight='bold', fontsize=11)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/sequence_directions.png', dpi=150,
                    bbox_inches='tight', facecolor='white')
        plt.close()

    def create_card_usage_chart(self):
        """Create chart showing most/least played cards."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        card_freq = self.summary['card_play_frequency']

        # Sort cards by frequency
        sorted_cards = sorted(card_freq.items(), key=lambda x: x[1], reverse=True)

        # Top 15 most played
        top_cards = sorted_cards[:15]
        cards, counts = zip(*top_cards)
        y_pos = np.arange(len(cards))

        bars1 = ax1.barh(y_pos, counts, color=COLORS['primary'], edgecolor='white')
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(cards)
        ax1.invert_yaxis()
        ax1.set_xlabel('Times Played', fontsize=11)
        ax1.set_title('Most Played Cards', fontsize=13, fontweight='bold')

        for bar, count in zip(bars1, counts):
            ax1.text(count + 5, bar.get_y() + bar.get_height()/2, f'{count}',
                     va='center', fontsize=9)

        # Bottom 15 least played (excluding cards not played)
        bottom_cards = [c for c in sorted_cards[-15:] if c[1] > 0]
        if bottom_cards:
            cards2, counts2 = zip(*bottom_cards)
            y_pos2 = np.arange(len(cards2))

            bars2 = ax2.barh(y_pos2, counts2, color=COLORS['secondary'], edgecolor='white')
            ax2.set_yticks(y_pos2)
            ax2.set_yticklabels(cards2)
            ax2.invert_yaxis()
            ax2.set_xlabel('Times Played', fontsize=11)
            ax2.set_title('Least Played Cards', fontsize=13, fontweight='bold')

            for bar, count in zip(bars2, counts2):
                ax2.text(count + 1, bar.get_y() + bar.get_height()/2, f'{count}',
                         va='center', fontsize=9)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/card_usage.png', dpi=150,
                    bbox_inches='tight', facecolor='white')
        plt.close()

    def create_strategy_evolution(self):
        """Create chart showing offensive vs defensive scores over game progression."""
        fig, ax = plt.subplots(figsize=(12, 6))

        # Group moves by turn number and calculate average scores
        turn_offensive = defaultdict(list)
        turn_defensive = defaultdict(list)

        for move in self.move_records:
            turn = move['turn_number']
            if turn < 100:  # Focus on first 100 turns
                turn_offensive[turn].append(move['offensive_score'])
                turn_defensive[turn].append(move['defensive_score'])

        turns = sorted(turn_offensive.keys())
        avg_offensive = [np.mean(turn_offensive[t]) for t in turns]
        avg_defensive = [np.mean(turn_defensive[t]) for t in turns]

        # Smooth with rolling average
        window = 5
        if len(avg_offensive) > window:
            avg_offensive_smooth = np.convolve(avg_offensive, np.ones(window)/window, mode='valid')
            avg_defensive_smooth = np.convolve(avg_defensive, np.ones(window)/window, mode='valid')
            turns_smooth = turns[window-1:]
        else:
            avg_offensive_smooth = avg_offensive
            avg_defensive_smooth = avg_defensive
            turns_smooth = turns

        ax.plot(turns_smooth, avg_offensive_smooth, label='Offensive Strategy',
                color=COLORS['player1'], linewidth=2.5, alpha=0.9)
        ax.plot(turns_smooth, avg_defensive_smooth, label='Defensive Strategy',
                color=COLORS['player2'], linewidth=2.5, alpha=0.9)

        ax.fill_between(turns_smooth, avg_offensive_smooth, alpha=0.2, color=COLORS['player1'])
        ax.fill_between(turns_smooth, avg_defensive_smooth, alpha=0.2, color=COLORS['player2'])

        ax.set_xlabel('Turn Number', fontsize=12)
        ax.set_ylabel('Average Score', fontsize=12)
        ax.set_title('Strategy Evolution Throughout Games\n(Offensive vs Defensive Priorities)',
                     fontsize=14, fontweight='bold')
        ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/strategy_evolution.png', dpi=150,
                    bbox_inches='tight', facecolor='white')
        plt.close()

    def create_jack_usage_analysis(self):
        """Analyze Jack card usage patterns."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Jack usage by player
        p1_jacks = [g['jacks_used_player1'] for g in self.game_records]
        p2_jacks = [g['jacks_used_player2'] for g in self.game_records]

        ax1.hist([p1_jacks, p2_jacks], bins=range(0, max(max(p1_jacks), max(p2_jacks)) + 2),
                 label=['Player 1', 'Player 2'], color=[COLORS['player1'], COLORS['player2']],
                 edgecolor='white', alpha=0.7)
        ax1.set_xlabel('Jacks Used Per Game', fontsize=11)
        ax1.set_ylabel('Frequency', fontsize=11)
        ax1.set_title('Jack Usage Distribution by Player', fontsize=13, fontweight='bold')
        ax1.legend(frameon=True, fancybox=True)

        # Jack usage timing
        jack_turns = []
        for move in self.move_records:
            if 'J' in move['card']:
                jack_turns.append(move['turn_number'])

        if jack_turns:
            ax2.hist(jack_turns, bins=30, color=COLORS['accent'], edgecolor='white', alpha=0.8)
            ax2.axvline(np.mean(jack_turns), color=COLORS['secondary'], linestyle='--',
                        linewidth=2, label=f'Mean: {np.mean(jack_turns):.1f}')
            ax2.set_xlabel('Turn Number', fontsize=11)
            ax2.set_ylabel('Frequency', fontsize=11)
            ax2.set_title('When Are Jacks Played?', fontsize=13, fontweight='bold')
            ax2.legend(frameon=True, fancybox=True)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/jack_analysis.png', dpi=150,
                    bbox_inches='tight', facecolor='white')
        plt.close()

    def create_first_sequence_analysis(self):
        """Analyze first sequence timing and winner correlation."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # First sequence turn distribution
        first_seq_turns = [g['first_sequence_turn'] for g in self.game_records
                          if g['first_sequence_turn'] is not None]

        ax1.hist(first_seq_turns, bins=25, color=COLORS['primary'], edgecolor='white', alpha=0.8)
        ax1.axvline(np.mean(first_seq_turns), color=COLORS['accent'], linestyle='--',
                    linewidth=2, label=f'Mean: {np.mean(first_seq_turns):.1f}')
        ax1.set_xlabel('Turn Number', fontsize=11)
        ax1.set_ylabel('Frequency', fontsize=11)
        ax1.set_title('When Is First Sequence Completed?', fontsize=13, fontweight='bold')
        ax1.legend(frameon=True, fancybox=True)

        # Does first sequence winner usually win?
        first_seq_wins = sum(1 for g in self.game_records
                            if g['first_sequence_player'] == g['winner']
                            and g['first_sequence_player'] is not None)
        first_seq_losses = sum(1 for g in self.game_records
                              if g['first_sequence_player'] != g['winner']
                              and g['first_sequence_player'] is not None
                              and g['winner'] is not None)

        labels = ['Won Game', 'Lost Game']
        sizes = [first_seq_wins, first_seq_losses]
        colors = [COLORS['success'], COLORS['neutral']]

        wedges, texts, autotexts = ax2.pie(sizes, labels=labels, colors=colors,
                                           autopct='%1.1f%%', startangle=90,
                                           wedgeprops=dict(edgecolor='white'))
        ax2.set_title('First Sequence Maker Outcome', fontsize=13, fontweight='bold')

        for autotext in autotexts:
            autotext.set_fontweight('bold')

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/first_sequence_analysis.png', dpi=150,
                    bbox_inches='tight', facecolor='white')
        plt.close()

    def create_blocking_effectiveness(self):
        """Analyze relationship between blocking moves and winning."""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Categorize games by blocking intensity
        p1_wins_low_block = []
        p1_wins_high_block = []

        median_blocks = np.median([g['blocking_moves_player1'] for g in self.game_records])

        for g in self.game_records:
            if g['blocking_moves_player1'] <= median_blocks:
                p1_wins_low_block.append(1 if g['winner'] == 0 else 0)
            else:
                p1_wins_high_block.append(1 if g['winner'] == 0 else 0)

        win_rates = [
            np.mean(p1_wins_low_block) * 100 if p1_wins_low_block else 0,
            np.mean(p1_wins_high_block) * 100 if p1_wins_high_block else 0
        ]

        labels = [f'Low Blocking\n(≤{median_blocks:.0f} moves)', f'High Blocking\n(>{median_blocks:.0f} moves)']
        colors = [COLORS['player1'], COLORS['primary']]

        bars = ax.bar(labels, win_rates, color=colors, edgecolor='white', width=0.6)

        for bar, rate in zip(bars, win_rates):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{rate:.1f}%', ha='center', fontweight='bold', fontsize=12)

        ax.set_ylabel('Win Rate (%)', fontsize=12)
        ax.set_title('Does Defensive Play (Blocking) Lead to More Wins?', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 100)

        # Add horizontal line at 50%
        ax.axhline(50, color='gray', linestyle='--', alpha=0.5, label='50% baseline')
        ax.legend(loc='upper right')

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/blocking_effectiveness.png', dpi=150,
                    bbox_inches='tight', facecolor='white')
        plt.close()

    def create_combined_dashboard(self):
        """Create a combined multi-panel dashboard."""
        fig = plt.figure(figsize=(20, 24))
        fig.suptitle('Sequence Game Analysis Dashboard\n1,000 Game Simulation Results',
                     fontsize=20, fontweight='bold', y=0.98)

        # Layout: 4 rows, 3 columns
        gs = fig.add_gridspec(4, 3, hspace=0.3, wspace=0.3)

        # 1. Win Rate Pie Chart (top left)
        ax1 = fig.add_subplot(gs[0, 0])
        sizes = [self.summary['player1_wins'], self.summary['player2_wins'], self.summary['draws']]
        colors = [COLORS['player1'], COLORS['player2'], COLORS['neutral']]
        wedges, texts, autotexts = ax1.pie(sizes, colors=colors, autopct='%1.1f%%',
                                           wedgeprops=dict(width=0.5, edgecolor='white'))
        ax1.set_title('Win Distribution', fontsize=12, fontweight='bold')

        # 2. Key Statistics (top middle)
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.axis('off')
        stats_text = f"""
        KEY STATISTICS

        Total Games: {self.summary['total_games']}

        Player 1 Wins: {self.summary['player1_wins']}
        Player 2 Wins: {self.summary['player2_wins']}
        Draws: {self.summary['draws']}

        Avg Game Length: {self.summary['average_game_length']:.1f} turns
        Shortest Game: {self.summary['min_game_length']} turns
        Longest Game: {self.summary['max_game_length']} turns

        Avg First Sequence: Turn {self.summary['average_first_sequence_turn']:.1f}
        """
        ax2.text(0.5, 0.5, stats_text, transform=ax2.transAxes, fontsize=11,
                 verticalalignment='center', horizontalalignment='center',
                 fontfamily='monospace',
                 bbox=dict(boxstyle='round', facecolor='white', edgecolor='gray', alpha=0.9))

        # 3. Sequence Directions (top right)
        ax3 = fig.add_subplot(gs[0, 2])
        directions = self.summary['sequence_directions']
        label_map = {'horizontal': 'Horiz', 'vertical': 'Vert',
                     'diagonal_down_right': 'Diag↘', 'diagonal_down_left': 'Diag↙'}
        labels = [label_map.get(k, k) for k in directions.keys()]
        values = list(directions.values())
        bars = ax3.bar(labels, values, color=[COLORS['primary'], COLORS['secondary'],
                                              COLORS['accent'], COLORS['success']])
        ax3.set_title('Sequence Directions', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Count')

        # 4. Board Heatmap (middle left, spans 2 columns)
        ax4 = fig.add_subplot(gs[1, 0:2])
        heatmap_data = np.array(self.summary['position_heatmap'])
        im = ax4.imshow(heatmap_data, cmap='YlOrRd', interpolation='nearest')
        for i in range(10):
            for j in range(10):
                card = BOARD_LAYOUT[i][j]
                ax4.text(j, i, card, ha='center', va='center', fontsize=6,
                        color='black' if heatmap_data[i][j] < heatmap_data.max()*0.6 else 'white')
        ax4.set_title('Position Heatmap (All Placements)', fontsize=12, fontweight='bold')
        plt.colorbar(im, ax=ax4, shrink=0.8)

        # 5. Game Length Distribution (middle right)
        ax5 = fig.add_subplot(gs[1, 2])
        lengths = [g['total_turns'] for g in self.game_records]
        ax5.hist(lengths, bins=25, color=COLORS['primary'], edgecolor='white', alpha=0.8)
        ax5.axvline(np.mean(lengths), color=COLORS['accent'], linestyle='--', linewidth=2)
        ax5.set_xlabel('Turns')
        ax5.set_ylabel('Frequency')
        ax5.set_title('Game Length Distribution', fontsize=12, fontweight='bold')

        # 6. Strategy Evolution (bottom left, spans 2 columns)
        ax6 = fig.add_subplot(gs[2, 0:2])
        turn_offensive = defaultdict(list)
        turn_defensive = defaultdict(list)
        for move in self.move_records:
            turn = move['turn_number']
            if turn < 80:
                turn_offensive[turn].append(move['offensive_score'])
                turn_defensive[turn].append(move['defensive_score'])
        turns = sorted(turn_offensive.keys())
        avg_off = [np.mean(turn_offensive[t]) for t in turns]
        avg_def = [np.mean(turn_defensive[t]) for t in turns]
        ax6.plot(turns, avg_off, label='Offensive', color=COLORS['player1'], linewidth=2)
        ax6.plot(turns, avg_def, label='Defensive', color=COLORS['player2'], linewidth=2)
        ax6.fill_between(turns, avg_off, alpha=0.2, color=COLORS['player1'])
        ax6.fill_between(turns, avg_def, alpha=0.2, color=COLORS['player2'])
        ax6.set_xlabel('Turn')
        ax6.set_ylabel('Score')
        ax6.set_title('Strategy Evolution Over Game', fontsize=12, fontweight='bold')
        ax6.legend()

        # 7. First Sequence Outcome (bottom right)
        ax7 = fig.add_subplot(gs[2, 2])
        first_seq_wins = sum(1 for g in self.game_records
                            if g['first_sequence_player'] == g['winner']
                            and g['first_sequence_player'] is not None)
        first_seq_losses = sum(1 for g in self.game_records
                              if g['first_sequence_player'] != g['winner']
                              and g['first_sequence_player'] is not None
                              and g['winner'] is not None)
        ax7.pie([first_seq_wins, first_seq_losses], labels=['Won', 'Lost'],
                colors=[COLORS['success'], COLORS['neutral']], autopct='%1.1f%%',
                wedgeprops=dict(edgecolor='white'))
        ax7.set_title('First Sequence Maker\nWin Rate', fontsize=12, fontweight='bold')

        # 8. Top Cards (bottom row, spans 2 columns)
        ax8 = fig.add_subplot(gs[3, 0:2])
        card_freq = self.summary['card_play_frequency']
        sorted_cards = sorted(card_freq.items(), key=lambda x: x[1], reverse=True)[:12]
        cards, counts = zip(*sorted_cards)
        ax8.barh(range(len(cards)), counts, color=COLORS['primary'])
        ax8.set_yticks(range(len(cards)))
        ax8.set_yticklabels(cards)
        ax8.invert_yaxis()
        ax8.set_xlabel('Times Played')
        ax8.set_title('Most Played Cards', fontsize=12, fontweight='bold')

        # 9. Jack Usage (bottom right)
        ax9 = fig.add_subplot(gs[3, 2])
        p1_jacks = [g['jacks_used_player1'] for g in self.game_records]
        p2_jacks = [g['jacks_used_player2'] for g in self.game_records]
        ax9.boxplot([p1_jacks, p2_jacks], labels=['Player 1', 'Player 2'])
        ax9.set_ylabel('Jacks Used')
        ax9.set_title('Jack Usage per Game', fontsize=12, fontweight='bold')

        plt.savefig(f'{self.output_dir}/combined_dashboard.png', dpi=150,
                    bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"Created combined dashboard: {self.output_dir}/combined_dashboard.png")


def load_and_create_dashboard(games_file: str, moves_file: str, summary_file: str):
    """Load data from files and create dashboard."""
    with open(games_file, 'r') as f:
        game_records = json.load(f)

    with open(moves_file, 'r') as f:
        move_records = json.load(f)

    with open(summary_file, 'r') as f:
        summary = json.load(f)

    dashboard = SequenceDashboard(game_records, move_records, summary)
    dashboard.create_all_visualizations()


if __name__ == "__main__":
    # If run directly, look for most recent data files
    import glob

    game_files = sorted(glob.glob("game_records_*.json"))
    move_files = sorted(glob.glob("move_records_*.json"))
    summary_files = sorted(glob.glob("summary_*.json"))

    if game_files and move_files and summary_files:
        print("Loading most recent simulation data...")
        load_and_create_dashboard(game_files[-1], move_files[-1], summary_files[-1])
    else:
        print("No simulation data found. Run run_simulations.py first.")
