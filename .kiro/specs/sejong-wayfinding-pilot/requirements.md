# Requirements — 세종청사 5·6동 Wayfinding 시범

## 배경
방문자가 BRT·버스·주차장에서 내려 방문접수처(R5·R6)까지 가는 동안 갈림길에서 헤맨다.
설문: 방문자 29/44명 바닥 유도 필요, 30/44명 정문 방향안내 추가 선택.
이 spec 은 계획선 기반 계산, 승인대장, 현장 관측, 시각화, 앱 프로토타입의 요구사항을 정의한다.

## 용어
| 용어 | 쉬운 뜻 |
|---|---|
| Marker | 현장 표식 하나 (사인·바닥표식). 앱의 위치 확인점과 1:1 |
| Route | 출발점에서 접수처까지 승인된 Marker 순서 |
| Revision | 승인대장 한 번의 개정. 사인·앱이 같은 Revision 을 쓴다 |
| p / r / d | 오진입 비율 / 오류 발견 위치 비율 / 틀린 가지 길이 |

## Requirement 1 — 계획선 경로 계산
**User Story:** 분석 담당자로서, 계획선 좌표로 5개 대표 동선의 도상길이를 재현하고 싶다. 그래야 원자료와 같은 기준에서 대안을 비교할 수 있다.

**Acceptance Criteria**
1. WHEN 점 좌표와 연결구간이 주어지면 THE SYSTEM SHALL 두 점 사이 최단 도상길이와 경로를 반환한다.
2. WHEN 경로가 없으면 THE SYSTEM SHALL 오류를 발생시킨다.
3. WHEN 원본 28점·27구간 데이터가 입력되면 THE SYSTEM SHALL B→R6 48.0, B→R5 303.5, S→R5 234.9, P1→R5 145.4, P2→R6 163.3 px 를 소수 첫째 자리까지 재현한다.
4. THE SYSTEM SHALL 결과 단위를 px 로 표기하고 m·초로 표기하지 않는다.

## Requirement 2 — 오진입 기대값
**User Story:** 분석 담당자로서, 가정 p·r 에 따른 평균 추가 도상길이를 보고 싶다. 그래야 N1(p↓)과 N2(r↓)의 역할을 구분해 설명할 수 있다.

**Acceptance Criteria**
1. THE SYSTEM SHALL E[L] = L0 + 2·p·r·d 로 계산한다.
2. IF p 또는 r 이 [0,1] 밖이면 THEN THE SYSTEM SHALL 입력을 거부한다.
3. WHEN 기본값(d=30.02, p∈{10,20,30}%, r∈{0.25,0.5,1.0})이면 THE SYSTEM SHALL README 7.4 표와 동일한 값을 출력한다.
4. THE SYSTEM SHALL 출력에 "가정값이며 효과 예측이 아님" 문구를 함께 표시한다.

## Requirement 3 — 승인대장 (Registry)
**User Story:** 청사 관리 담당자로서, 사인·앱·의견 지점을 하나의 대장으로 관리하고 싶다. 그래야 명칭이 어긋나지 않는다.

**Acceptance Criteria**
1. THE SYSTEM SHALL Marker(code, building_no, purpose, arrow, plan_xy, revision, status)를 저장한다.
2. WHEN Route 가 저장되면 THE SYSTEM SHALL 모든 Marker 가 같은 Revision 에 존재하는지 검증한다.
3. IF 같은 목적지에 서로 다른 명칭 문자열이 있으면 THEN THE SYSTEM SHALL 검증 오류를 낸다.
4. IF Route 가 직원 전용 출입구 또는 접수처 이후 내부 구역을 포함하면 THEN THE SYSTEM SHALL 저장을 거부한다.
5. WHEN Route 가 중지되면 THE SYSTEM SHALL 앱 안내에서 즉시 제외한다.
6. THE SYSTEM SHALL Revision 마다 승인자·승인일·변경 내용을 기록한다.

## Requirement 4 — 현장 관측과 p·r 추정
**User Story:** 연구 담당자로서, 관측 기록에서 p·r 을 추정하고 싶다. 그래야 가정값을 실측값으로 바꿀 수 있다.

**Acceptance Criteria**
1. THE SYSTEM SHALL 관측 1건(조건 N0/N1/N2, 출발, 목적, 분기 선택, 정지시간, 되돌아온 지점, 문의 수, 첫 도달 접수처, 시간대)을 받는다.
2. THE SYSTEM SHALL p = 오진입 선택 수 ÷ 해당 분기 선택 수, r = 오류 발견 거리 ÷ 가지 길이 로 계산한다.
3. THE SYSTEM SHALL 조건별·분기별로 집계하고 표본 수를 함께 보여준다.
4. THE SYSTEM SHALL 이름·연락처·얼굴 등 개인 식별정보 필드를 갖지 않는다.
5. THE SYSTEM SHALL 앱 완료 로그만으로 성공을 판정하지 않는다.

## Requirement 5 — 경로 재생 시각화
**User Story:** 발표자로서, 정상 경로와 오진입·복귀 경로를 재생해 보여주고 싶다.

**Acceptance Criteria**
1. THE SYSTEM SHALL 정적 HTML 하나로 열리며 서버가 필요 없다.
2. THE SYSTEM SHALL 색상(도착 수단)과 숫자(목적 동)를 함께 표시한다.
3. THE SYSTEM SHALL 공개 저장소용 빌드에서 실제 평면도 이미지를 포함하지 않는다.

## Requirement 6 — '세종 한걸음' 프로토타입 (후속 승인 후)
**User Story:** 초행 방문자로서, 설치 없이 QR 로 다음 표식 하나씩 안내받고 싶다.

**Acceptance Criteria**
1. WHEN QR 또는 수동 코드가 입력되면 THE SYSTEM SHALL 마지막 확인지점을 갱신한다.
2. THE SYSTEM SHALL 한 화면에 다음 표식 하나만 안내한다.
3. WHEN "길을 모르겠어요"를 누르면 THE SYSTEM SHALL 마지막 확인지점부터 재안내한다.
4. WHEN 접수처 표식이 확인되면 THE SYSTEM SHALL 도착을 알리고 선택형 의견(잘 보임/헷갈림/안 보임/건너뛰기)을 받는다.
5. THE SYSTEM SHALL GPS 를 사용하지 않고 회원가입을 요구하지 않는다.
6. THE SYSTEM SHALL 큰 글씨 모드를 제공하고 색상만으로 정보를 전달하지 않는다.
