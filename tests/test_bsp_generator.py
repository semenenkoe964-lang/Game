from src.algorithms.bsp_generator import BSPGenerator
from src.core.settings import FLOOR_CONFIGS, FLOOR_TILESET_TILE_COUNT


def test_bsp_generator_creates_rooms():
    floor_map = BSPGenerator(seed=1).generate_valid_floor(FLOOR_CONFIGS[1])

    assert len(floor_map.rooms) > 0
    for room in floor_map.rooms:
        assert 0 <= room.x < floor_map.width
        assert 0 <= room.y < floor_map.height
        assert room.right < floor_map.width
        assert room.bottom < floor_map.height


def test_start_exit_and_chests_are_on_floor():
    floor_map = BSPGenerator(seed=2).generate_valid_floor(FLOOR_CONFIGS[1])

    assert floor_map.start_tile is not None
    assert floor_map.exit_tile is not None
    assert floor_map.key_tile is not None
    assert floor_map.is_floor(*floor_map.start_tile)
    assert floor_map.is_floor(*floor_map.exit_tile)
    assert floor_map.is_floor(*floor_map.key_tile)
    assert floor_map.key_tile not in floor_map.chest_tiles
    assert len(floor_map.chest_tiles) >= 1
    assert all(floor_map.is_floor(*tile) for tile in floor_map.chest_tiles)


def test_floor_visual_tile_indices_do_not_change_floor_logic():
    floor_map = BSPGenerator(seed=10).generate_valid_floor(FLOOR_CONFIGS[1])

    for y in range(floor_map.height):
        for x in range(floor_map.width):
            if floor_map.is_floor(x, y):
                assert 0 <= floor_map.get_floor_tile_index(x, y) < FLOOR_TILESET_TILE_COUNT
