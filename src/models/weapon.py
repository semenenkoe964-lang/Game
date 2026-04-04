import math
import random
from dataclasses import dataclass

import pygame

from src.core.settings import WEAPON_STATS
from src.models.bullet import Bullet


@dataclass
class Weapon:
    name: str
    damage: int
    fire_rate: float
    bullet_speed: float
    bullets_per_shot: int
    spread: float
    cooldown: float = 0.0

    @classmethod
    def from_name(cls, name: str) -> "Weapon":
        stats = WEAPON_STATS[name]
        return cls(
            name=name,
            damage=stats["damage"],
            fire_rate=stats["fire_rate"],
            bullet_speed=stats["bullet_speed"],
            bullets_per_shot=stats["bullets_per_shot"],
            spread=stats["spread"],
            cooldown=0.0,
        )

    def update(self, dt: float) -> None:
        self.cooldown = max(0.0, self.cooldown - dt)

    def can_fire(self) -> bool:
        return self.cooldown <= 0.0

    def fire(self, position: pygame.Vector2, direction: pygame.Vector2) -> list[Bullet]:
        if not self.can_fire():
            return []

        self.cooldown = self.fire_rate
        direction = direction.normalize() if direction.length_squared() else pygame.Vector2(1, 0)
        base_angle = math.atan2(direction.y, direction.x)

        bullets = []
        if self.bullets_per_shot == 1:
            angles = [base_angle + math.radians(random.uniform(-self.spread, self.spread))]
        else:
            start_angle = base_angle - math.radians(self.spread) / 2
            step = math.radians(self.spread) / max(1, self.bullets_per_shot - 1)
            angles = [start_angle + step * i for i in range(self.bullets_per_shot)]

        for angle in angles:
            velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * self.bullet_speed
            bullets.append(Bullet(position.copy(), velocity, self.damage))
        return bullets
