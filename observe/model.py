"""현장 관측 모델.

개인정보 보호 원칙: 이름·연락처·얼굴·기기 식별자 필드를 두지 않는다.
session_hash 는 익명 해시(무작위)이며 개인을 식별할 수 없어야 한다.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Literal

Condition = Literal["N0", "N1", "N2"]
TimeSlot = Literal["morning", "lunch", "afternoon", "evening"]


@dataclass(frozen=True)
class Observation:
    """관측 1건. 개인 식별 정보 없음."""
    condition: Condition                 # N0 / N1 / N2
    origin: str                          # 출발점 코드 (B, S, P1, P2 …)
    destination: str                     # 목적 접수처 코드 (R5, R6)
    junction: str                        # 관측 분기점 코드 (예: "J")
    chose_wrong: bool                    # 분기에서 틀린 쪽을 골랐는가
    branch_len_px: float                 # 틀린 가지의 도상길이 (px)
    detect_dist_px: float | None         # 오류 발견까지 간 거리 (px). 오진입 아니면 None
    pause_sec: float                     # 판단 정지시간 (초). 방향 판단으로 멈춘 시간만
    inquiry_count: int                   # 문의 횟수
    first_reached: str                   # 첫 도달 접수처 코드
    time_slot: TimeSlot                  # 시간대
    session_hash: str = ""               # 익명 세션 해시 (선택)

    def __post_init__(self) -> None:
        if self.condition not in ("N0", "N1", "N2"):
            raise ValueError(f"condition 은 N0/N1/N2 중 하나: {self.condition}")
        if self.branch_len_px <= 0:
            raise ValueError("branch_len_px 는 0보다 커야 함")
        if self.chose_wrong and self.detect_dist_px is None:
            raise ValueError("chose_wrong=True 이면 detect_dist_px 필요")
        if not self.chose_wrong and self.detect_dist_px is not None:
            raise ValueError("chose_wrong=False 이면 detect_dist_px 는 None")
        if self.detect_dist_px is not None and not (
            0 <= self.detect_dist_px <= self.branch_len_px
        ):
            raise ValueError("detect_dist_px 는 [0, branch_len_px] 범위")
        if self.pause_sec < 0 or self.inquiry_count < 0:
            raise ValueError("pause_sec, inquiry_count 는 0 이상")

    @property
    def reached_correct(self) -> bool:
        """문의·오접수 없이 올바른 접수처에 첫 도달했는가."""
        return self.first_reached == self.destination and self.inquiry_count == 0


def save_observations(obs: list[Observation], path: str | Path) -> None:
    Path(path).write_text(
        json.dumps([asdict(o) for o in obs], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_observations(path: str | Path) -> list[Observation]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Observation(**r) for r in raw]
