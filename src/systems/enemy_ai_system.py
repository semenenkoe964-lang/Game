import pygame

from src.models.mummy import FastMummy
from src.systems.movement_system import MovementSystem
from src.systems.spatial_hash import SpatialHash
from src.core.settings import MUMMY_ATTACK_RANGE, SPATIAL_HASH_CELL_SIZE


class EnemyAISystem:
    def __init__(self):
        self.enemy_grid = SpatialHash(SPATIAL_HASH_CELL_SIZE)
        self.attack_range = MUMMY_ATTACK_RANGE
        self.separation_radius = 48
        self.separation_strength = 1.4

    def update(self, mummies, player, floor_map, dt: float) -> None:
        alive_mummies = [mummy for mummy in mummies if mummy.alive]
        self.enemy_grid.build(alive_mummies)
        for mummy in alive_mummies:
            mummy.update_timers(dt)
            self._run_behavior_tree(mummy, player, floor_map, dt)

    def _run_behavior_tree(self, mummy, player, floor_map, dt: float) -> None:
        distance_to_player = mummy.position.distance_to(player.position)

        # Selector node: attack, chase, or wander depending on mummy type.
        if distance_to_player <= self.attack_range:
            self._attack(mummy, player)
            mummy.update_animation(dt, pygame.Vector2(0, 0))
            return

        if isinstance(mummy, FastMummy):
            self._chase(mummy, player, floor_map, dt)
            return

        if distance_to_player <= mummy.detection_radius:
            self._chase(mummy, player, floor_map, dt)
        else:
            self._wander(mummy, floor_map, dt)

    def _attack(self, mummy, player) -> None:
        if mummy.attack_timer <= 0:
            player.take_damage(mummy.damage)
            mummy.attack_timer = mummy.attack_cooldown

    def _chase(self, mummy, player, floor_map, dt: float) -> None:
        direction = player.position - mummy.position
        if direction.length_squared():
            direction = direction.normalize()
        direction += self._separation_vector(mummy)
        self._move_mummy(mummy, direction, floor_map, dt)

    def _wander(self, mummy, floor_map, dt: float) -> None:
        self._move_mummy(mummy, mummy.pick_wander_direction(), floor_map, dt)

    def _move_mummy(self, mummy, direction: pygame.Vector2, floor_map, dt: float) -> None:
        old_position = mummy.position.copy()
        MovementSystem.move_with_collisions(mummy, direction, dt, floor_map)
        mummy.update_animation(dt, mummy.position - old_position)

    def _separation_vector(self, mummy) -> pygame.Vector2:
        separation = pygame.Vector2(0, 0)
        for other in self.enemy_grid.query_radius(mummy.position, self.separation_radius):
            if other is mummy:
                continue
            offset = mummy.position - other.position
            distance = offset.length()
            if 0 < distance < self.separation_radius:
                separation += offset.normalize() * ((self.separation_radius - distance) / self.separation_radius)
        return separation * self.separation_strength
