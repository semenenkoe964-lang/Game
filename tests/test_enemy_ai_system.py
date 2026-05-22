from src.models.mummy import NormalMummy
from src.models.player import Player
from src.systems.enemy_ai_system import EnemyAISystem


def test_mummy_deals_damage_when_in_attack_range():
    player = Player((100, 100))
    mummy = NormalMummy((130, 100))
    ai = EnemyAISystem()

    ai.update([mummy], player, floor_map=None, dt=0.1)

    assert player.health == player.max_health - mummy.damage
