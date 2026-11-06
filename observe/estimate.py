"""p·r 추정과 조건(N0/N1/N2)·분기별 집계, 재계산 리포트.

p = 오진입 선택 수 ÷ 해당 분기 선택 수
r = 오류 발견 거리 ÷ 가지 길이 (오진입 건의 평균)

표본 n < MIN_N 이면 "표본 부족" 으로 표시한다.
앱 완료 로그만으로 성공을 판정하지 않는다 (reached_correct 는 관측자 기록 기준).
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from observe.model import Observation
from sim.wayfinding import ASSUMPTION_NOTICE, expected_length

MIN_N = 10


@dataclass(frozen=True)
class Estimate:
    condition: str
    junction: str
    n: int                    # 해당 분기 선택 수
    n_wrong: int              # 오진입 수
    p: float | None           # 오진입 비율
    r: float | None           # 평균 발견 비율 (오진입 0건이면 None)
    mean_pause_sec: float
    mean_inquiry: float
    correct_rate: float       # 문의 없이 올바른 접수처 첫 도달 비율
    sufficient: bool          # n >= MIN_N

    @property
    def label(self) -> str:
        return "" if self.sufficient else "표본 부족"


def estimate(observations: list[Observation]) -> list[Estimate]:
    """조건·분기별로 묶어 p·r 및 보조 지표를 계산."""
    groups: dict[tuple[str, str], list[Observation]] = defaultdict(list)
    for o in observations:
        groups[(o.condition, o.junction)].append(o)

    out: list[Estimate] = []
    for (cond, junc), items in sorted(groups.items()):
        n = len(items)
        wrong = [o for o in items if o.chose_wrong]
        p = len(wrong) / n if n else None
        r = (
            sum(o.detect_dist_px / o.branch_len_px for o in wrong) / len(wrong)  # type: ignore[operator]
            if wrong else None
        )
        out.append(Estimate(
            condition=cond,
            junction=junc,
            n=n,
            n_wrong=len(wrong),
            p=p,
            r=r,
            mean_pause_sec=sum(o.pause_sec for o in items) / n,
            mean_inquiry=sum(o.inquiry_count for o in items) / n,
            correct_rate=sum(o.reached_correct for o in items) / n,
            sufficient=n >= MIN_N,
        ))
    return out


def recompute_report(
    estimates: list[Estimate],
    l0: float,
    d: float,
) -> list[dict]:
    """추정 p·r 을 E[L] 식에 넣어 조건별 평균 추가 도상길이를 계산."""
    rows = []
    for e in estimates:
        if e.p is None:
            continue
        r = e.r if e.r is not None else 0.0
        rows.append({
            "condition": e.condition,
            "junction": e.junction,
            "n": e.n,
            "p": round(e.p, 3),
            "r": round(r, 3),
            "expected_extra_px": round(expected_length(l0, e.p, r, d) - l0, 2),
            "note": e.label,
        })
    return rows


def format_report(estimates: list[Estimate], l0: float, d: float) -> str:
    lines = [
        "현장 관측 집계 (관측 기록 기반 — 가정값 아님, 단 표본 수 확인 필요)",
        ASSUMPTION_NOTICE,
        "",
        f"{'조건':<4}{'분기':<6}{'n':>4}{'p':>8}{'r':>8}{'정지(s)':>9}{'문의':>6}{'정확도달':>9}{'추가px':>9}  비고",
        "-" * 78,
    ]
    rows = {(r["condition"], r["junction"]): r for r in recompute_report(estimates, l0, d)}
    for e in estimates:
        row = rows.get((e.condition, e.junction))
        p = f"{e.p:.1%}" if e.p is not None else "-"
        r = f"{e.r:.2f}" if e.r is not None else "-"
        extra = f"{row['expected_extra_px']:.1f}" if row else "-"
        lines.append(
            f"{e.condition:<4}{e.junction:<6}{e.n:>4}{p:>8}{r:>8}"
            f"{e.mean_pause_sec:>9.1f}{e.mean_inquiry:>6.2f}{e.correct_rate:>9.1%}{extra:>9}  {e.label}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    from observe.model import load_observations
    from sim.wayfinding import B_J_MISENTRY_BRANCH_PX, B_R5_L0_PX

    if len(sys.argv) < 2:
        print("사용법: python -m observe.estimate <observations.json>")
        sys.exit(1)
    obs = load_observations(sys.argv[1])
    print(format_report(estimate(obs), B_R5_L0_PX, B_J_MISENTRY_BRANCH_PX))
