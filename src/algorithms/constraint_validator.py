from dataclasses import dataclass

from src.algorithms.room_graph import RoomGraph
from src.models.floor_map import FloorMap


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str]


class ConstraintValidator:
    @staticmethod
    def validate(floor_map: FloorMap) -> ValidationResult:
        errors: list[str] = []

        if floor_map.start_tile is None:
            errors.append("start tile is missing")
        if floor_map.exit_tile is None:
            errors.append("exit tile is missing")
        if floor_map.key_tile is None:
            errors.append("key tile is missing")
        if errors:
            return ValidationResult(False, errors)

        assert floor_map.start_tile is not None
        assert floor_map.exit_tile is not None
        assert floor_map.key_tile is not None

        if not floor_map.is_floor(*floor_map.start_tile):
            errors.append("start must be placed on floor")
        if not floor_map.is_floor(*floor_map.exit_tile):
            errors.append("exit must be placed on floor")
        if not floor_map.is_floor(*floor_map.key_tile):
            errors.append("key must be placed on floor")

        if floor_map.key_tile in floor_map.chest_tiles:
            errors.append("key must not be placed inside a chest")
        if floor_map.key_tile == floor_map.start_tile:
            errors.append("key must not overlap the start")
        if floor_map.key_tile == floor_map.exit_tile:
            errors.append("key must not overlap the exit")
        if not floor_map.chest_tiles:
            errors.append("floor must contain at least one chest")

        for chest_tile in floor_map.chest_tiles:
            if not floor_map.is_floor(*chest_tile):
                errors.append("all chests must be placed on floor")

        reachable = floor_map.reachable_tiles_from(floor_map.start_tile)
        if floor_map.key_tile not in reachable:
            errors.append("key is not reachable from start")
        if floor_map.exit_tile not in reachable:
            errors.append("exit is not reachable from start")

        graph = RoomGraph(floor_map.rooms, floor_map.connections)
        if (
            floor_map.start_room_index is not None
            and floor_map.exit_room_index is not None
            and floor_map.start_room_index == floor_map.exit_room_index
        ):
            errors.append("exit must not be in the start room")
        if (
            floor_map.start_room_index is not None
            and floor_map.key_room_index is not None
            and floor_map.start_room_index == floor_map.key_room_index
        ):
            errors.append("key must not be in the start room")

        if (
            len(floor_map.rooms) >= 4
            and floor_map.start_room_index is not None
            and floor_map.exit_room_index is not None
        ):
            distances = graph.distances_from(floor_map.start_room_index)
            if distances.get(floor_map.exit_room_index, 0) < 2:
                errors.append("exit should not be close to the start room")
            if (
                floor_map.key_room_index is not None
                and distances.get(floor_map.key_room_index, 0) < 2
            ):
                errors.append("key should not be close to the start room")

        start_x, start_y = floor_map.start_tile
        for enemy_type, enemy_tile in floor_map.enemy_spawns:
            if not floor_map.is_floor(*enemy_tile):
                errors.append(f"{enemy_type} mummy spawn must be on floor")
            distance = abs(enemy_tile[0] - start_x) + abs(enemy_tile[1] - start_y)
            if distance < 8:
                errors.append("enemies must not spawn near the player")

        return ValidationResult(not errors, errors)

    @staticmethod
    def is_valid(floor_map: FloorMap) -> bool:
        return ConstraintValidator.validate(floor_map).is_valid
