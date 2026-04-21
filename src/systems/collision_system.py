import pygame


def circle_overlap(pos_a, radius_a: float, pos_b, radius_b: float) -> bool:
    delta = pygame.Vector2(pos_a) - pygame.Vector2(pos_b)
    return delta.length_squared() <= (radius_a + radius_b) ** 2


def segment_intersects_circle(start, end, center, radius: float) -> bool:
    start = pygame.Vector2(start)
    end = pygame.Vector2(end)
    center = pygame.Vector2(center)
    segment = end - start
    if segment.length_squared() == 0:
        return (center - start).length_squared() <= radius * radius

    t = max(0.0, min(1.0, (center - start).dot(segment) / segment.length_squared()))
    closest = start + segment * t
    return (center - closest).length_squared() <= radius * radius
