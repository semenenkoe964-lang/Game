import pygame

from src.core.scene_manager import SceneManager
from src.core.settings import COLORS, FPS, WINDOW_HEIGHT, WINDOW_WIDTH
from src.scenes.menu_scene import MenuScene


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pyramid Escape")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.scene_manager = SceneManager()
        self.scene_manager.set_scene(MenuScene(self.scene_manager))
        self.running = True

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            self.scene_manager.handle_events(events)
            self.scene_manager.update(dt)

            self.screen.fill(COLORS["background"])
            self.scene_manager.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
