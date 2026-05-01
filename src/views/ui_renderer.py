import pygame

from src.core.settings import COLORS, FONT_NAME


class UIRenderer:
    def __init__(self):
        self.font = pygame.font.SysFont(FONT_NAME, 20, bold=True)
        self.big_font = pygame.font.SysFont(FONT_NAME, 46, bold=True)
        self.small_font = pygame.font.SysFont(FONT_NAME, 18)

    def draw_game_ui(self, screen, player, floor_number: int, max_floors: int, message: str = "") -> None:
        lines = [
            f"HP: {player.health}",
            f"Floor: {floor_number}/{max_floors}",
            f"Weapon: {player.current_weapon.name}",
            f"Key: {'Yes' if player.has_key else 'No'}",
            f"Score: {player.score}",
        ]
        x = 12
        y = 10
        for line in lines:
            image = self.font.render(line, True, COLORS["ui"])
            screen.blit(image, (x, y))
            y += 23
        if message:
            image = self.small_font.render(message, True, COLORS["title"])
            screen.blit(image, (12, y + 6))

    def draw_crosshair(self, screen, position) -> None:
        x, y = int(position[0]), int(position[1])
        color = COLORS["bullet"]
        pygame.draw.line(screen, color, (x - 8, y), (x - 3, y), 2)
        pygame.draw.line(screen, color, (x + 3, y), (x + 8, y), 2)
        pygame.draw.line(screen, color, (x, y - 8), (x, y - 3), 2)
        pygame.draw.line(screen, color, (x, y + 3), (x, y + 8), 2)
        pygame.draw.circle(screen, color, (x, y), 2, 1)

    def draw_centered_text(self, screen, title: str, lines: list[str]) -> None:
        screen.fill(COLORS["background"])
        title_image = self.big_font.render(title, True, COLORS["title"])
        title_rect = title_image.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 80))
        screen.blit(title_image, title_rect)

        y = screen.get_height() // 2
        for line in lines:
            color = COLORS["ui"] if line else COLORS["muted_ui"]
            image = self.font.render(line, True, color)
            rect = image.get_rect(center=(screen.get_width() // 2, y))
            screen.blit(image, rect)
            y += 34
