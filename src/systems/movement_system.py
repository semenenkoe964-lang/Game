import pygame


class MovementSystem:
    @staticmethod
    def move_with_collisions(entity, direction: pygame.Vector2, dt: float, floor_map) -> None:
        if direction.length_squared() == 0:
            return

        direction = direction.normalize()
        movement = direction * entity.speed * dt

        next_x = pygame.Vector2(entity.position.x + movement.x, entity.position.y)
        if floor_map.is_area_walkable(next_x, entity.radius):
            entity.position.x = next_x.x

        next_y = pygame.Vector2(entity.position.x, entity.position.y + movement.y)
        if floor_map.is_area_walkable(next_y, entity.radius):
            entity.position.y = next_y.y
