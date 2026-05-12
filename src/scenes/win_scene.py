import pygame

from src.views.ui_renderer import UIRenderer


class WinScene:
    def __init__(self, scene_manager, final_score: int):
        pygame.mouse.set_visible(True)
        self.scene_manager = scene_manager
        self.final_score = final_score
        self.ui = UIRenderer()

    def handle_events(self, events) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                from src.scenes.game_scene import GameScene

                self.scene_manager.set_scene(GameScene(self.scene_manager, floor_number=1))

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen) -> None:
        self.ui.draw_centered_text(
            screen,
            "ESCAPED",
            [
                "You survived all 3 floors.",
                f"Score: {self.final_score}",
                "ENTER - New Run",
            ],
        )
