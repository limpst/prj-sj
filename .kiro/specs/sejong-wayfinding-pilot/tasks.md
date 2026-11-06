# Tasks — 세종청사 5·6동 Wayfinding 시범

- [x] 1. 기대값 모형과 Dijkstra 구현
  - `sim/wayfinding.py`: Graph, shortest_path, expected_length, extra_length_table
  - `tests/test_wayfinding.py`: README 7.4 표 재현, 363.5px, 범위 검증
  - _Requirements: 1.1, 1.2, 2.1, 2.2, 2.3_

- [x] 2. 계획선 데이터 로더
  - [x] 2.1 `sim/io.py` load_graph(points.csv, edges.csv)
  - [x] 2.2 `data/` 있을 때만 5개 동선 길이 재현 테스트 (없으면 skip)
  - [x] 2.3 28점·27구간 트리 구조 검사 (사이클 없음, 연결됨)
  - _Requirements: 1.3, 1.4_

- [x] 3. 기대값 출력에 가정값 고지 문구 추가 (CLI·JSON 모두)
  - _Requirements: 2.4_

- [x] 4. 승인대장
  - [x] 4.1 `registry/model.py` Marker·Route·Revision dataclass + JSON 입출력
  - [x] 4.2 `registry/validate.py` 동일 Revision, 명칭 일치, 금지 노드 검사
  - [x] 4.3 Route 중지 플래그와 활성 경로 조회
  - [x] 4.4 규칙별 위반 사례 테스트
  - _Requirements: 3.1–3.6_

- [x] 5. 현장 관측
  - [x] 5.1 `observe/model.py` Observation (개인정보 필드 없음)
  - [x] 5.2 `observe/estimate.py` p·r 추정, 조건·분기별 집계, n 표시
  - [x] 5.3 추정 p·r 을 `expected_length` 에 넣는 재계산 리포트
  - _Requirements: 4.1–4.5_

- [x] 6. 경로 재생 시각화
  - [x] 6.1 `sim` → `viz/routes.json` 내보내기 (합성 좌표 옵션)
  - [x] 6.2 `viz/index.html` 정상·오진입·복귀 애니메이션, 색상+숫자 병기
  - _Requirements: 5.1–5.3_

- [ ] 7. '세종 한걸음' 프로토타입 — **후속 사업 승인 후 착수**
  - [ ] 7.1 `?m=` 진입, 마지막 확인지점 상태
  - [ ] 7.2 단계 안내·도움·도착·의견 화면
  - [ ] 7.3 큰 글씨 모드, GPS·회원가입 없음 확인
  - _Requirements: 6.1–6.6_
