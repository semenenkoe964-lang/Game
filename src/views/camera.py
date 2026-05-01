from src.core.settings import TILE_SIZE, WINDOW_HEIGHT, WINDOW_WIDTH


class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0

    def follow(self, target_position, floor_map) -> None:
        self.x = int(target_position[0] - WINDOW_WIDTH / 2)
        self.y = int(target_position[1] - WINDOW_HEIGHT / 2)
        max_x = max(0, floor_map.pixel_width - WINDOW_WIDTH)
        max_y = max(0, floor_map.pixel_height - WINDOW_HEIGHT)
        self.x = max(0, min(self.x, max_x))
        self.y = max(0, min(self.y, max_y))

    def world_to_screen(self, position) -> tuple[int, int]:
        return (int(position[0] - self.x), int(position[1] - self.y))

    def screen_to_world(self, position) -> tuple[int, int]:
        return (int(position[0] + self.x), int(position[1] + self.y))

    def visible_tile_bounds(self, floor_map) -> tuple[int, int, int, int]:
        start_x = max(0, self.x // TILE_SIZE - 1)
        start_y = max(0, self.y // TILE_SIZE - 1)
        end_x = min(floor_map.width, (self.x + WINDOW_WIDTH) // TILE_SIZE + 2)
        end_y = min(floor_map.height, (self.y + WINDOW_HEIGHT) // TILE_SIZE + 2)
        return start_x, start_y, end_x, end_y
