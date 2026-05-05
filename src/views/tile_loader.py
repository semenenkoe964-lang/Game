import pygame


class FloorTileSet:
    """Loads one visual floor tileset. All loaded tiles remain logical FLOOR."""

    def __init__(self, path: str, columns: int, rows: int, render_size: int):
        self.image = pygame.image.load(path).convert_alpha()
        self.columns = columns
        self.rows = rows
        self.render_size = render_size
        self.tiles = self._load_tiles()

    def get_tile(self, index: int) -> pygame.Surface:
        return self.tiles[index % len(self.tiles)]

    def _load_tiles(self) -> list[pygame.Surface]:
        source_width, source_height = self.image.get_size()
        tiles = []
        for row in range(self.rows):
            for col in range(self.columns):
                left = round(col * source_width / self.columns)
                right = round((col + 1) * source_width / self.columns)
                top = round(row * source_height / self.rows)
                bottom = round((row + 1) * source_height / self.rows)
                cell = self.image.subsurface(
                    pygame.Rect(left, top, right - left, bottom - top)
                ).copy()
                tile = self._crop_tile_from_cell(cell)
                tile = pygame.transform.scale(tile, (self.render_size, self.render_size))
                tile = self._remove_edge_strips(tile)
                tiles.append(tile)
        return tiles

    def _crop_tile_from_cell(self, cell: pygame.Surface) -> pygame.Surface:
        width, height = cell.get_size()
        tile_pixels = []
        for y in range(height):
            for x in range(width):
                r, g, b, alpha = cell.get_at((x, y))
                brightness = (r + g + b) / 3
                if alpha > 0 and brightness > 55:
                    tile_pixels.append((x, y))

        if not tile_pixels:
            return cell

        min_x = max(0, min(x for x, _ in tile_pixels))
        max_x = min(width - 1, max(x for x, _ in tile_pixels))
        min_y = max(0, min(y for _, y in tile_pixels))
        max_y = min(height - 1, max(y for _, y in tile_pixels))

        # The source image has a dark gap and drop shadow around every tile.
        # Crop slightly inside the detected tile so those black edges do not repeat in-game.
        crop_width = max_x - min_x + 1
        crop_height = max_y - min_y + 1
        inset_x = max(6, int(crop_width * 0.20))
        inset_y = max(6, int(crop_height * 0.20))
        min_x = min(max_x, min_x + inset_x)
        max_x = max(min_x, max_x - inset_x)
        min_y = min(max_y, min_y + inset_y)
        max_y = max(min_y, max_y - inset_y)

        return cell.subsurface(
            pygame.Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
        ).copy()

    def _remove_edge_strips(self, tile: pygame.Surface) -> pygame.Surface:
        tile = tile.copy()
        width, height = tile.get_size()
        border = max(1, self.render_size // 24)

        for y in range(border):
            for x in range(width):
                tile.set_at((x, y), tile.get_at((x, border)))
                tile.set_at((x, height - 1 - y), tile.get_at((x, height - 1 - border)))

        for x in range(border):
            for y in range(height):
                tile.set_at((x, y), tile.get_at((border, y)))
                tile.set_at((width - 1 - x, y), tile.get_at((width - 1 - border, y)))

        return tile


class WallTileSet:
    """Loads three simple wall sprites: straight, perpendicular, and corner."""

    def __init__(self, path: str, render_size: int, side_wall_path: str | None = None):
        self.image = pygame.image.load(path).convert_alpha()
        self.render_size = render_size
        self.rows = self._load_rows()
        self.tiles = [tile for row in self.rows for tile in row]
        self.straight_wall_tile = self._tile_at(0, 0)
        self.perpendicular_wall_tile = self._tile_at(0, 2)
        if side_wall_path is not None:
            self.perpendicular_wall_tile = self._load_side_wall_tile(side_wall_path)
        self.corner_wall_tile = self._tile_at(1, 0)

    def get_tile(self, wall_kind: str) -> pygame.Surface:
        if wall_kind == "corner":
            return self.corner_wall_tile
        if wall_kind == "perpendicular":
            return self.perpendicular_wall_tile
        return self.straight_wall_tile

    def _load_rows(self) -> list[list[pygame.Surface]]:
        mask = self._foreground_mask()
        row_segments = self._segments(
            [sum(mask[y]) for y in range(self.image.get_height())],
            threshold=100,
            merge_gap=20,
            min_length=20,
        )

        rows = []
        for y1, y2 in row_segments:
            column_counts = [
                sum(1 for y in range(y1, y2 + 1) if mask[y][x])
                for x in range(self.image.get_width())
            ]
            column_segments = self._segments(
                column_counts,
                threshold=8,
                merge_gap=12,
                min_length=12,
            )
            row_tiles = [
                self._make_tile_from_bounds(x1, y1, x2, y2)
                for x1, x2 in column_segments
            ]
            if row_tiles:
                rows.append(row_tiles)
        return rows

    def _foreground_mask(self) -> list[list[bool]]:
        width, height = self.image.get_size()
        mask = [[False for _ in range(width)] for _ in range(height)]
        for y in range(height):
            for x in range(width):
                r, g, b, alpha = self.image.get_at((x, y))
                brightness = (r + g + b) / 3
                if alpha > 0 and brightness > 50:
                    mask[y][x] = True
        return mask

    def _make_tile_from_bounds(self, x1: int, y1: int, x2: int, y2: int) -> pygame.Surface:
        padding = 2
        left = max(0, x1 - padding)
        top = max(0, y1 - padding)
        right = min(self.image.get_width() - 1, x2 + padding)
        bottom = min(self.image.get_height() - 1, y2 + padding)
        crop = self.image.subsurface(
            pygame.Rect(left, top, right - left + 1, bottom - top + 1)
        ).copy()
        crop = self._remove_dark_background(crop)
        return pygame.transform.scale(crop, (self.render_size, self.render_size))

    def _remove_dark_background(self, tile: pygame.Surface) -> pygame.Surface:
        tile = tile.copy()
        width, height = tile.get_size()
        for y in range(height):
            for x in range(width):
                r, g, b, alpha = tile.get_at((x, y))
                brightness = (r + g + b) / 3
                if alpha > 0 and brightness < 38:
                    tile.set_at((x, y), (r, g, b, 0))
        return tile

    def _segments(
        self,
        counts: list[int],
        threshold: int,
        merge_gap: int,
        min_length: int,
    ) -> list[tuple[int, int]]:
        raw = []
        start = None
        for index, count in enumerate(counts):
            if count > threshold and start is None:
                start = index
            elif count <= threshold and start is not None:
                if index - start >= min_length:
                    raw.append([start, index - 1])
                start = None
        if start is not None and len(counts) - start >= min_length:
            raw.append([start, len(counts) - 1])

        merged = []
        for segment in raw:
            if merged and segment[0] - merged[-1][1] <= merge_gap:
                merged[-1][1] = segment[1]
            else:
                merged.append(segment)
        return [(start, end) for start, end in merged]

    def _tile_at(self, row: int, col: int) -> pygame.Surface:
        if row < len(self.rows) and col < len(self.rows[row]):
            return self.rows[row][col]
        if self.tiles:
            return self.tiles[0]
        fallback = pygame.Surface((self.render_size, self.render_size), pygame.SRCALPHA)
        fallback.fill((128, 100, 70, 255))
        return fallback

    def _load_side_wall_tile(self, path: str) -> pygame.Surface:
        image = pygame.image.load(path).convert_alpha()
        width, height = image.get_size()
        pixels = []
        for y in range(height):
            for x in range(width):
                r, g, b, alpha = image.get_at((x, y))
                brightness = (r + g + b) / 3
                if alpha > 0 and brightness > 50:
                    pixels.append((x, y))

        if not pixels:
            return self.perpendicular_wall_tile

        min_x = max(0, min(x for x, _ in pixels) - 2)
        max_x = min(width - 1, max(x for x, _ in pixels) + 2)
        min_y = max(0, min(y for _, y in pixels) - 2)
        max_y = min(height - 1, max(y for _, y in pixels) + 2)

        sprite_width = max_x - min_x + 1
        center_y = (min_y + max_y) // 2
        half_size = sprite_width // 2
        crop_top = max(min_y, center_y - half_size)
        crop_bottom = min(max_y, crop_top + sprite_width - 1)
        crop_top = max(min_y, crop_bottom - sprite_width + 1)

        crop = image.subsurface(
            pygame.Rect(min_x, crop_top, sprite_width, crop_bottom - crop_top + 1)
        ).copy()
        crop = self._remove_dark_background(crop)
        return pygame.transform.scale(crop, (self.render_size, self.render_size))
