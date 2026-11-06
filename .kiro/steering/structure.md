---
inclusion: always
---
# Structure

- `README.md` — 설계 문서 / 기술 보고서 (단일 진실 원천). 설계가 바뀌면 같이 갱신.
- `sim/` — 경로·기대값 계산. 순수 함수, I/O 없음.
- `tests/` — pytest. 모듈별 `test_<module>.py`.
- `registry/` (예정) — 승인대장 스키마 Marker·Route·Revision 와 검증기.
- `observe/` (예정) — 현장 관측 기록 → p·r 추정.
- `viz/` (예정) — 경로 재생 정적 HTML.
- `app/` (예정, 승인 후) — '세종 한걸음' 모바일 웹앱.
- `data/` (비공개, gitignore) — 계획선 좌표 28점·27구간.
- `docs/source/` (비공개, gitignore) — 원자료 PPTX.
- `.kiro/specs/<feature>/` — requirements.md → design.md → tasks.md.
