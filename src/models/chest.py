import pygame


class Chest:
    def __init__(self, position: tuple[float, float], content: str):
        self.position = pygame.Vector2(position)
        self.content = content
        self.opened = False
        self.radius = 12

    def open(self) -> str | None:
        if self.opened:
            return None
        self.opened = True
        return self.content
