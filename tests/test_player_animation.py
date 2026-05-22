import pygame

from src.models.player import PLAYER_RIGHT, Player


def test_player_animation_uses_movement_direction():
    player = Player((100, 100))

    player.update_animation(0.13, pygame.Vector2(10, 0))

    assert player.sprite_direction == PLAYER_RIGHT
    assert player.animation_frame in (1, 2, 3)


def test_player_animation_returns_to_idle_when_stopped():
    player = Player((100, 100))
    player.update_animation(0.13, pygame.Vector2(10, 0))

    player.update_animation(0.13, pygame.Vector2(0, 0))

    assert player.animation_frame == 0
