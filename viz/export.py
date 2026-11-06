"""sim → viz/routes.json 내보내기.

실제 좌표(data/)가 있으면 그것을, 없으면 합성 좌표를 쓴다.
공개 저장소용 출력에는 실제 평면도 이미지를 포함하지 않는다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from sim.io import data_available, load_graph
from sim.wayfinding import (
    ASSUMPTION_NOTICE,
    B_J_MISENTRY_BRANCH_PX,
    Graph,
    shortest_path,
)

# 도착 수단별 색 + 목적 동 숫자 (색만으로 구분하지 않기 위해 숫자·문자 병기)
ORIGIN_STYLE = {
    "B": {"mode": "BRT", "color": "#1f6feb"},
    "S": {"mode": "BUS", "color": "#2da44e"},
    "P1": {"mode": "CAR", "color": "#d97706"},
    "P2": {"mode": "CAR", "color": "#d97706"},
}
DEST_BUILDING = {"R5": "5", "R6": "6"}


def synthetic_graph() -> Graph:
    """합성 좌표 (실제 청사 좌표 아님). 구조: B-J 갈림길, J→R6 짧은 가지, J→X→R5."""
    nodes = {
        "B": (60.0, 200.0),
        "J": (140.0, 200.0),
        "R6": (140.0, 170.0),
        "X": (260.0, 200.0),
        "R5": (400.0, 200.0),
        "S": (260.0, 320.0),
        "P1": (400.0, 320.0),
        "P2": (60.0, 320.0),
        "Y": (60.0, 260.0),
    }
    edges = (
        ("B", "J"), ("J", "R6"), ("J", "X"), ("X", "R5"),
        ("X", "S"), ("R5", "P1"), ("B", "Y"), ("Y", "P2"),
    )
    return Graph(nodes=nodes, edges=edges)


def build_payload(g: Graph, synthetic: bool) -> dict:
    routes = []
    for (o, d) in [("B", "R6"), ("B", "R5"), ("S", "R5"), ("P1", "R5"), ("P2", "R6")]:
        if o not in g.nodes or d not in g.nodes:
            continue
        length, path = shortest_path(g, o, d)
        style = ORIGIN_STYLE.get(o, {"mode": "?", "color": "#555555"})
        routes.append({
            "id": f"{o}-{d}",
            "origin": o,
            "destination": d,
            "building": DEST_BUILDING.get(d, "?"),
            "mode": style["mode"],
            "color": style["color"],
            "length_px": round(length, 1),
            "path": path,
        })
    return {
        "synthetic": synthetic,
        "notice": ASSUMPTION_NOTICE,
        "branch_d_px": B_J_MISENTRY_BRANCH_PX,
        "junction": "J",
        "wrong_branch_end": "R6",
        "nodes": {k: list(v) for k, v in g.nodes.items()},
        "edges": [list(e) for e in g.edges],
        "routes": routes,
    }


def export(out: str | Path = "viz/routes.json", use_real: bool = False) -> Path:
    if use_real and data_available():
        g, synthetic = load_graph(), False
    else:
        g, synthetic = synthetic_graph(), True
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(build_payload(g, synthetic), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return out


if __name__ == "__main__":
    real = "--real" in sys.argv
    p = export(use_real=real)
    print(f"저장: {p} ({'실제' if real and data_available() else '합성'} 좌표)")
