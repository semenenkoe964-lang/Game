from dataclasses import dataclass


@dataclass
class Room:
    x: int
    y: int
    width: int
    height: int
    is_dark: bool = False

    @property
    def center(self) -> tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)

    @property
    def right(self) -> int:
        return self.x + self.width - 1

    @property
    def bottom(self) -> int:
        return self.y + self.height - 1

    def contains_tile(self, tile_x: int, tile_y: int) -> bool:
        return self.x <= tile_x <= self.right and self.y <= tile_y <= self.bottom

    def inner_tiles(self) -> list[tuple[int, int]]:
        return [
            (x, y)
            for y in range(self.y + 1, self.bottom)
            for x in range(self.x + 1, self.right)
        ]
