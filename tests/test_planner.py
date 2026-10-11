from app.planner import astar, bfs, dijkstra
GRID = [[0,0,0,0],[1,1,0,1],[0,0,0,0],[0,1,1,0]]

def assert_valid(path, start, goal):
    assert path and path[0] == start and path[-1] == goal
    for (r,c),(nr,nc) in zip(path,path[1:]): assert abs(r-nr)+abs(c-nc)==1 and GRID[nr][nc]==0

def test_astar_valid_path():
    path, explored = astar(GRID,(0,0),(3,3)); assert_valid(path,(0,0),(3,3)); assert explored>0

def test_bfs_valid_path():
    path, explored = bfs(GRID,(0,0),(3,3)); assert_valid(path,(0,0),(3,3)); assert explored>0

def test_dijkstra_valid_path():
    path, explored = dijkstra(GRID,(0,0),(3,3)); assert_valid(path,(0,0),(3,3)); assert explored>0

def test_all_algorithms_find_equal_shortest_distance():
    paths=[fn(GRID,(0,0),(3,3))[0] for fn in (astar,bfs,dijkstra)]
    assert len({len(p) for p in paths})==1

def test_blocked_goal_is_unreachable():
    assert astar([[0,1],[0,1]],(0,0),(0,1))[0] == []
