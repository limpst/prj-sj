import dataclasses

import pytest

from observe.estimate import MIN_N, estimate, recompute_report
from observe.model import Observation, load_observations, save_observations


def _obs(wrong=False, detect=None, cond="N1", inquiry=0, reached="R5", pause=2.0):
    return Observation(
        condition=cond, origin="B", destination="R5", junction="J",
        chose_wrong=wrong, branch_len_px=30.0,
        detect_dist_px=detect if wrong else None,
        pause_sec=pause, inquiry_count=inquiry, first_reached=reached,
        time_slot="morning",
    )


def test_no_personal_identifier_fields():
    names = {f.name for f in dataclasses.fields(Observation)}
    assert not names & {"name", "phone", "email", "face", "device_id", "ip"}


def test_p_and_r_estimate():
    # 10건 중 2건 오진입, 발견 거리 15px 와 30px -> r = (0.5 + 1.0) / 2 = 0.75
    obs = [_obs() for _ in range(8)] + [_obs(True, 15.0), _obs(True, 30.0)]
    (e,) = estimate(obs)
    assert e.n == 10 and e.n_wrong == 2
    assert e.p == pytest.approx(0.2)
    assert e.r == pytest.approx(0.75)
    assert e.sufficient


def test_small_sample_flagged():
    (e,) = estimate([_obs() for _ in range(MIN_N - 1)])
    assert not e.sufficient and e.label == "표본 부족"
    assert e.r is None


def test_grouped_by_condition():
    obs = [_obs(cond="N0"), _obs(cond="N1"), _obs(cond="N2")]
    assert [e.condition for e in estimate(obs)] == ["N0", "N1", "N2"]


def test_recompute_matches_formula():
    obs = [_obs() for _ in range(8)] + [_obs(True, 15.0), _obs(True, 30.0)]
    rows = recompute_report(estimate(obs), l0=303.46, d=30.02)
    # 2 * 0.2 * 0.75 * 30.02 = 9.006
    assert rows[0]["expected_extra_px"] == pytest.approx(9.01, abs=0.01)


def test_correct_reach_requires_no_inquiry():
    assert _obs().reached_correct
    assert not _obs(inquiry=1).reached_correct
    assert not _obs(reached="R6").reached_correct


@pytest.mark.parametrize("kwargs", [
    dict(cond="N9"),
    dict(wrong=True, detect=None),
    dict(wrong=True, detect=99.0),
])
def test_invalid_observation_rejected(kwargs):
    with pytest.raises(ValueError):
        _obs(**kwargs)


def test_save_load_round_trip(tmp_path):
    obs = [_obs(), _obs(True, 10.0)]
    p = tmp_path / "o.json"
    save_observations(obs, p)
    assert load_observations(p) == obs
