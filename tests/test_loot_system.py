from src.algorithms.bsp_generator import BSPGenerator
from src.core.settings import FLOOR_CONFIGS
from src.models.player import Player
from src.systems.loot_system import LootSystem


def test_weighted_random_returns_allowed_values():
    allowed = set(LootSystem.REGULAR_LOOT_WEIGHTS)

    for _ in range(50):
        assert LootSystem.choose_regular_loot() in allowed


def test_floor_chests_do_not_contain_key():
    for seed in range(20):
        floor_map = BSPGenerator(seed=seed).generate_valid_floor(FLOOR_CONFIGS[1])
        chests = LootSystem.create_chests_for_floor(floor_map)

        assert all(chest.content != "key" for chest in chests)


def test_key_is_separate_from_chests():
    floor_map = BSPGenerator(seed=21).generate_valid_floor(FLOOR_CONFIGS[1])

    assert floor_map.key_tile is not None
    assert floor_map.key_tile not in floor_map.chest_tiles


def test_medkit_does_not_heal_above_max_health():
    player = Player((10, 10))
    player.health = player.max_health - 5

    LootSystem.apply_loot(player, "medkit")

    assert player.health == player.max_health
