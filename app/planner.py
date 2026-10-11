"""Four-directional grid path-planning algorithms. 1 = obstacle, 0 = free."""
from collections import deque
from heapq import heappop, heappush
from itertools import count
from time import perf_counter
Cell = tuple[int, int]


def _valid(grid, cell):
    r, c = cell
    return 0 <= r < len(grid) and 0 <= c < len(grid[0]) and grid[r][c] == 0


def _neighbors(grid, cell):
    r, c = cell
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nxt = (r + dr, c + dc)
        if _valid(grid, nxt):
            yield nxt


def _reconstruct(parent, goal):
    path, node = [], goal
    while node is not None:
        path.append(node)
        node = parent[node]
    return list(reversed(path))


def bfs(grid, start, goal):
    if not grid or not grid[0] or not _valid(grid, start) or not _valid(grid, goal): return [], 0
    queue, parent, explored = deque([start]), {start: None}, 0
    while queue:
        cur = queue.popleft(); explored += 1
        if cur == goal: return _reconstruct(parent, goal), explored
        for nxt in _neighbors(grid, cur):
            if nxt not in parent: parent[nxt] = cur; queue.append(nxt)
    return [], explored


def _best_first(grid, start, goal, heuristic):
    if not grid or not grid[0] or not _valid(grid, start) or not _valid(grid, goal): return [], 0
    seq = count(); frontier = [(heuristic(start), next(seq), start)]
    parent, cost, explored = {start: None}, {start: 0}, 0
    while frontier:
        _, _, cur = heappop(frontier); explored += 1
        if cur == goal: return _reconstruct(parent, goal), explored
        for nxt in _neighbors(grid, cur):
            new_cost = cost[cur] + 1
            if new_cost < cost.get(nxt, 10**12):
                cost[nxt], parent[nxt] = new_cost, cur
                heappush(frontier, (new_cost + heuristic(nxt), next(seq), nxt))
    return [], explored


def dijkstra(grid, start, goal):
    return _best_first(grid, start, goal, lambda _cell: 0)


def astar(grid, start, goal):
    return _best_first(grid, start, goal, lambda cell: abs(cell[0]-goal[0]) + abs(cell[1]-goal[1]))


def compare_algorithms():
    grid = [[0,0,0,0,0,0,0,0],[0,1,1,1,0,1,1,0],[0,0,0,1,0,0,0,0],[1,1,0,1,0,1,1,0],[0,0,0,0,0,0,0,0],[0,1,1,1,1,1,1,0],[0,0,0,0,0,0,0,0]]
    start, goal = (0,0), (6,7); results = {}
    for name, algo in (("A*", astar), ("BFS", bfs), ("Dijkstra", dijkstra)):
        begin = perf_counter(); path, explored = algo(grid, start, goal)
        results[name] = {"path": [list(x) for x in path], "path_length": max(0,len(path)-1), "nodes_explored": explored, "execution_time_ms": round((perf_counter()-begin)*1000,4), "reachable": bool(path)}
    return {"grid": grid, "start": list(start), "goal": list(goal), "results": results}
