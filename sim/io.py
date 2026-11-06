"""계획선 CSV 로더 — 28점·27구간 데이터 → Graph.

data/points.csv : id,x,y,kind
data/edges.csv  : a,b

파일이 없으면 FileNotFoundError. 테스트에서 data/ 없을 때 pytest.mark.skipif 로 건너뜀.
"""
from __future__ import annotations

import csv
from pathlib import Path

from sim.wayfinding import Graph

_VALID_KINDS = frozenset(
    {"origin", "junction", "reception", "waypoint", "staff_only", "internal"}
)


def data_available(data_dir: str | Path = "data") -> bool:
    """data/ 디렉터리와 두 CSV 파일이 모두 있으면 True."""
    d = Path(data_dir)
    return (d / "points.csv").exists() and (d / "edges.csv").exists()


def load_graph(data_dir: str | Path = "data") -> Graph:
    """CSV 두 파일을 읽어 Graph 를 반환한다.

    Raises
    ------
    FileNotFoundError
        파일이 없을 때.
    ValueError
        필수 열 누락, 알 수 없는 kind, 중복 엣지, 미등록 노드 참조,
        트리 구조 위반(사이클·비연결).
    """
    d = Path(data_dir)
    nodes = _read_points(d / "points.csv")
    edges, edge_set = _read_edges(d / "edges.csv", nodes)
    _assert_tree(nodes, edge_set)
    return Graph(nodes=nodes, edges=tuple(edges))


# ── 내부 함수 ─────────────────────────────────────────────────────────────────

def _read_points(path: Path) -> dict[str, tuple[float, float]]:
    if not path.exists():
        raise FileNotFoundError(f"points.csv 없음: {path}")
    nodes: dict[str, tuple[float, float]] = {}
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        _require_fields(reader, {"id", "x", "y", "kind"}, "points.csv")
        for row in reader:
            nid = row["id"].strip()
            kind = row["kind"].strip()
            if kind not in _VALID_KINDS:
                raise ValueError(f"알 수 없는 kind '{kind}' (노드 {nid})")
            nodes[nid] = (float(row["x"]), float(row["y"]))
    if not nodes:
        raise ValueError("points.csv 에 데이터가 없음")
    return nodes


def _read_edges(
    path: Path,
    nodes: dict[str, tuple[float, float]],
) -> tuple[list[tuple[str, str]], set[frozenset[str]]]:
    if not path.exists():
        raise FileNotFoundError(f"edges.csv 없음: {path}")
    edges: list[tuple[str, str]] = []
    edge_set: set[frozenset[str]] = set()
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        _require_fields(reader, {"a", "b"}, "edges.csv")
        for row in reader:
            a, b = row["a"].strip(), row["b"].strip()
            for n in (a, b):
                if n not in nodes:
                    raise ValueError(f"엣지 참조 미등록 노드: '{n}'")
            key = frozenset({a, b})
            if key in edge_set:
                raise ValueError(f"중복 엣지: {a}—{b}")
            edge_set.add(key)
            edges.append((a, b))
    return edges, edge_set


def _assert_tree(
    nodes: dict[str, tuple[float, float]],
    edge_set: set[frozenset[str]],
) -> None:
    """V-1 개 엣지 + 연결 그래프 = 트리."""
    n, e = len(nodes), len(edge_set)
    if e != n - 1:
        raise ValueError(
            f"트리 구조 위반: 노드 {n}개에 엣지 {e}개 (트리는 {n - 1}개 필요)"
        )
    # BFS 연결 확인
    adj: dict[str, set[str]] = {k: set() for k in nodes}
    for fs in edge_set:
        a, b = tuple(fs)
        adj[a].add(b)
        adj[b].add(a)
    start = next(iter(nodes))
    visited: set[str] = set()
    queue = [start]
    while queue:
        cur = queue.pop()
        if cur in visited:
            continue
        visited.add(cur)
        queue.extend(adj[cur] - visited)
    if visited != set(nodes):
        raise ValueError(f"연결되지 않은 노드: {set(nodes) - visited}")


def _require_fields(reader: csv.DictReader, required: set[str], fname: str) -> None:
    if reader.fieldnames is None or not required.issubset(reader.fieldnames):
        raise ValueError(f"{fname} 필수 열 누락 (필요: {required})")


if __name__ == "__main__":
    import sys

    data_dir = sys.argv[1] if len(sys.argv) > 1 else "data"
    if not data_available(data_dir):
        print(f"[skip] {data_dir}/points.csv 또는 edges.csv 없음")
        sys.exit(0)
    g = load_graph(data_dir)
    print(f"노드 {len(g.nodes)}개, 엣지 {len(g.edges)}개 로드 완료")
    for nid, (x, y) in list(g.nodes.items())[:5]:
        print(f"  {nid}: ({x}, {y})")
