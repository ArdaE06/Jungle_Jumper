# 🐰 Jungle Jumper

Jungle Jumper is a fast-paced 2D arcade game developed using Python and Pygame.
The player controls a jumping animal (starting with a bunny 🐰) and must avoid deadly spikes while collecting fruits to earn gold.

---

## 🎮 Gameplay

* The character continuously moves left and right across the screen
* Press **SPACE** to jump and avoid obstacles
* Collect fruits to increase your gold and score
* Avoid spikes — touching them ends the game

---

## ✨ Features

* 🐰 **Character System**

  * Playable animal character (Bunny)
  * Sprite-based animations (left, right, game over)

* 🍎 **Dynamic Coin System**

  * Different fruit types appear as score increases
  * Each fruit gives different gold values:

    * Apple 🍎 → 1 gold
    * Cherry 🍒 → 2 gold
    * Grape 🍇 → 3 gold

* 🛡️ **Bubble Shield Mechanic**

  * Collect a bubble to gain temporary protection
  * Prevents death from one collision
  * Adds strategic gameplay depth

* ⚡ **Progressive Difficulty**

  * More spikes appear as score increases
  * Faster and more challenging gameplay

* 💥 **Particle Effects**

  * Jump particles
  * Death explosion effects
  * Floating score indicators

* 🏆 **Score System**

  * Real-time score tracking
  * High score saving system

* 💰 **Persistent Gold System**

  * Collected coins are saved locally

---

## 🎯 Controls

| Key   | Action                    |
| ----- | ------------------------- |
| SPACE | Jump                      |
| R     | Restart (after game over) |

---

## 🖥️ Technologies Used

* Python
* Pygame

---

## 📂 Project Structure

```
Jungle-Jumper/
│
├── main.py
├── assets/
│   ├── images
│   └── sounds
├── skins/
│   └── bunny/
├── coins.txt
├── highscore.txt
└── README.md
```

---

## 🚀 How to Run

1. Install Python (3.x)
2. Install Pygame:

   ```
   pip install pygame
   ```
3. Run the game:

   ```
   python main.py
   ```

---

## 📌 Future Improvements

* More playable characters
* Sound effects and music
* Menu system
* Mobile support
* Power-ups and abilities

---

## 👨‍💻 Developer

Developed by Arda Esnaf
Computer Engineering Student

---

## ⭐ GitHub

If you like the project, consider giving it a star ⭐

