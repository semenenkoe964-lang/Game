from collections import deque

from src.models.room import Room


class RoomGraph:
    def __init__(self, rooms: list[Room], edges: list[tuple[int, int]]):
        self.rooms = rooms
        self.edges = [(min(a, b), max(a, b)) for a, b in edges if a != b]
        self.adjacency: dict[int, set[int]] = {i: set() for i in range(len(rooms))}
        for a, b in self.edges:
            self.adjacency[a].add(b)
            self.adjacency[b].add(a)

    def distances_from(self, start_index: int) -> dict[int, int]:
        distances = {start_index: 0}
        queue = deque([start_index])
        while queue:
            current = queue.popleft()
            for neighbor in self.adjacency.get(current, set()):
                if neighbor not in distances:
                    distances[neighbor] = distances[current] + 1
                    queue.append(neighbor)
        return distances

    def farthest_room_from(self, start_index: int) -> int:
        distances = self.distances_from(start_index)
        return max(distances, key=lambda room_index: distances[room_index])

    def farthest_rooms_from(self, start_index: int) -> list[int]:
        distances = self.distances_from(start_index)
        return sorted(distances, key=lambda room_index: distances[room_index], reverse=True)

    def are_connected(self, start_index: int, end_index: int) -> bool:
        return end_index in self.distances_from(start_index)
