from src.algorithms.bsp_generator import BSPGenerator
from src.algorithms.room_graph import RoomGraph
from src.core.settings import FLOOR_CONFIGS


def test_room_graph_is_created():
    floor_map = BSPGenerator(seed=7).generate_valid_floor(FLOOR_CONFIGS[1])
    graph = RoomGraph(floor_map.rooms, floor_map.connections)

    assert len(graph.adjacency) == len(floor_map.rooms)
    assert len(graph.edges) > 0


def test_can_find_farthest_room():
    floor_map = BSPGenerator(seed=8).generate_valid_floor(FLOOR_CONFIGS[1])
    graph = RoomGraph(floor_map.rooms, floor_map.connections)

    farthest = graph.farthest_room_from(floor_map.start_room_index)

    assert farthest in range(len(floor_map.rooms))
    assert farthest != floor_map.start_room_index


def test_exit_is_not_start_room():
    floor_map = BSPGenerator(seed=9).generate_valid_floor(FLOOR_CONFIGS[1])

    assert floor_map.exit_room_index != floor_map.start_room_index
