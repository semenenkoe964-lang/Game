import pygame

from src.core.settings import COLORS
from src.views.ui_renderer import UIRenderer


class PauseScene:
    def __init__(self, scene_manager, game_scene):
        pygame.mouse.set_visible(True)
        self.scene_manager = scene_manager
        self.game_scene = game_scene
        self.ui = UIRenderer()

    def handle_events(self, events) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                pygame.mouse.set_visible(False)
                self.scene_manager.set_scene(self.game_scene)

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen) -> None:
        self.game_scene.draw(screen)
        overlay = pygame.Surface(screen.get_size()).convert_alpha()
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        title = self.ui.big_font.render("PAUSE", True, COLORS["title"])
        title_rect = title.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 30))
        screen.blit(title, title_rect)
        hint = self.ui.font.render("ESC or ENTER - Continue", True, COLORS["ui"])
        hint_rect = hint.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 30))
        screen.blit(hint, hint_rect)
