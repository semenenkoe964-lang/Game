from src.algorithms.bsp_generator import BSPGenerator
from src.algorithms.constraint_validator import ConstraintValidator
from src.core.settings import FLOOR_CONFIGS


def test_valid_floor_passes_validation():
    floor_map = BSPGenerator(seed=3).generate_valid_floor(FLOOR_CONFIGS[1])

    result = ConstraintValidator.validate(floor_map)

    assert result.is_valid, result.errors


def test_floor_without_key_fails_validation():
    floor_map = BSPGenerator(seed=4).generate_valid_floor(FLOOR_CONFIGS[1])
    floor_map.key_tile = None

    result = ConstraintValidator.validate(floor_map)

    assert not result.is_valid


def test_floor_without_exit_fails_validation():
    floor_map = BSPGenerator(seed=5).generate_valid_floor(FLOOR_CONFIGS[1])
    floor_map.exit_tile = None

    result = ConstraintValidator.validate(floor_map)

    assert not result.is_valid


def test_key_and_exit_are_reachable():
    floor_map = BSPGenerator(seed=6).generate_valid_floor(FLOOR_CONFIGS[1])
    reachable = floor_map.reachable_tiles_from(floor_map.start_tile)

    assert floor_map.key_tile in reachable
    assert floor_map.exit_tile in reachable


def test_key_must_not_be_inside_chest_list():
    floor_map = BSPGenerator(seed=11).generate_valid_floor(FLOOR_CONFIGS[1])
    floor_map.chest_tiles.append(floor_map.key_tile)

    result = ConstraintValidator.validate(floor_map)

    assert not result.is_valid


def test_key_must_not_overlap_exit():
    floor_map = BSPGenerator(seed=12).generate_valid_floor(FLOOR_CONFIGS[1])
    floor_map.key_tile = floor_map.exit_tile

    result = ConstraintValidator.validate(floor_map)

    assert not result.is_valid


def test_floor_without_chests_fails_validation():
    floor_map = BSPGenerator(seed=13).generate_valid_floor(FLOOR_CONFIGS[1])
    floor_map.chest_tiles.clear()

    result = ConstraintValidator.validate(floor_map)

    assert not result.is_valid
