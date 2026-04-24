from src.core.settings import SPATIAL_HASH_CELL_SIZE
from src.systems.collision_system import segment_intersects_circle
from src.systems.spatial_hash import SpatialHash


class CombatSystem:
    def __init__(self):
        self.enemy_grid = SpatialHash(SPATIAL_HASH_CELL_SIZE)

    def fire_player_weapon(self, player, direction=None) -> list:
        fire_direction = direction if direction is not None else player.last_direction
        return player.current_weapon.fire(player.position, fire_direction)

    def update_bullets(self, bullets, mummies, floor_map, player, dt: float) -> list:
        self.enemy_grid.build([mummy for mummy in mummies if mummy.alive])
        alive_bullets = []

        for bullet in bullets:
            bullet.update(dt)
            if not bullet.alive:
                continue

            if floor_map.segment_hits_wall(bullet.previous_position, bullet.position):
                continue

            hit_mummy = self._find_hit_mummy(bullet, mummies)
            if hit_mummy is not None:
                hit_mummy.take_damage(bullet.damage)
                if not hit_mummy.alive:
                    player.score += hit_mummy.score_value
                continue

            alive_bullets.append(bullet)

        return alive_bullets

    def _find_hit_mummy(self, bullet, mummies):
        segment_middle = (bullet.previous_position + bullet.position) * 0.5
        query_radius = bullet.previous_position.distance_to(bullet.position) * 0.5 + 80
        nearby = self.enemy_grid.query_radius(segment_middle, query_radius)
        for mummy in nearby:
            if not mummy.alive:
                continue
            if segment_intersects_circle(
                bullet.previous_position,
                bullet.position,
                mummy.position,
                mummy.radius,
            ):
                return mummy
        return None
