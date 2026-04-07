import random

import pygame

from src.core.settings import ANIMATION_FRAME_COUNT, ANIMATION_SPEED, MUMMY_STATS

DOWN = "down"
UP = "up"
LEFT = "left"
RIGHT = "right"


class Mummy:
    mummy_type = "normal"
    symbol = "M"

    def __init__(self, position: tuple[float, float]):
        stats = MUMMY_STATS[self.mummy_type]
        self.position = pygame.Vector2(position)
        self.health = stats["health"]
        self.speed = stats["speed"]
        self.damage = stats["damage"]
        self.attack_cooldown = stats["attack_cooldown"]
        self.detection_radius = stats["detection_radius"]
        self.radius = stats["radius"]
        self.score_value = stats["score"]
        self.attack_timer = 0.0
        self.wander_timer = 0.0
        self.wander_direction = pygame.Vector2(0, 0)
        self.direction = DOWN
        self.animation_timer = 0.0
        self.animation_frame = 0

    @property
    def alive(self) -> bool:
        return self.health > 0

    def take_damage(self, amount: int) -> None:
        self.health -= amount

    def update_timers(self, dt: float) -> None:
        self.attack_timer = max(0.0, self.attack_timer - dt)
        self.wander_timer = max(0.0, self.wander_timer - dt)

    def pick_wander_direction(self) -> pygame.Vector2:
        if self.wander_timer <= 0:
            self.wander_timer = random.uniform(0.8, 1.8)
            self.wander_direction = pygame.Vector2(
                random.uniform(-1, 1),
                random.uniform(-1, 1),
            )
            if self.wander_direction.length_squared():
                self.wander_direction = self.wander_direction.normalize()
        return self.wander_direction

    def update_animation(self, dt: float, movement_delta: pygame.Vector2) -> None:
        if movement_delta.length_squared() <= 0.01:
            self.animation_frame = 0
            self.animation_timer = 0.0
            return

        self.direction = self._direction_from_vector(movement_delta)
        self.animation_timer += dt
        if self.animation_timer >= ANIMATION_SPEED:
            self.animation_timer = 0.0
            self.animation_frame = (self.animation_frame + 1) % ANIMATION_FRAME_COUNT

    def _direction_from_vector(self, movement_delta: pygame.Vector2) -> str:
        if abs(movement_delta.x) > abs(movement_delta.y):
            return RIGHT if movement_delta.x > 0 else LEFT
        return DOWN if movement_delta.y > 0 else UP


class NormalMummy(Mummy):
    mummy_type = "normal"
    symbol = "M"


class FastMummy(Mummy):
    mummy_type = "fast"
    symbol = "F"
