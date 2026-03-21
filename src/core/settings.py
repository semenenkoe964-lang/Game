WINDOW_WIDTH = 960
WINDOW_HEIGHT = 640
FPS = 60

TILE_SIZE = 24
FONT_SIZE = 22
FONT_NAME = "consolas"

MAX_FLOORS = 3

FLOOR_TILESET = "assets/images/tiles/floor_tileset.png"
FLOOR_TILESET_COLUMNS = 5
FLOOR_TILESET_ROWS = 5
FLOOR_TILESET_TILE_COUNT = FLOOR_TILESET_COLUMNS * FLOOR_TILESET_ROWS
WALL_TILESET = "assets/images/tiles/wall_tileset.png"
SIDE_WALL_SPRITE = "assets/images/tiles/side_wall.png"

COLORS = {
    "background": (8, 8, 10),
    "wall": (170, 145, 95),
    "floor": (116, 100, 72),
    "floor_alt": (145, 128, 91),
    "player": (245, 235, 180),
    "normal_mummy": (116, 220, 126),
    "fast_mummy": (255, 115, 102),
    "bullet": (255, 230, 120),
    "chest": (210, 145, 55),
    "exit_closed": (180, 60, 60),
    "exit_open": (70, 210, 130),
    "medkit": (80, 220, 120),
    "weapon": (105, 190, 255),
    "ui": (238, 232, 210),
    "muted_ui": (170, 164, 145),
    "title": (255, 210, 115),
}

FLOOR_CONFIGS = {
    1: {
        "map_width": 80,
        "map_height": 50,
        "rooms": 6,
        "normal_mummies": 3,
        "fast_mummies": 0,
        "chests": 3,
        "dark_room_chance": 0.2,
    },
    2: {
        "map_width": 90,
        "map_height": 55,
        "rooms": 8,
        "normal_mummies": 4,
        "fast_mummies": 1,
        "chests": 4,
        "dark_room_chance": 0.35,
    },
    3: {
        "map_width": 100,
        "map_height": 60,
        "rooms": 10,
        "normal_mummies": 5,
        "fast_mummies": 2,
        "chests": 5,
        "dark_room_chance": 0.45,
    },
}

PLAYER_MAX_HEALTH = 100
PLAYER_SPEED = 180
PLAYER_RADIUS = 9
PLAYER_START_WEAPON = "Pistol"
PLAYER_SPRITE_SHEET = "assets/images/player/player_movement.png"
PLAYER_FRAME_WIDTH = 96
PLAYER_FRAME_HEIGHT = 96
PLAYER_RENDER_WIDTH = 64
PLAYER_RENDER_HEIGHT = 64
PLAYER_ANIMATION_SPEED = 0.12

WEAPON_STATS = {
    "Pistol": {
        "damage": 25,
        "fire_rate": 0.35,
        "bullet_speed": 500,
        "bullets_per_shot": 1,
        "spread": 0,
    },
    "Shotgun": {
        "damage": 14,
        "fire_rate": 0.8,
        "bullet_speed": 430,
        "bullets_per_shot": 5,
        "spread": 25,
    },
    "Auto Rifle": {
        "damage": 10,
        "fire_rate": 0.12,
        "bullet_speed": 520,
        "bullets_per_shot": 1,
        "spread": 6,
    },
}

MUMMY_STATS = {
    "normal": {
        "health": 60,
        "speed": 95,
        "damage": 15,
        "attack_cooldown": 0.8,
        "detection_radius": 260,
        "radius": 10,
        "score": 100,
    },
    "fast": {
        "health": 35,
        "speed": 145,
        "damage": 10,
        "attack_cooldown": 0.55,
        "detection_radius": 340,
        "radius": 9,
        "score": 160,
    },
}

MUMMY_ATTACK_RANGE = 34
MUMMY_SPRITE_SHEET = "assets/images/enemies/mummy_sprite_sheet.png"
MUMMY_SPRITE_WIDTH = 64
MUMMY_SPRITE_HEIGHT = 64
MUMMY_RENDER_SIZE = 48
NORMAL_MUMMY_ROW_START = 0
FAST_MUMMY_ROW_START = 2
ANIMATION_FRAME_COUNT = 2
ANIMATION_SPEED = 0.18

CHEST_INTERACTION_RADIUS = 34
KEY_INTERACTION_RADIUS = 34
EXIT_INTERACTION_RADIUS = 34
MEDKIT_HEAL = 35
SCORE_LOOT_VALUE = 250

LIGHT_RADIUS_TILES = 7
DARK_ROOM_DIM_FACTOR = 0.38
NORMAL_ROOM_DIM_FACTOR = 1.0

SPATIAL_HASH_CELL_SIZE = 72
