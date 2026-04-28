import random

from src.core.settings import MEDKIT_HEAL, SCORE_LOOT_VALUE
from src.models.chest import Chest


class LootSystem:
    REGULAR_LOOT_WEIGHTS = {
        "medkit": 50,
        "weapon_pistol": 12,
        "weapon_shotgun": 12,
        "weapon_auto": 11,
        "score": 15,
    }

    WEAPON_CONTENT_TO_NAME = {
        "weapon_pistol": "Pistol",
        "weapon_shotgun": "Shotgun",
        "weapon_auto": "Auto Rifle",
    }

    @classmethod
    def choose_regular_loot(cls) -> str:
        values = list(cls.REGULAR_LOOT_WEIGHTS)
        weights = [cls.REGULAR_LOOT_WEIGHTS[value] for value in values]
        return random.choices(values, weights=weights, k=1)[0]

    @classmethod
    def create_chests_for_floor(cls, floor_map) -> list[Chest]:
        chests = []
        for tile in floor_map.chest_tiles:
            position = floor_map.tile_to_world(tile)
            chests.append(Chest(position, cls.choose_regular_loot()))
        return chests

    @classmethod
    def apply_loot(cls, player, content: str | None) -> str:
        if content is None:
            return ""
        if content == "medkit":
            player.heal(MEDKIT_HEAL)
            return "Used a medkit"
        if content in cls.WEAPON_CONTENT_TO_NAME:
            player.add_weapon(cls.WEAPON_CONTENT_TO_NAME[content])
            return f"Found {cls.WEAPON_CONTENT_TO_NAME[content]}"
        if content == "score":
            player.score += SCORE_LOOT_VALUE
            return f"+{SCORE_LOOT_VALUE} score"
        return ""
