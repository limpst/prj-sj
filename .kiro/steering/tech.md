---
inclusion: always
---
# Tech

- Python 3.11+ (로컬 3.14). 표준 라이브러리 우선, 외부 의존성 추가 시 이유를 README 에 적는다.
- 테스트: pytest. 원자료 수치(README 7.2·7.4 표)를 재현하는 테스트를 깨지 않는다.
- 경로 계산: 무방향 그래프, 가중치 = 유클리드 도상 px, 이진 힙 Dijkstra (`sim/wayfinding.py`).
- 기대값 모형: E[L] = L0 + 2·p·r·d. p, r ∈ [0, 1] 검증.
- 데이터: 청사 평면도 좌표·원자료 PPTX 는 비공개. `data/`, `docs/source/` 는 gitignore. 테스트는 합성 그래프로.
- 시각화는 정적 HTML(외부 CDN 최소). 앱 프로토타입은 설치 없는 Mobile Web App.
- 문서는 한국어, 전문 용어는 영어 그대로(Wayfinding, Nudge, Dijkstra, EARS …), 용어 표 유지.
- 커밋 전: `python -m pytest -q` 통과.

## 명령
- 테스트: `python -m pytest -q`
- 기대값 표: `python -m sim.wayfinding`
