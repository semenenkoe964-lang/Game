import pygame


class SpriteSheet:
    def __init__(self, path: str, frame_width: int, frame_height: int):
        self.image = pygame.image.load(path).convert_alpha()
        self.frame_width = frame_width
        self.frame_height = frame_height

    def get_frame(self, col: int, row: int) -> pygame.Surface:
        rect = pygame.Rect(
            col * self.frame_width,
            row * self.frame_height,
            self.frame_width,
            self.frame_height,
        )
        return self.image.subsurface(rect).copy()
