import pytest

from sim.wayfinding import (
    B_J_MISENTRY_BRANCH_PX,
    B_R5_L0_PX,
    Graph,
    expected_length,
    extra_length_table,
    shortest_path,
)


def test_table_matches_deck_slide8():
    t = extra_length_table()
    assert [t[(0.10, r)] for r in (0.25, 0.5, 1.0)] == [1.5, 3.0, 6.0]
    assert [t[(0.20, r)] for r in (0.25, 0.5, 1.0)] == [3.0, 6.0, 12.0]
    assert [t[(0.30, r)] for r in (0.25, 0.5, 1.0)] == [4.5, 9.0, 18.0]


def test_full_misentry_round_trip_is_about_60px():
    assert round(expected_length(B_R5_L0_PX, 1.0, 1.0, B_J_MISENTRY_BRANCH_PX), 1) == 363.5


def test_early_detection_halves_extra():
    full = expected_length(0, 0.2, 1.0, B_J_MISENTRY_BRANCH_PX)
    half = expected_length(0, 0.2, 0.5, B_J_MISENTRY_BRANCH_PX)
    assert half == pytest.approx(full / 2)


def test_invalid_probability_rejected():
    with pytest.raises(ValueError):
        expected_length(0, 1.2, 0.5, 1)


def test_dijkstra_prefers_shorter_detour():
    g = Graph(
        nodes={"B": (0, 0), "J": (10, 0), "R5": (20, 0), "X": (10, 30)},
        edges=(("B", "J"), ("J", "R5"), ("B", "X"), ("X", "R5")),
    )
    d, path = shortest_path(g, "B", "R5")
    assert path == ["B", "J", "R5"]
    assert d == pytest.approx(20.0)
