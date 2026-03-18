# Pyramid Escape

Pyramid Escape is a small 2D top-down roguelike/shooter MVP made with Python and pygame. The player explores procedurally generated pyramid floors, fights mummies, opens chests, finds a key, and escapes through the exit.

The current map graphics are ASCII-based: pygame renders characters through a font. The player and mummies use pixel-art spritesheets.

## Графика

- Сундуки и пули пока отрисовываются ASCII-символами.
- Пол использует pixel-art tileset из `assets/images/tiles/floor_tileset.png`.
- Стены используют pixel-art tileset из `assets/images/tiles/wall_tileset.png` и остаются непроходимыми.
- Боковые стены используют отдельный спрайт `assets/images/tiles/side_wall.png`.
- Игрок использует pixel-art spritesheet из `assets/images/player/player_movement.png`.
- Мумии используют pixel-art spritesheet из `assets/images/enemies/mummy_sprite_sheet.png`.
- Спрайты оружия, сундуков и части окружения планируются позже.

## How to Run

```bash
pip install -r requirements.txt
python main.py
```

## How to Run Tests

```bash
pytest
```

## Controls

- `WASD` / arrow keys - move
- Left mouse button - shoot toward the cursor
- `E` - pick up the key, open a nearby chest, or use the exit
- `Q` - switch weapon
- `ESC` - pause
- `ENTER` - select menu item or restart after death/win

## Rules

- The player starts on floor 1 with 100 HP and a pistol.
- Each floor contains rooms, corridors, mummies, chests, a key, and an exit.
- The key lies on the floor in a distant room and is picked up with `E`.
- The exit is closed until the key is found.
- HP, score, and weapons are kept between floors.
- After floor 3 the player wins.
- If HP reaches 0, the run restarts from floor 1.

## Implemented Algorithms

Complex algorithms:

- BSP dungeon generation for procedural floors.
- Lightmap-style dark rooms with a light radius around the player.
- Value noise for floor tile visual variation.

Medium algorithms:

- Simple behavior tree for mummy decisions.
- Boids separation so mummies do not stack into one point.
- Spatial hash grid for nearby object queries.
- Swept collision / CCD for fast bullets.

Light algorithms:

- Game loop with deltaTime movement.
- AABB-like tile collision and circle overlap checks.
- Weighted random loot.
- Camera offset and clamp.

## Project Structure

```text
main.py
requirements.txt
README.md

src/
  core/          game loop, settings, scene manager
  scenes/        menu, game, pause, death, win screens
  models/        player, mummies, weapons, bullets, chests, map, rooms
  algorithms/    BSP generation, room graph, validation, value noise
  systems/       movement, combat, collision, loot, lighting, AI, spatial hash
  views/         ASCII renderer, UI renderer, camera
  controllers/   keyboard input

tests/           pytest tests for core algorithms
```
