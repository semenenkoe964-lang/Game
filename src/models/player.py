import pygame

from src.core.settings import (
    PLAYER_ANIMATION_SPEED,
    PLAYER_MAX_HEALTH,
    PLAYER_RADIUS,
    PLAYER_SPEED,
)
from src.models.weapon import Weapon

PLAYER_UP = "up"
PLAYER_UP_RIGHT = "up_right"
PLAYER_LEFT = "left"
PLAYER_RIGHT = "right"
PLAYER_DOWN_LEFT = "down_left"
PLAYER_DOWN_RIGHT = "down_right"
PLAYER_DOWN = "down"
PLAYER_UP_LEFT = "up_left"


class Player:
    def __init__(self, position: tuple[float, float]):
        self.position = pygame.Vector2(position)
        self.radius = PLAYER_RADIUS
        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.speed = PLAYER_SPEED
        self.weapons = [Weapon.from_name("Pistol")]
        self.current_weapon_index = 0
        self.has_key = False
        self.last_direction = pygame.Vector2(1, 0)
        self.score = 0
        self.sprite_direction = PLAYER_DOWN
        self.animation_timer = 0.0
        self.animation_frame = 0

    @property
    def current_weapon(self) -> Weapon:
        return self.weapons[self.current_weapon_index]

    def update_weapons(self, dt: float) -> None:
        for weapon in self.weapons:
            weapon.update(dt)

    def set_position(self, position: tuple[float, float]) -> None:
        self.position.update(position)

    def switch_weapon(self) -> None:
        if self.weapons:
            self.current_weapon_index = (self.current_weapon_index + 1) % len(self.weapons)

    def add_weapon(self, weapon_name: str) -> None:
        existing_names = [weapon.name for weapon in self.weapons]
        if weapon_name not in existing_names:
            self.weapons.append(Weapon.from_name(weapon_name))
        self.current_weapon_index = [weapon.name for weapon in self.weapons].index(weapon_name)

    def heal(self, amount: int) -> None:
        self.health = min(self.max_health, self.health + amount)

    def take_damage(self, amount: int) -> None:
        self.health = max(0, self.health - amount)

    def update_animation(self, dt: float, movement_delta: pygame.Vector2) -> None:
        if movement_delta.length_squared() <= 0.01:
            self.animation_frame = 0
            self.animation_timer = 0.0
            return

        self.sprite_direction = self._direction_from_vector(movement_delta)
        if self.animation_frame == 0:
            self.animation_frame = 1

        self.animation_timer += dt
        if self.animation_timer >= PLAYER_ANIMATION_SPEED:
            self.animation_timer = 0.0
            self.animation_frame += 1
            if self.animation_frame > 3:
                self.animation_frame = 1

    def _direction_from_vector(self, movement_delta: pygame.Vector2) -> str:
        dx = movement_delta.x
        dy = movement_delta.y
        if abs(dx) > 0.01 and abs(dy) > 0.01:
            if dx > 0 and dy < 0:
                return PLAYER_UP_RIGHT
            if dx < 0 and dy < 0:
                return PLAYER_UP_LEFT
            if dx > 0 and dy > 0:
                return PLAYER_DOWN_RIGHT
            return PLAYER_DOWN_LEFT
        if abs(dx) > abs(dy):
            return PLAYER_RIGHT if dx > 0 else PLAYER_LEFT
        return PLAYER_DOWN if dy > 0 else PLAYER_UP

    def reset_for_new_game(self, position: tuple[float, float]) -> None:
        self.__init__(position)
