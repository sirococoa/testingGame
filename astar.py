from heapq import heappush, heappop


def h(p, x):
    return abs(p[0] - x[0]) + abs(p[1] - x[1])

def a_star(stage, enemy, player):
    cand = [(h(player, enemy), None, enemy)]
    route = {}
    width = len(stage[0])
    height = len(stage)
    while cand:
        d, p, u = heappop(cand)
        if u in route:
            continue
        route[u] = p
        if u == player:
            return d - h(player, player), route
        for mx, my in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            if 0 <= u[0] + mx <= width and 0 <= u[1] + my <= height:
                if stage[u[0] + mx][u[1] + my] == 1:
                    w = 1 + h(player, u) - h(player, (u[0] + mx, u[1] + my))
                    heappush(cand, (d + w, u, (u[0] + mx, u[1] + my)))
    return float('inf'), None