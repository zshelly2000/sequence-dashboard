# Sequence AI Showdown

> **Two perfect AI bots. 1,000 games. One ultimate analysis.**

[![Live Dashboard](https://img.shields.io/badge/Live%20Dashboard-View%20Now-red?style=for-the-badge)](https://zshelly2000.github.io/sequence-dashboard/)
[![Games Played](https://img.shields.io/badge/Games%20Simulated-1,000-blue?style=for-the-badge)](https://zshelly2000.github.io/sequence-dashboard/)
[![Moves Analyzed](https://img.shields.io/badge/Moves%20Analyzed-46,359-green?style=for-the-badge)](https://zshelly2000.github.io/sequence-dashboard/)

---

## [View the Live Dashboard](https://zshelly2000.github.io/sequence-dashboard/)

An ESPN-style analytics dashboard showcasing insights from 1,000 games of Sequence played between two AI bots using optimal strategy.

---

## What is This?

This project simulates the classic board game **Sequence** with two AI bots playing against each other 1,000 times. Every move is recorded and analyzed to discover:

- Which player has the advantage?
- What board positions are most valuable?
- Does making the first sequence predict victory?
- How do offensive vs. defensive strategies evolve during a game?

## Key Findings

| Insight | Value |
|---------|-------|
| **First-Mover Advantage** | Player 1 wins 52.5% of games |
| **First Sequence = Victory** | 70.7% of first-sequence makers win |
| **Average Game Length** | 46 turns |
| **Draw Rate** | 0% (always a winner!) |
| **Most Common Sequence** | Vertical (34.7%) |

## Dashboard Features

The interactive dashboard includes:

- **Win Rate Distribution** - Donut chart showing overall results
- **Board Heatmaps** - Which positions are played most often
- **Strategy Evolution** - How offense/defense priorities change throughout games
- **First Sequence Analysis** - Timing and impact of the first completed sequence
- **Card Usage Statistics** - Most and least played cards
- **Jack Analysis** - When and how special cards are used

## Project Structure

```
sequence-dashboard/
├── sequence_game.py      # Complete Sequence game engine
├── sequence_bot.py       # AI bot with strategic evaluation
├── run_simulations.py    # Simulation runner & data collection
├── dashboard.py          # Visualization generator
├── main.py               # Main entry point
├── requirements.txt      # Python dependencies
└── docs/                 # Dashboard website
    ├── index.html        # ESPN-style dashboard
    └── *.png             # Visualization images
```

## How the AI Works

The bot uses a scoring system that evaluates each possible move based on:

1. **Offensive Value** - Does this move build toward a sequence?
2. **Defensive Value** - Does this move block the opponent?
3. **Sequence Potential** - How many future sequences could this enable?
4. **Jack Conservation** - Save special cards for critical moments
5. **Position Value** - Center and corner-adjacent positions are prioritized

## Run It Yourself

```bash
# Install dependencies
pip install matplotlib numpy

# Run 1,000 game simulation (takes ~2 minutes)
python main.py
```

## Tech Stack

- **Python** - Game engine and AI logic
- **Matplotlib** - Data visualization
- **NumPy** - Statistical analysis
- **GitHub Pages** - Dashboard hosting

## About Sequence

Sequence is a board-and-card game where players try to create rows of 5 chips on a 10x10 board by playing cards from their hand. Special "Jack" cards can place chips anywhere (two-eyed) or remove opponent chips (one-eyed). First player to complete 2 sequences wins!

---

<p align="center">
  <a href="https://zshelly2000.github.io/sequence-dashboard/">
    <img src="https://img.shields.io/badge/VIEW%20LIVE%20DASHBOARD-FF0000?style=for-the-badge&logo=github&logoColor=white" alt="View Dashboard" />
  </a>
</p>

---

*Built with Python | Visualized with Matplotlib | Hosted on GitHub Pages*
