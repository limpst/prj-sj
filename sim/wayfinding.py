"""5·6동 방문자 동선: Dijkstra 경로 계산 + 단일 오진입(misentry) 기대 도상길이 모형.

단위는 도상 px(평면도 위 길이)이며 m·초가 아니다. p·r 은 가정값이고 넛지 효과 예측이 아니다.
"""
from __future__ import annotations

import heapq
import math
from dataclasses import dataclass
from itertools import product
from typing import Iterable

PLANNED_ROUTES_PX = {
    ("B", "R6"): 48.0,
    ("B", "R5"): 303.5,
    ("S", "R5"): 234.9,
    ("P1", "R5"): 145.4,
    ("P2", "R6"): 163.3,
}

B_R5_L0_PX = 303.46
B_J_MISENTRY_BRANCH_PX = 30.02


@dataclass(frozen=True)
class Graph:
    nodes: dict[str, tuple[float, float]]
    edges: tuple[tuple[str, str], ...]

    def length(self, a: str, b: str) -> float:
        (x1, y1), (x2, y2) = self.nodes[a], self.nodes[b]
        return math.hypot(x2 - x1, y2 - y1)

    def adjacency(self) -> dict[str, list[tuple[str, float]]]:
        adj: dict[str, list[tuple[str, float]]] = {n: [] for n in self.nodes}
        for a, b in self.edges:
            w = self.length(a, b)
            adj[a].append((b, w))
            adj[b].append((a, w))
        return adj


def shortest_path(g: Graph, src: str, dst: str) -> tuple[float, list[str]]:
    adj = g.adjacency()
    dist = {src: 0.0}
    prev: dict[str, str] = {}
    pq = [(0.0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == dst:
            break
        if d > dist.get(u, math.inf):
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist.get(v, math.inf):
                dist[v], prev[v] = nd, u
                heapq.heappush(pq, (nd, v))
    if dst not in dist:
        raise ValueError(f"no path {src}->{dst}")
    path = [dst]
    while path[-1] != src:
        path.append(prev[path[-1]])
    return dist[dst], path[::-1]


def expected_length(l0: float, p: float, r: float, d: float) -> float:
    """E[L] = L0 + 2·p·r·d — 오진입 가지 d 를 r 만큼 갔다가 같은 길로 복귀."""
    if not (0 <= p <= 1 and 0 <= r <= 1):
        raise ValueError("p, r must be in [0, 1]")
    return l0 + 2 * p * r * d


def extra_length_table(
    ps: Iterable[float] = (0.10, 0.20, 0.30),
    rs: Iterable[float] = (0.25, 0.50, 1.00),
    d: float = B_J_MISENTRY_BRANCH_PX,
) -> dict[tuple[float, float], float]:
    return {(p, r): round(2 * p * r * d, 1) for p, r in product(ps, rs)}


if __name__ == "__main__":
    print("B->R5 extra px (rows p, cols r=0.25/0.50/1.00)")
    t = extra_length_table()
    for p in (0.10, 0.20, 0.30):
        print(f"p={p:.0%}", [t[(p, r)] for r in (0.25, 0.50, 1.00)])
