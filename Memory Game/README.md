# 🃏 Memory Match Game

A polished card matching memory game built in Python with Pygame. Test your memory by finding matching pairs of cards!

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- **Smooth Animations** - 3D card flip effects at 60 FPS
- **4 Difficulty Levels** - Easy (6 pairs) to Expert (12 pairs)
- **Progress Tracking** - Matches, attempts, and time
- **Performance Rating** - Get scored based on your efficiency
- **Modern UI** - Clean gradients, hover effects, and polished design

## 🎮 How to Play

1. Select a difficulty level
2. Click on cards to flip them
3. Find matching pairs - matched cards stay face up
4. Match all pairs to win!
5. Try to complete the game in as few attempts as possible

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/memory-match-game.git
   cd memory-match-game
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the game**
   ```bash
   python src/memory_game.py
   ```

## 📁 Project Structure

```
memory-match-game/
├── src/
│   └── memory_game.py      # Main game file
├── assets/                  # Game assets (if any)
├── screenshots/             # Game screenshots
├── requirements.txt         # Python dependencies
├── LICENSE                  # MIT License
└── README.md               # This file
```

## 🎯 Difficulty Levels

| Level  | Pairs | Grid Size | Description |
|--------|-------|-----------|-------------|
| Easy   | 6     | 3 × 4     | Perfect for beginners |
| Medium | 8     | 4 × 4     | A balanced challenge |
| Hard   | 10    | 5 × 4     | For experienced players |
| Expert | 12    | 4 × 6     | Ultimate memory test |

## 🏆 Scoring

Your performance is rated based on attempts vs. number of pairs:

| Rating | Criteria | Message |
|--------|----------|---------|
| 🏆 | Attempts = Pairs | Perfect Score! |
| ⭐ | Attempts ≤ 1.5× Pairs | Excellent! |
| 👍 | Attempts ≤ 2× Pairs | Good Job! |
| 💪 | Attempts > 2× Pairs | Keep practicing! |

## 🎨 Screenshots

*Coming soon - add your own screenshots to the `screenshots/` folder!*

## 🛠️ Technical Details

- **Framework**: Pygame 2.x
- **Resolution**: 800 × 700 pixels
- **Frame Rate**: 60 FPS
- **Card Animation**: Custom flip effect with scaling

## 🤝 Contributing

Contributions are welcome! Here are some ways you can help:

1. 🐛 Report bugs
2. 💡 Suggest new features
3. 🔧 Submit pull requests

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/memory-match-game.git
cd memory-match-game

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the game
python src/memory_game.py
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Pygame](https://www.pygame.org/)
- Card symbols from Unicode playing card characters

---

**Enjoy the game! If you like it, give it a ⭐ on GitHub!**
