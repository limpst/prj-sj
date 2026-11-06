"""승인대장 검증기.

규칙:
1. Route 의 모든 Marker 가 같은 Revision 에 존재하는지.
2. 같은 building_no + purpose 조합의 label_ko 문자열이 일치하는지.
3. Route 가 staff_only 또는 internal 노드를 포함하지 않는지.
4. Route 가 중지(active=False)인 경로는 앱 안내 대상에서 빠지는지.

검증 오류는 모두 모아서 반환(첫 오류에서 멈추지 않음).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from registry.model import Registry

_FORBIDDEN_KINDS = frozenset({"staff_only", "internal"})

IssueLevel = Literal["error", "warning"]


@dataclass
class Issue:
    level: IssueLevel
    rule: str
    detail: str

    def __str__(self) -> str:
        return f"[{self.level.upper()}] {self.rule}: {self.detail}"


def validate(reg: Registry) -> list[Issue]:
    """전체 검증 실행. 이슈 목록 반환 (빈 목록 = 통과)."""
    issues: list[Issue] = []
    issues.extend(_check_marker_revision(reg))
    issues.extend(_check_label_consistency(reg))
    issues.extend(_check_forbidden_nodes(reg))
    issues.extend(_check_active_routes(reg))
    return issues


# ── 규칙별 검사 ───────────────────────────────────────────────────────────────

def _check_marker_revision(reg: Registry) -> list[Issue]:
    """Route 에 참조된 Marker 가 Route 와 같은 Revision 에 있어야 한다."""
    issues: list[Issue] = []
    marker_map = {m.code: m for m in reg.markers}
    for route in reg.routes:
        for code in route.marker_seq:
            m = marker_map.get(code)
            if m is None:
                issues.append(Issue(
                    "error", "marker_revision",
                    f"Route '{route.route_id}': Marker '{code}' 가 대장에 없음",
                ))
            elif m.revision != route.revision:
                issues.append(Issue(
                    "error", "marker_revision",
                    f"Route '{route.route_id}' (rev={route.revision}): "
                    f"Marker '{code}' 의 revision={m.revision} 이 다름",
                ))
    return issues


def _check_label_consistency(reg: Registry) -> list[Issue]:
    """같은 목적지(접수처 building_no + purpose)의 label_ko 는 동일해야 한다.

    출발점·갈림길 표식은 자기 위치 이름을 쓰므로 비교 대상이 아니다.
    """
    issues: list[Issue] = []
    seen: dict[tuple[str, str], str] = {}  # (building_no, purpose) -> label_ko
    for m in reg.markers:
        if m.node_kind != "reception":
            continue
        key = (m.building_no, m.purpose)
        if key not in seen:
            seen[key] = m.label_ko
        elif m.label_ko and seen[key] and seen[key] != m.label_ko:
            issues.append(Issue(
                "error", "label_consistency",
                f"Marker '{m.code}': building_no={m.building_no}, purpose={m.purpose} 의 "
                f"label_ko='{m.label_ko}' 가 기존 '{seen[key]}' 와 다름",
            ))
    return issues


def _check_forbidden_nodes(reg: Registry) -> list[Issue]:
    """Route 에 직원 전용·청사 내부 노드가 포함되면 안 된다."""
    issues: list[Issue] = []
    marker_map = {m.code: m for m in reg.markers}
    for route in reg.routes:
        for code in route.marker_seq:
            m = marker_map.get(code)
            if m and m.node_kind in _FORBIDDEN_KINDS:
                issues.append(Issue(
                    "error", "forbidden_node",
                    f"Route '{route.route_id}': Marker '{code}' "
                    f"(kind={m.node_kind}) 는 방문자 경로에 포함할 수 없음",
                ))
    return issues


def _check_active_routes(reg: Registry) -> list[Issue]:
    """중지된 경로는 active=False 여야 하며 경고로만 표시."""
    issues: list[Issue] = []
    for route in reg.routes:
        if not route.active:
            issues.append(Issue(
                "warning", "suspended_route",
                f"Route '{route.route_id}' 는 중지(active=False) 상태 — 앱 안내 제외됨",
            ))
    return issues


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    from registry.model import make_sample_registry

    path = sys.argv[1] if len(sys.argv) > 1 else None
    if path:
        from registry.model import Registry as _R
        reg = _R.load(path)
    else:
        reg = make_sample_registry()
        print("[info] registry.json 경로 없음 — 샘플 대장으로 실행\n")

    issues = validate(reg)
    if not issues:
        print("✅ 검증 통과 — 이슈 없음")
    else:
        errors = [i for i in issues if i.level == "error"]
        warnings = [i for i in issues if i.level == "warning"]
        for i in issues:
            print(i)
        print(f"\n총 {len(issues)}건 (오류 {len(errors)}, 경고 {len(warnings)})")
        sys.exit(1 if errors else 0)
