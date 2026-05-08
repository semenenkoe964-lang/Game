import pygame

from src.core.settings import (
    ANIMATION_FRAME_COUNT,
    COLORS,
    FAST_MUMMY_ROW_START,
    FLOOR_TILESET,
    FLOOR_TILESET_COLUMNS,
    FLOOR_TILESET_ROWS,
    FONT_NAME,
    FONT_SIZE,
    MUMMY_RENDER_SIZE,
    MUMMY_SPRITE_HEIGHT,
    MUMMY_SPRITE_SHEET,
    MUMMY_SPRITE_WIDTH,
    NORMAL_MUMMY_ROW_START,
    PLAYER_FRAME_HEIGHT,
    PLAYER_FRAME_WIDTH,
    PLAYER_RENDER_HEIGHT,
    PLAYER_RENDER_WIDTH,
    PLAYER_SPRITE_SHEET,
    SIDE_WALL_SPRITE,
    TILE_SIZE,
    WALL_TILESET,
)
from src.models.mummy import DOWN, LEFT, RIGHT, UP
from src.models.player import (
    PLAYER_DOWN,
    PLAYER_DOWN_LEFT,
    PLAYER_DOWN_RIGHT,
    PLAYER_LEFT,
    PLAYER_RIGHT,
    PLAYER_UP,
    PLAYER_UP_LEFT,
    PLAYER_UP_RIGHT,
)
from src.views.tile_loader import FloorTileSet, WallTileSet
from src.views.sprite_loader import SpriteSheet


MUMMY_FRAME_COORDS = {
    DOWN: (2, 0),
    UP: (2, 1),
    RIGHT: (4, 0),
    LEFT: (6, 0),
}

PLAYER_DIRECTION_ROWS = {
    PLAYER_UP: 0,
    PLAYER_UP_RIGHT: 1,
    PLAYER_LEFT: 2,
    PLAYER_RIGHT: 3,
    PLAYER_DOWN_LEFT: 4,
    PLAYER_DOWN_RIGHT: 5,
    PLAYER_DOWN: 6,
    PLAYER_UP_LEFT: 7,
}


class ASCIIRenderer:
    def __init__(self):
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE, bold=True)
        self.floor_tiles = self._load_floor_tiles()
        self.wall_tiles = self._load_wall_tiles()
        self.mummy_sprites = self._load_mummy_sprites()
        self.player_sprites = self._load_player_sprites()

    def draw_world(self, screen, floor_map, camera, lighting, player, chests, mummies, bullets) -> None:
        self._draw_tiles(screen, floor_map, camera, lighting, player)
        self._draw_exit(screen, floor_map, camera, lighting, player)
        self._draw_key(screen, floor_map, camera, lighting, player)

        for chest in chests:
            if not chest.opened:
                self._draw_object(screen, floor_map, camera, lighting, player, chest.position, "C", COLORS["chest"])

        for bullet in bullets:
            self._draw_char_at_world(screen, camera, bullet.position, "*", COLORS["bullet"])

        for mummy in mummies:
            if mummy.alive:
                self._draw_mummy(screen, floor_map, camera, lighting, player, mummy)

        self._draw_player(screen, floor_map, camera, lighting, player)

    def _draw_tiles(self, screen, floor_map, camera, lighting, player) -> None:
        start_x, start_y, end_x, end_y = camera.visible_tile_bounds(floor_map)
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                visible, factor = lighting.tile_visibility(floor_map, x, y, player.position)
                if not visible:
                    continue

                if floor_map.is_wall(x, y):
                    if not self._is_wall_edge(floor_map, x, y):
                        continue
                    if self.wall_tiles is not None:
                        self._draw_wall_tile(screen, floor_map, camera, x, y, factor)
                    else:
                        color = lighting.apply_color(COLORS["wall"], factor)
                        self._draw_char_at_tile(screen, camera, x, y, "#", color)
                    continue

                if self.floor_tiles is not None:
                    self._draw_floor_tile(screen, floor_map, camera, x, y, factor)
                else:
                    symbol = floor_map.get_symbol(x, y)
                    base_color = COLORS["floor_alt"] if symbol in (",", "'", "`") else COLORS["floor"]
                    color = lighting.apply_color(base_color, factor)
                    self._draw_char_at_tile(screen, camera, x, y, symbol, color)

    def _draw_exit(self, screen, floor_map, camera, lighting, player) -> None:
        if floor_map.exit_tile is None:
            return
        symbol = "O" if player.has_key else "D"
        color = COLORS["exit_open"] if player.has_key else COLORS["exit_closed"]
        self._draw_object(
            screen,
            floor_map,
            camera,
            lighting,
            player,
            floor_map.tile_to_world(floor_map.exit_tile),
            symbol,
            color,
        )

    def _draw_key(self, screen, floor_map, camera, lighting, player) -> None:
        if player.has_key or floor_map.key_tile is None:
            return
        self._draw_object(
            screen,
            floor_map,
            camera,
            lighting,
            player,
            floor_map.tile_to_world(floor_map.key_tile),
            "K",
            COLORS["title"],
        )

    def _draw_object(self, screen, floor_map, camera, lighting, player, position, symbol: str, color) -> None:
        tile_x, tile_y = floor_map.world_to_tile(position)
        visible, factor = lighting.tile_visibility(floor_map, tile_x, tile_y, player.position)
        if visible:
            self._draw_char_at_world(screen, camera, position, symbol, lighting.apply_color(color, factor))

    def _draw_mummy(self, screen, floor_map, camera, lighting, player, mummy) -> None:
        tile_x, tile_y = floor_map.world_to_tile(mummy.position)
        visible, factor = lighting.tile_visibility(floor_map, tile_x, tile_y, player.position)
        if not visible:
            return

        sprite = self._get_mummy_sprite(mummy)
        if sprite is None:
            color_key = "fast_mummy" if mummy.symbol == "F" else "normal_mummy"
            self._draw_char_at_world(
                screen,
                camera,
                mummy.position,
                mummy.symbol,
                lighting.apply_color(COLORS[color_key], factor),
            )
            return

        if factor < 1.0:
            sprite = sprite.copy()
            dim_value = max(0, min(255, int(255 * factor)))
            sprite.fill((dim_value, dim_value, dim_value, 255), special_flags=pygame.BLEND_RGBA_MULT)

        rect = sprite.get_rect(center=camera.world_to_screen(mummy.position))
        screen.blit(sprite, rect)

    def _draw_player(self, screen, floor_map, camera, lighting, player) -> None:
        tile_x, tile_y = floor_map.world_to_tile(player.position)
        visible, factor = lighting.tile_visibility(floor_map, tile_x, tile_y, player.position)
        if not visible:
            return

        sprite = self._get_player_sprite(player)
        if sprite is None:
            self._draw_char_at_world(
                screen,
                camera,
                player.position,
                "@",
                lighting.apply_color(COLORS["player"], factor),
            )
            return

        if factor < 1.0:
            sprite = sprite.copy()
            dim_value = max(0, min(255, int(255 * factor)))
            sprite.fill((dim_value, dim_value, dim_value, 255), special_flags=pygame.BLEND_RGBA_MULT)

        rect = sprite.get_rect(center=camera.world_to_screen(player.position))
        screen.blit(sprite, rect)

    def _draw_floor_tile(self, screen, floor_map, camera, x: int, y: int, factor: float) -> None:
        assert self.floor_tiles is not None
        tile = self.floor_tiles.get_tile(floor_map.get_floor_tile_index(x, y))
        if factor < 1.0:
            tile = tile.copy()
            dim_value = max(0, min(255, int(255 * factor)))
            tile.fill((dim_value, dim_value, dim_value, 255), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(tile, (x * TILE_SIZE - camera.x, y * TILE_SIZE - camera.y))

    def _draw_wall_tile(self, screen, floor_map, camera, x: int, y: int, factor: float) -> None:
        assert self.wall_tiles is not None
        tile = self.wall_tiles.get_tile(self._wall_visual_kind(floor_map, x, y))
        base_color = (
            int(COLORS["wall"][0] * factor),
            int(COLORS["wall"][1] * factor),
            int(COLORS["wall"][2] * factor),
        )
        screen.fill(
            base_color,
            pygame.Rect(x * TILE_SIZE - camera.x, y * TILE_SIZE - camera.y, TILE_SIZE, TILE_SIZE),
        )
        if factor < 1.0:
            tile = tile.copy()
            dim_value = max(0, min(255, int(255 * factor)))
            tile.fill((dim_value, dim_value, dim_value, 255), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(tile, (x * TILE_SIZE - camera.x, y * TILE_SIZE - camera.y))

    def _wall_visual_kind(self, floor_map, x: int, y: int) -> str:
        touches_up_or_down = floor_map.is_floor(x, y - 1) or floor_map.is_floor(x, y + 1)
        touches_left_or_right = floor_map.is_floor(x - 1, y) or floor_map.is_floor(x + 1, y)

        if touches_up_or_down and touches_left_or_right:
            return "corner"
        if touches_left_or_right:
            return "perpendicular"
        if touches_up_or_down:
            return "straight"
        return "corner"

    def _is_wall_edge(self, floor_map, x: int, y: int) -> bool:
        if not floor_map.is_wall(x, y):
            return False
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if floor_map.is_floor(x + dx, y + dy):
                    return True
        return False

    def _load_floor_tiles(self) -> FloorTileSet | None:
        try:
            return FloorTileSet(
                FLOOR_TILESET,
                FLOOR_TILESET_COLUMNS,
                FLOOR_TILESET_ROWS,
                TILE_SIZE,
            )
        except (FileNotFoundError, pygame.error, ValueError):
            return None

    def _load_wall_tiles(self) -> WallTileSet | None:
        try:
            return WallTileSet(WALL_TILESET, TILE_SIZE, SIDE_WALL_SPRITE)
        except (FileNotFoundError, pygame.error, ValueError):
            return None

    def _load_mummy_sprites(self) -> dict | None:
        try:
            sheet = SpriteSheet(MUMMY_SPRITE_SHEET, MUMMY_SPRITE_WIDTH, MUMMY_SPRITE_HEIGHT)
            sprites = {}
            for mummy_type, row_start in (
                ("normal", NORMAL_MUMMY_ROW_START),
                ("fast", FAST_MUMMY_ROW_START),
            ):
                for direction, (start_col, row_offset) in MUMMY_FRAME_COORDS.items():
                    for frame_index in range(ANIMATION_FRAME_COUNT):
                        frame = sheet.get_frame(start_col + frame_index, row_start + row_offset)
                        frame = pygame.transform.scale(frame, (MUMMY_RENDER_SIZE, MUMMY_RENDER_SIZE))
                        sprites[(mummy_type, direction, frame_index)] = frame
            return sprites
        except (FileNotFoundError, pygame.error, ValueError):
            return None

    def _get_mummy_sprite(self, mummy) -> pygame.Surface | None:
        if self.mummy_sprites is None:
            return None
        mummy_type = "fast" if mummy.symbol == "F" else "normal"
        key = (mummy_type, mummy.direction, mummy.animation_frame)
        return self.mummy_sprites.get(key)

    def _load_player_sprites(self) -> dict | None:
        try:
            sheet = SpriteSheet(PLAYER_SPRITE_SHEET, PLAYER_FRAME_WIDTH, PLAYER_FRAME_HEIGHT)
            sprites = {}
            for direction, row in PLAYER_DIRECTION_ROWS.items():
                for frame_index in range(4):
                    frame = sheet.get_frame(frame_index, row)
                    frame = pygame.transform.scale(
                        frame,
                        (PLAYER_RENDER_WIDTH, PLAYER_RENDER_HEIGHT),
                    )
                    sprites[(direction, frame_index)] = frame
            return sprites
        except (FileNotFoundError, pygame.error, ValueError):
            return None

    def _get_player_sprite(self, player) -> pygame.Surface | None:
        if self.player_sprites is None:
            return None
        key = (player.sprite_direction, player.animation_frame)
        return self.player_sprites.get(key)

    def _draw_char_at_tile(self, screen, camera, x: int, y: int, symbol: str, color) -> None:
        world_position = ((x + 0.5) * TILE_SIZE, (y + 0.5) * TILE_SIZE)
        self._draw_char_at_world(screen, camera, world_position, symbol, color)

    def _draw_char_at_world(self, screen, camera, position, symbol: str, color) -> None:
        text = self.font.render(symbol, True, color)
        screen_x, screen_y = camera.world_to_screen(position)
        rect = text.get_rect(center=(screen_x, screen_y))
        screen.blit(text, rect)
