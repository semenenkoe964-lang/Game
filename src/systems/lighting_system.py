import pygame

from src.core.settings import (
    DARK_ROOM_DIM_FACTOR,
    LIGHT_RADIUS_TILES,
    NORMAL_ROOM_DIM_FACTOR,
    TILE_SIZE,
)


class LightingSystem:
    def __init__(self):
        self.light_radius_pixels = LIGHT_RADIUS_TILES * TILE_SIZE

    def tile_visibility(self, floor_map, tile_x: int, tile_y: int, player_position) -> tuple[bool, float]:
        tile_world = floor_map.tile_to_world((tile_x, tile_y))
        distance = pygame.Vector2(tile_world).distance_to(player_position)
        player_room = floor_map.room_at_world(player_position)
        tile_room = floor_map.room_at_tile(tile_x, tile_y)

        if player_room is not None and player_room.is_dark and distance > self.light_radius_pixels:
            return False, 0.0

        if tile_room is not None and tile_room.is_dark:
            if distance <= self.light_radius_pixels:
                return True, NORMAL_ROOM_DIM_FACTOR
            return True, DARK_ROOM_DIM_FACTOR

        return True, NORMAL_ROOM_DIM_FACTOR

    def apply_color(self, color, factor: float) -> tuple[int, int, int]:
        return (
            max(0, min(255, int(color[0] * factor))),
            max(0, min(255, int(color[1] * factor))),
            max(0, min(255, int(color[2] * factor))),
        )

    def draw_overlay(self, screen, camera, player, floor_map) -> None:
        player_room = floor_map.room_at_world(player.position)
        if player_room is not None and player_room.is_dark:
            multiplier = 135
        else:
            multiplier = 245

        overlay = pygame.Surface(screen.get_size()).convert_alpha()
        overlay.fill((multiplier, multiplier, multiplier, 255))
        light_center = camera.world_to_screen(player.position)
        pygame.draw.circle(overlay, (255, 255, 255, 255), light_center, self.light_radius_pixels)
        screen.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
