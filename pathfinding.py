from vector import Vector2
from heapq import heappush, heappop
from world.world import World, Zone
from typing import List


# manhatten formula
def _pathfinding_heuristic(p1: Vector2, p2: Vector2) -> float:
    return abs(p1.x - p2.x) + abs(p1.y - p2.y)


# get all neighbors nearby point
def _pathfinding_get_neighbors(world: World, point: Vector2, inaccuracy=5) -> List[Vector2]:
    potential_neighbors = [
        Vector2(point.x + inaccuracy, point.y),
        Vector2(point.x + inaccuracy, point.y + inaccuracy),
        Vector2(point.x,              point.y + inaccuracy),
        Vector2(point.x - inaccuracy, point.y + inaccuracy),
        Vector2(point.x - inaccuracy, point.y),
        Vector2(point.x - inaccuracy, point.y - inaccuracy),
        Vector2(point.x,              point.y - inaccuracy),
        Vector2(point.x + inaccuracy, point.y - inaccuracy),
    ]
    # neighbors = []
    # for pn in potential_neighbors:
    #     if _pathfinding_cast_ray(world, point, pn, True) is pn:
    #         neighbors.append(pn)
    # return neighbors
    return potential_neighbors


# check if we're inside of the neighborhood
def _pathfinding_is_in_neighborhood(zone: Zone, point: Vector2) -> bool:
    if zone is None or point is None:
        return False
    if point in zone:
        return True
    for neighbor in zone.get_neighbors():
        if point in neighbor:
            return True
    return False


# cast a ray and check if we collide with a wall or outside of the world
def _pathfinding_cast_ray(world: World, start: Vector2, goal: Vector2, stop_at_goal=False, inaccuracy=1) -> Vector2:
    step = (goal - start).normalize()
    current = start.clone()

    while True:
        current += step
        # zone = world.get_zone_containing_point(current)

        # check if ray is connected or within game world
        # if current not in world or not _pathfinding_is_in_neighborhood(zone, current):
        if current not in world:
            return current

        if stop_at_goal:
            distance = current.distance(goal)
            if distance < inaccuracy:
                return goal


def a_star_pathfind(world: World, start: Vector2, goal: Vector2) -> List[Vector2]:
    if start not in world or goal not in world:
        print("err: start or goal not in world")
        return []

    open_nodes = []
    closed_nodes = set()
    g_score = {start: 0}
    parent = {start: start}

    heappush(open_nodes, (_pathfinding_heuristic(start, goal), start))

    while open_nodes:
        _, current = heappop(open_nodes)

        # we're at the goal!
        if current.distance(goal) < 10:
            path = []
            while current is not start and current in parent:
                path.append(current)
                current = parent[current]
            return path

        # add to closed to prevent recounting
        closed_nodes.add(current)

        # current_zone = world.get_zone_containing_point(current)
        for neighbor in _pathfinding_get_neighbors(world, current):
            if neighbor not in closed_nodes:
                # if not _pathfinding_is_in_neighborhood(current_zone, neighbor):
                #     continue

                g_current = g_score[current] + current.distance(neighbor)
                g_old = g_score.get(neighbor, 0)

                # new path!
                if g_current < g_old or neighbor not in [_[1] for _ in open_nodes]:
                    # update vertex and insert to open_nodes
                    parent[neighbor] = current
                    g_score[neighbor] = g_current
                    f_score = g_current + _pathfinding_heuristic(neighbor, goal)
                    heappush(open_nodes, (f_score, neighbor))

                # if _pathfinding_cast_ray(world, parent[current], neighbor, True) is neighbor:
                #     g_parent_score = g_score[parent[current]] + parent[current].distance(neighbor)
                #     if g_parent_score < g_old or neighbor not in [_[1] for _ in open_nodes]:
                #         parent[neighbor] = parent[current]
                #         g_score[neighbor] = g_parent_score
                #         f_score = g_parent_score + _pathfinding_heuristic(neighbor, goal)
                #         heappush(open_nodes, (f_score, neighbor))
                # else:
                #     if g_current < g_old or neighbor not in [_[1] for _ in open_nodes]:
                #         parent[neighbor] = current
                #         g_score[neighbor] = g_current
                #         f_score = g_current + _pathfinding_heuristic(neighbor, goal)
                #         heappush(open_nodes, (f_score, neighbor))

    print("err: no path found")
    return []
