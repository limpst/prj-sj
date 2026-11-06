"""승인대장 데이터 모델 — Marker · Route · Revision.

설계 원칙:
- DB 없음. JSON 파일 한 개(registry.json)로 관리.
- 사인·앱은 반드시 같은 Revision 을 참조해야 한다.
- 직원 전용(staff_only) · 청사 내부(internal) 노드는 방문자 경로에 포함 불가.
- 승인은 사람이 한다. 코드는 검증만.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Literal

ArrowType = Literal["straight", "left", "right", "u-turn", "arrival"]
StatusType = Literal["active", "suspended", "draft"]
NodeKind = Literal["origin", "junction", "reception", "waypoint", "staff_only", "internal"]


@dataclass
class Marker:
    """현장 표식 하나. 앱의 위치 확인점과 1:1 대응."""
    code: str                          # 고유 코드 (예: B-J-001)
    building_no: str                   # 목적 동 (예: "5", "6", "공통")
    purpose: str                       # 목적 표기 문자열 (예: "방문접수")
    arrow: ArrowType                   # 화살표 방향
    plan_xy: tuple[float, float]       # 계획도면 좌표 (px)
    revision: str                      # 연결된 Revision ID
    status: StatusType = "active"
    node_kind: NodeKind = "waypoint"   # 노드 종류 (보안 검사용)
    label_ko: str = ""                 # 한국어 표기 (예: "6동 통합안내실")
    label_en: str = ""                 # 영문 보조 표기


@dataclass
class Route:
    """출발점 → 접수처까지 승인된 Marker 순서."""
    route_id: str
    origin: str                        # 출발 노드 코드 (예: "B")
    destination: str                   # 도착 노드 코드 (예: "R6")
    marker_seq: list[str]              # Marker.code 목록 (순서)
    revision: str                      # Revision ID
    active: bool = True
    description: str = ""


@dataclass
class Revision:
    """대장 한 번의 개정 이력."""
    revision_id: str                   # 예: "2026-11-06-r1"
    approved_by: str
    approved_at: str                   # ISO 8601
    diff: str                          # 변경 내용 요약
    note: str = ""


@dataclass
class Registry:
    """전체 승인대장."""
    markers: list[Marker] = field(default_factory=list)
    routes: list[Route] = field(default_factory=list)
    revisions: list[Revision] = field(default_factory=list)

    # ── 조회 ────────────────────────────────────────────────────────────────

    def get_marker(self, code: str) -> Marker | None:
        return next((m for m in self.markers if m.code == code), None)

    def active_routes(self) -> list[Route]:
        """중지되지 않은 활성 경로만 반환."""
        return [r for r in self.routes if r.active]

    def suspend_route(self, route_id: str) -> bool:
        """경로를 즉시 중지(앱 안내에서 제외)."""
        for r in self.routes:
            if r.route_id == route_id:
                r.active = False
                return True
        return False

    def latest_revision(self) -> Revision | None:
        if not self.revisions:
            return None
        return max(self.revisions, key=lambda r: r.approved_at)

    # ── 직렬화 ──────────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "markers": [asdict(m) for m in self.markers],
            "routes": [asdict(r) for r in self.routes],
            "revisions": [asdict(r) for r in self.revisions],
        }

    def save(self, path: str | Path) -> None:
        Path(path).write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: str | Path) -> "Registry":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        markers = [Marker(**m) for m in data.get("markers", [])]
        # tuple 복원 (JSON은 list로 저장됨)
        for m in markers:
            object.__setattr__(m, "plan_xy", tuple(m.plan_xy)) if isinstance(m.plan_xy, list) else None
        routes = [Route(**r) for r in data.get("routes", [])]
        revisions = [Revision(**r) for r in data.get("revisions", [])]
        return cls(markers=markers, routes=routes, revisions=revisions)


# ── 샘플 대장 생성 ────────────────────────────────────────────────────────────

def make_sample_registry() -> Registry:
    """테스트·시연용 합성 승인대장."""
    rev = Revision(
        revision_id="2026-11-06-r1",
        approved_by="홍길동",
        approved_at="2026-11-06T09:00:00",
        diff="초기 5·6동 시범 구간 등록",
    )
    markers = [
        Marker("B-001",  "공통", "방문접수", "straight", (100.0, 200.0), "2026-11-06-r1", "active", "origin",    "BRT 북측 출구", "BRT North Exit"),
        Marker("J-001",  "공통", "방문접수", "straight", (150.0, 200.0), "2026-11-06-r1", "active", "junction",  "첫 갈림길 J",  "Junction J"),
        Marker("R6-001", "6",    "방문접수", "arrival",  (155.0, 200.0), "2026-11-06-r1", "active", "reception", "6동 통합안내실", "Visitor Reception Bldg.6"),
        Marker("R5-001", "5",    "방문접수", "arrival",  (450.0, 250.0), "2026-11-06-r1", "active", "reception", "3·5동 종합안내실", "Visitor Reception Bldg.5"),
        Marker("S-001",  "5",    "방문접수", "straight", (300.0, 300.0), "2026-11-06-r1", "active", "origin",    "3동 인근 버스정류장", "Bus Stop near Bldg.3"),
    ]
    routes = [
        Route("RT-B-R6", "B", "R6", ["B-001", "J-001", "R6-001"], "2026-11-06-r1"),
        Route("RT-B-R5", "B", "R5", ["B-001", "J-001", "R5-001"], "2026-11-06-r1"),
        Route("RT-S-R5", "S", "R5", ["S-001", "R5-001"],          "2026-11-06-r1"),
    ]
    return Registry(markers=markers, routes=routes, revisions=[rev])


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "registry/registry.json"
    reg = make_sample_registry()
    reg.save(path)
    print(f"샘플 대장 저장: {path}")
    print(f"  Marker {len(reg.markers)}개, Route {len(reg.routes)}개, Revision {len(reg.revisions)}개")
