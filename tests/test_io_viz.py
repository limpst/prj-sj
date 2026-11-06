import json

import pytest

from sim.io import data_available, load_graph
from sim.wayfinding import PLANNED_ROUTES_PX, ASSUMPTION_NOTICE, shortest_path, table_as_dict
from viz.export import build_payload, render_html, synthetic_graph


def _write(tmp_path, points, edges):
    (tmp_path / "points.csv").write_text("id,x,y,kind\n" + "\n".join(points) + "\n", encoding="utf-8")
    (tmp_path / "edges.csv").write_text("a,b\n" + "\n".join(edges) + "\n", encoding="utf-8")


def test_load_graph_tree(tmp_path):
    _write(tmp_path, ["A,0,0,origin", "B,3,4,junction", "C,6,8,reception"], ["A,B", "B,C"])
    g = load_graph(tmp_path)
    assert shortest_path(g, "A", "C")[0] == pytest.approx(10.0)


def test_cycle_rejected(tmp_path):
    _write(tmp_path, ["A,0,0,origin", "B,1,0,junction", "C,2,0,reception"], ["A,B", "B,C", "A,C"])
    with pytest.raises(ValueError, match="트리"):
        load_graph(tmp_path)


def test_disconnected_rejected(tmp_path):
    # 5점·4구간이라 개수는 트리와 같지만, A-B-C 사이클 + D-E 분리 → 연결 검사에서 걸려야 함
    _write(tmp_path,
           ["A,0,0,origin", "B,1,0,junction", "C,2,0,junction", "D,3,0,waypoint", "E,4,0,reception"],
           ["A,B", "B,C", "C,A", "D,E"])
    with pytest.raises(ValueError, match="연결되지 않은"):
        load_graph(tmp_path)


def test_unknown_kind_and_node_rejected(tmp_path):
    _write(tmp_path, ["A,0,0,bogus"], [])
    with pytest.raises(ValueError, match="kind"):
        load_graph(tmp_path)
    _write(tmp_path, ["A,0,0,origin", "B,1,0,origin"], ["A,Z"])
    with pytest.raises(ValueError, match="미등록"):
        load_graph(tmp_path)


@pytest.mark.skipif(not data_available(), reason="data/ 없음 (비공개)")
def test_real_planned_routes_reproduced():
    g = load_graph()
    assert len(g.nodes) == 28 and len(g.edges) == 27
    for (o, d), px in PLANNED_ROUTES_PX.items():
        assert round(shortest_path(g, o, d)[0], 1) == px


def test_json_output_carries_notice():
    out = table_as_dict()
    assert out["notice"] == ASSUMPTION_NOTICE
    assert out["table"]["p=20%"]["r=1.00"] == 12.0


def test_viz_payload_and_html_inline():
    payload = build_payload(synthetic_graph(), synthetic=True)
    assert payload["synthetic"] is True
    assert {r["id"] for r in payload["routes"]} == {"B-R6", "B-R5", "S-R5", "P1-R5", "P2-R6"}
    for r in payload["routes"]:
        assert r["mode"] in {"BRT", "BUS", "CAR"} and r["building"] in {"5", "6"}
    html = render_html(payload)
    assert "/*__DATA__*/" not in html
    start = html.index("const DATA = ") + len("const DATA = ")
    end = html.index(";\n(function", start)
    assert json.loads(html[start:end])["junction"] == "J"
