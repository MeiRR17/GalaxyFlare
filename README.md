# Galaxy Flare

A small offline arcade space shooter built with Python and Pygame.

## Install and play

Requires Python 3.10+ with a desktop display and Pygame 2.5 or later.

```bash
python -m pip install -r requirements.txt
python src/main.py
```

The game loads images relative to the repository's `img/` directory, **not** the current working directory. It can therefore be launched from an IDE, terminal, or another working directory without breaking image paths. No network connection, accounts, tracking, or backend are required.

## Controls

| Control | Action |
| --- | --- |
| Arrow keys / WASD | Move in two dimensions |
| Space (hold) | Shoot lasers at a capped rate |
| R (game over) | Restart with a fresh score and three lives |
| Esc / close window | Exit |

Hit meteors with lasers to earn ten points each. Meteors accelerate gradually as the session progresses. Collisions with the player cost one life; a short visible invulnerability window prevents rapid repeated damage. After three hits, the game ends and displays the score. Meteor sprites that move off-screen are removed to avoid accumulating objects indefinitely.

## Files

The main game entry point is `src/main.py`. Images are loaded from `img/` (including `img/meteors/m1.png`). Dependency declarations are in `requirements.txt`. The code is intentionally single-player and entirely local; there is no saved high-score system or audio playback yet.

## Development state

This is an MVP implemented on a feature branch. No tests or gameplay acceptance run were performed in this development cycle. It is not a packaged desktop release, and `master` remains unchanged until review.
