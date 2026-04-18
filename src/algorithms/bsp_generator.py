from dataclasses import dataclass
import random

from src.algorithms.constraint_validator import ConstraintValidator
from src.algorithms.perlin_noise import (
    ValueNoise,
    floor_symbol_from_noise,
    floor_tile_index_from_noise,
)
from src.algorithms.room_graph import RoomGraph
from src.core.settings import FLOOR_TILESET_TILE_COUNT
from src.models.floor_map import FloorMap
from src.models.room import Room


@dataclass
class BSPNode:
    x: int
    y: int
    width: int
    height: int
    left: "BSPNode | None" = None
    right: "BSPNode | None" = None
    room_index: int | None = None

    @property
    def area(self) -> int:
        return self.width * self.height

    def is_leaf(self) -> bool:
        return self.left is None and self.right is None


class BSPGenerator:
    def __init__(self, seed: int | None = None):
        self.rng = random.Random(seed)
        self.seed = seed if seed is not None else self.rng.randint(1, 999_999)
        self.min_leaf_size = 14
        self.min_room_size = 6

    def generate_valid_floor(self, config: dict, max_attempts: int = 50) -> FloorMap:
        last_errors: list[str] = []
        for _ in range(max_attempts):
            floor_map = self.generate(config)
            result = ConstraintValidator.validate(floor_map)
            if result.is_valid:
                return floor_map
            last_errors = result.errors
        raise RuntimeError(f"Could not generate valid floor: {', '.join(last_errors)}")

    def generate(self, config: dict) -> FloorMap:
        width = config["map_width"]
        height = config["map_height"]
        target_rooms = config["rooms"]

        floor_map = FloorMap(width, height)
        root = BSPNode(1, 1, width - 2, height - 2)
        leaves = self._split_until_target(root, target_rooms)
        self._create_rooms(floor_map, leaves)
        self._connect_tree(floor_map, root)
        self._decorate_floor(floor_map)
        self._choose_important_rooms(floor_map, config)
        self._place_key(floor_map)
        self._place_chests(floor_map, config["chests"])
        self._place_enemies(floor_map, config)
        return floor_map

    def _split_until_target(self, root: BSPNode, target_rooms: int) -> list[BSPNode]:
        leaves = [root]
        while len(leaves) < target_rooms:
            candidates = [leaf for leaf in leaves if self._can_split(leaf)]
            if not candidates:
                break
            leaf = max(candidates, key=lambda node: node.area)
            if not self._split(leaf):
                break
            leaves.remove(leaf)
            assert leaf.left is not None and leaf.right is not None
            leaves.extend([leaf.left, leaf.right])
        return leaves

    def _can_split(self, node: BSPNode) -> bool:
        return node.width >= self.min_leaf_size * 2 or node.height >= self.min_leaf_size * 2

    def _split(self, node: BSPNode) -> bool:
        split_vertical = self.rng.choice([True, False])
        if node.width / max(1, node.height) > 1.25:
            split_vertical = True
        elif node.height / max(1, node.width) > 1.25:
            split_vertical = False

        if split_vertical:
            if node.width < self.min_leaf_size * 2:
                return False
            split = self.rng.randint(self.min_leaf_size, node.width - self.min_leaf_size)
            node.left = BSPNode(node.x, node.y, split, node.height)
            node.right = BSPNode(node.x + split, node.y, node.width - split, node.height)
        else:
            if node.height < self.min_leaf_size * 2:
                return False
            split = self.rng.randint(self.min_leaf_size, node.height - self.min_leaf_size)
            node.left = BSPNode(node.x, node.y, node.width, split)
            node.right = BSPNode(node.x, node.y + split, node.width, node.height - split)
        return True

    def _create_rooms(self, floor_map: FloorMap, leaves: list[BSPNode]) -> None:
        for leaf in leaves:
            max_width = max(self.min_room_size, leaf.width - 3)
            max_height = max(self.min_room_size, leaf.height - 3)
            room_width = self.rng.randint(self.min_room_size, max_width)
            room_height = self.rng.randint(self.min_room_size, max_height)
            room_x = self.rng.randint(leaf.x + 1, leaf.x + leaf.width - room_width - 1)
            room_y = self.rng.randint(leaf.y + 1, leaf.y + leaf.height - room_height - 1)
            room = Room(room_x, room_y, room_width, room_height)
            leaf.room_index = len(floor_map.rooms)
            floor_map.rooms.append(room)
            floor_map.carve_room(room)

    def _connect_tree(self, floor_map: FloorMap, node: BSPNode) -> int:
        if node.is_leaf():
            assert node.room_index is not None
            return node.room_index

        assert node.left is not None and node.right is not None
        left_room = self._connect_tree(floor_map, node.left)
        right_room = self._connect_tree(floor_map, node.right)
        start = floor_map.rooms[left_room].center
        end = floor_map.rooms[right_room].center

        if self.rng.random() < 0.5:
            corner = (end[0], start[1])
            floor_map.carve_corridor(start, corner)
            floor_map.carve_corridor(corner, end)
        else:
            corner = (start[0], end[1])
            floor_map.carve_corridor(start, corner)
            floor_map.carve_corridor(corner, end)

        edge = (min(left_room, right_room), max(left_room, right_room))
        if edge not in floor_map.connections:
            floor_map.connections.append(edge)

        return self.rng.choice([left_room, right_room])

    def _decorate_floor(self, floor_map: FloorMap) -> None:
        noise = ValueNoise(self.seed)
        for y in range(floor_map.height):
            for x in range(floor_map.width):
                if floor_map.is_floor(x, y):
                    value = noise.noise(x * 0.22, y * 0.22)
                    floor_map.floor_variants[y][x] = floor_symbol_from_noise(value)
                    floor_map.floor_tile_indices[y][x] = floor_tile_index_from_noise(
                        value,
                        FLOOR_TILESET_TILE_COUNT,
                    )

    def _choose_important_rooms(self, floor_map: FloorMap, config: dict) -> None:
        graph = RoomGraph(floor_map.rooms, floor_map.connections)
        first_endpoint = graph.farthest_room_from(0)
        second_endpoint = graph.farthest_room_from(first_endpoint)

        floor_map.start_room_index = first_endpoint
        floor_map.exit_room_index = second_endpoint
        floor_map.start_tile = floor_map.rooms[first_endpoint].center
        floor_map.exit_tile = floor_map.rooms[second_endpoint].center

        farthest = graph.farthest_rooms_from(first_endpoint)
        key_candidates = [
            room_index
            for room_index in farthest
            if room_index not in (first_endpoint, second_endpoint)
        ]
        floor_map.key_room_index = key_candidates[0] if key_candidates else second_endpoint

        for index, room in enumerate(floor_map.rooms):
            room.is_dark = self.rng.random() < config["dark_room_chance"]
            if index == floor_map.start_room_index:
                room.is_dark = False

    def _place_chests(self, floor_map: FloorMap, chest_count: int) -> None:
        chest_count = max(1, chest_count)
        used_tiles = {floor_map.key_tile, floor_map.start_tile, floor_map.exit_tile}
        room_indices = [
            index
            for index in range(len(floor_map.rooms))
            if index != floor_map.start_room_index
        ]
        attempts = 0
        while len(floor_map.chest_tiles) < chest_count and attempts < 200:
            attempts += 1
            room_index = self.rng.choice(room_indices)
            tile = self._random_tile_in_room(floor_map, room_index)
            if tile not in used_tiles:
                used_tiles.add(tile)
                floor_map.chest_tiles.append(tile)

        if len(floor_map.chest_tiles) >= chest_count:
            return

        for room_index in room_indices:
            room = floor_map.rooms[room_index]
            for y in range(room.y + 1, room.bottom):
                for x in range(room.x + 1, room.right):
                    tile = (x, y)
                    if floor_map.is_floor(*tile) and tile not in used_tiles:
                        used_tiles.add(tile)
                        floor_map.chest_tiles.append(tile)
                        if len(floor_map.chest_tiles) >= chest_count:
                            return

    def _place_key(self, floor_map: FloorMap) -> None:
        assert floor_map.key_room_index is not None
        blocked_tiles = {floor_map.start_tile, floor_map.exit_tile}
        for _ in range(100):
            key_tile = self._random_tile_in_room(floor_map, floor_map.key_room_index)
            if key_tile not in blocked_tiles:
                floor_map.key_tile = key_tile
                return
        room = floor_map.rooms[floor_map.key_room_index]
        for y in range(room.y + 1, room.bottom):
            for x in range(room.x + 1, room.right):
                key_tile = (x, y)
                if floor_map.is_floor(*key_tile) and key_tile not in blocked_tiles:
                    floor_map.key_tile = key_tile
                    return
        floor_map.key_tile = room.center

    def _place_enemies(self, floor_map: FloorMap, config: dict) -> None:
        spawn_types = ["normal"] * config["normal_mummies"] + ["fast"] * config["fast_mummies"]
        room_indices = [
            index
            for index in range(len(floor_map.rooms))
            if index != floor_map.start_room_index
        ]
        used_tiles = set(floor_map.chest_tiles)
        if floor_map.key_tile:
            used_tiles.add(floor_map.key_tile)
        if floor_map.exit_tile:
            used_tiles.add(floor_map.exit_tile)

        for enemy_type in spawn_types:
            for _ in range(100):
                room_index = self.rng.choice(room_indices)
                tile = self._random_tile_in_room(floor_map, room_index)
                if tile in used_tiles:
                    continue
                assert floor_map.start_tile is not None
                distance = abs(tile[0] - floor_map.start_tile[0]) + abs(tile[1] - floor_map.start_tile[1])
                if distance >= 8:
                    floor_map.enemy_spawns.append((enemy_type, tile))
                    used_tiles.add(tile)
                    break

    def _random_tile_in_room(self, floor_map: FloorMap, room_index: int) -> tuple[int, int]:
        room = floor_map.rooms[room_index]
        for _ in range(50):
            tile = (
                self.rng.randint(room.x + 1, room.right - 1),
                self.rng.randint(room.y + 1, room.bottom - 1),
            )
            if floor_map.is_floor(*tile):
                return tile
        return room.center
