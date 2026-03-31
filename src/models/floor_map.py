from collections import deque

from src.core.settings import TILE_SIZE
from src.models.room import Room


class FloorMap:
    """Tile map for one pyramid floor. Algorithms use tile coordinates."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tiles = [["#" for _ in range(width)] for _ in range(height)]
        self.floor_variants = [["." for _ in range(width)] for _ in range(height)]
        self.floor_tile_indices = [[0 for _ in range(width)] for _ in range(height)]

        self.rooms: list[Room] = []
        self.connections: list[tuple[int, int]] = []

        self.start_tile: tuple[int, int] | None = None
        self.exit_tile: tuple[int, int] | None = None
        self.key_tile: tuple[int, int] | None = None
        self.chest_tiles: list[tuple[int, int]] = []
        self.enemy_spawns: list[tuple[str, tuple[int, int]]] = []

        self.start_room_index: int | None = None
        self.exit_room_index: int | None = None
        self.key_room_index: int | None = None

    @property
    def pixel_width(self) -> int:
        return self.width * TILE_SIZE

    @property
    def pixel_height(self) -> int:
        return self.height * TILE_SIZE

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def is_floor(self, x: int, y: int) -> bool:
        return self.in_bounds(x, y) and self.tiles[y][x] == "."

    def is_wall(self, x: int, y: int) -> bool:
        return not self.in_bounds(x, y) or self.tiles[y][x] == "#"

    def set_floor(self, x: int, y: int) -> None:
        if self.in_bounds(x, y):
            self.tiles[y][x] = "."

    def get_symbol(self, x: int, y: int) -> str:
        if self.is_wall(x, y):
            return "#"
        return self.floor_variants[y][x]

    def get_floor_tile_index(self, x: int, y: int) -> int:
        return self.floor_tile_indices[y][x]

    def carve_room(self, room: Room) -> None:
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                self.set_floor(x, y)

    def carve_corridor(self, start: tuple[int, int], end: tuple[int, int]) -> None:
        x1, y1 = start
        x2, y2 = end
        if x1 <= x2:
            x_range = range(x1, x2 + 1)
        else:
            x_range = range(x2, x1 + 1)
        if y1 <= y2:
            y_range = range(y1, y2 + 1)
        else:
            y_range = range(y2, y1 + 1)

        for x in x_range:
            self._carve_wide(x, y1)
        for y in y_range:
            self._carve_wide(x2, y)

    def _carve_wide(self, cx: int, cy: int) -> None:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                self.set_floor(cx + dx, cy + dy)

    def tile_to_world(self, tile: tuple[int, int]) -> tuple[float, float]:
        x, y = tile
        return ((x + 0.5) * TILE_SIZE, (y + 0.5) * TILE_SIZE)

    def world_to_tile(self, position) -> tuple[int, int]:
        return (int(position[0] // TILE_SIZE), int(position[1] // TILE_SIZE))

    def room_index_at_tile(self, x: int, y: int) -> int | None:
        for index, room in enumerate(self.rooms):
            if room.contains_tile(x, y):
                return index
        return None

    def room_at_tile(self, x: int, y: int) -> Room | None:
        index = self.room_index_at_tile(x, y)
        if index is None:
            return None
        return self.rooms[index]

    def room_at_world(self, position) -> Room | None:
        x, y = self.world_to_tile(position)
        return self.room_at_tile(x, y)

    def is_area_walkable(self, position, radius: float) -> bool:
        left = int((position[0] - radius) // TILE_SIZE)
        right = int((position[0] + radius) // TILE_SIZE)
        top = int((position[1] - radius) // TILE_SIZE)
        bottom = int((position[1] + radius) // TILE_SIZE)
        for y in range(top, bottom + 1):
            for x in range(left, right + 1):
                if self.is_wall(x, y):
                    return False
        return True

    def segment_hits_wall(self, start, end, step: float = TILE_SIZE / 4) -> bool:
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = (dx * dx + dy * dy) ** 0.5
        steps = max(1, int(distance / step))
        for i in range(steps + 1):
            t = i / steps
            x = start[0] + dx * t
            y = start[1] + dy * t
            tile_x, tile_y = self.world_to_tile((x, y))
            if self.is_wall(tile_x, tile_y):
                return True
        return False

    def reachable_tiles_from(self, start_tile: tuple[int, int]) -> set[tuple[int, int]]:
        if not self.is_floor(*start_tile):
            return set()

        visited = {start_tile}
        queue = deque([start_tile])
        while queue:
            x, y = queue.popleft()
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if (nx, ny) not in visited and self.is_floor(nx, ny):
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        return visited
