import math
import random


def _smoothstep(t: float) -> float:
    return t * t * (3 - 2 * t)


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


class ValueNoise:
    """Small deterministic value-noise generator for floor decoration."""

    def __init__(self, seed: int = 0):
        self.seed = seed
        self.cache: dict[tuple[int, int], float] = {}

    def _value_at_grid_point(self, x: int, y: int) -> float:
        key = (x, y)
        if key not in self.cache:
            rng = random.Random((x * 73856093) ^ (y * 19349663) ^ self.seed)
            self.cache[key] = rng.random()
        return self.cache[key]

    def noise(self, x: float, y: float) -> float:
        x0 = math.floor(x)
        y0 = math.floor(y)
        x1 = x0 + 1
        y1 = y0 + 1

        sx = _smoothstep(x - x0)
        sy = _smoothstep(y - y0)

        n00 = self._value_at_grid_point(x0, y0)
        n10 = self._value_at_grid_point(x1, y0)
        n01 = self._value_at_grid_point(x0, y1)
        n11 = self._value_at_grid_point(x1, y1)

        top = _lerp(n00, n10, sx)
        bottom = _lerp(n01, n11, sx)
        return _lerp(top, bottom, sy)


def floor_symbol_from_noise(value: float) -> str:
    if value < 0.25:
        return ","
    if value < 0.42:
        return "`"
    if value < 0.58:
        return "'"
    return "."


def floor_tile_index_from_noise(value: float, tile_count: int = 25) -> int:
    index = int(value * tile_count)
    return max(0, min(tile_count - 1, index))
