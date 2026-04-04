import pygame


class Bullet:
    def __init__(self, position: pygame.Vector2, velocity: pygame.Vector2, damage: int):
        self.position = position
        self.previous_position = position.copy()
        self.velocity = velocity
        self.damage = damage
        self.radius = 4
        self.lifetime = 1.6
        self.alive = True

    def update(self, dt: float) -> None:
        self.previous_position = self.position.copy()
        self.position += self.velocity * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
