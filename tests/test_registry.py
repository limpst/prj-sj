import pytest

from registry.model import Marker, Registry, Route, Revision, make_sample_registry
from registry.validate import validate


def _rev():
    return Revision("rev1", "담당자", "2026-11-06T09:00:00", "초기")


def _marker(code, kind="waypoint", rev="rev1", building="공통", label=""):
    return Marker(code, building, "방문접수", "straight", (0.0, 0.0), rev, "active", kind, label)


def test_sample_registry_passes():
    assert validate(make_sample_registry()) == []


def test_round_trip_json(tmp_path):
    reg = make_sample_registry()
    p = tmp_path / "registry.json"
    reg.save(p)
    loaded = Registry.load(p)
    assert len(loaded.markers) == len(reg.markers)
    assert loaded.active_routes()[0].route_id == reg.active_routes()[0].route_id


def test_marker_wrong_revision_is_error():
    reg = Registry(
        markers=[_marker("M1", rev="rev2")],
        routes=[Route("RT1", "B", "R6", ["M1"], "rev1")],
        revisions=[_rev()],
    )
    issues = validate(reg)
    assert any(i.rule == "marker_revision" and i.level == "error" for i in issues)


def test_missing_marker_is_error():
    reg = Registry(
        markers=[],
        routes=[Route("RT1", "B", "R6", ["ghost"], "rev1")],
        revisions=[_rev()],
    )
    assert any(i.rule == "marker_revision" for i in validate(reg))


def test_label_mismatch_for_same_reception_is_error():
    reg = Registry(
        markers=[
            _marker("R6a", kind="reception", building="6", label="6동 통합안내실"),
            _marker("R6b", kind="reception", building="6", label="6동 안내소"),
        ],
        routes=[],
        revisions=[_rev()],
    )
    assert any(i.rule == "label_consistency" for i in validate(reg))


def test_non_reception_label_difference_is_ok():
    reg = Registry(
        markers=[
            _marker("B1", kind="origin", building="공통", label="BRT 출구"),
            _marker("J1", kind="junction", building="공통", label="갈림길"),
        ],
        routes=[],
        revisions=[_rev()],
    )
    assert [i for i in validate(reg) if i.rule == "label_consistency"] == []


def test_forbidden_node_in_route_is_error():
    reg = Registry(
        markers=[_marker("S1", kind="staff_only")],
        routes=[Route("RT1", "B", "R6", ["S1"], "rev1")],
        revisions=[_rev()],
    )
    assert any(i.rule == "forbidden_node" for i in validate(reg))


def test_suspend_route_removes_from_active():
    reg = make_sample_registry()
    rid = reg.routes[0].route_id
    assert reg.suspend_route(rid) is True
    assert all(r.route_id != rid for r in reg.active_routes())
    assert any(i.rule == "suspended_route" and i.level == "warning" for i in validate(reg))
