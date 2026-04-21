from collections import defaultdict
import math


class SpatialHash:
    def __init__(self, cell_size: int):
        self.cell_size = cell_size
        self.cells: dict[tuple[int, int], list[object]] = defaultdict(list)

    def clear(self) -> None:
        self.cells.clear()

    def _cell_for_position(self, position) -> tuple[int, int]:
        return (int(position[0] // self.cell_size), int(position[1] // self.cell_size))

    def insert(self, obj) -> None:
        self.cells[self._cell_for_position(obj.position)].append(obj)

    def build(self, objects: list[object]) -> None:
        self.clear()
        for obj in objects:
            self.insert(obj)

    def query_radius(self, position, radius: float) -> list[object]:
        center_x, center_y = self._cell_for_position(position)
        cell_radius = math.ceil(radius / self.cell_size)
        result = []
        for y in range(center_y - cell_radius, center_y + cell_radius + 1):
            for x in range(center_x - cell_radius, center_x + cell_radius + 1):
                result.extend(self.cells.get((x, y), []))
        return result
