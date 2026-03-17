MiroFish 기반 사주 시뮬레이터 SaaS 재딥리서치 보고서
Executive summary
이 보고서는 **MiroFish 레포의 실제 코드 구조(로그/상태/비동기 처리/메모리 업데이트/리포트 생성 방식)**를 “참고 가능한 아키텍처 패턴”으로만 해석하고, AGPL을 수용하지 않는다는 전제에서 사주명리 수익형 SaaS를 만들기 위해 필요한 핵심 5개 산출물을 설계합니다. MiroFish는 패키지 메타데이터에 라이선스가 AGPL-3.0으로 명시되어 있고, 네트워크로 제공되는 수정 버전에 대해 소스 제공 의무를 요구하는 조항(AGPLv3 13조 취지)이 알려져 있으므로, 본 보고서의 설계는 **코드 재사용이 아니라 “아이디어/패턴 수준 참고 + 클린룸 재구현”**을 기본 방침으로 합니다. 

다섯 산출물의 요지는 다음과 같습니다.
첫째, 사주를 “LLM 텍스트”가 아니라 결정론적(재현 가능한) 수치/스키마로 먼저 컴파일해야 하며, 이를 위해 ssaju(TS) 또는 sajupy(Python)처럼 원국·십성·합충형파해·신살·용신·대운·세운·월운까지 산출하는 라이브러리를 엔진 계층으로 두고, 한국 역법 정확도 앵커로 한국천문연구원 데이터/오픈API를 활용하는 설계를 제안합니다. 

둘째, “수만 줄 로그”를 사용자 가치로 바꾸는 핵심은 이벤트 로그 스키마(append-only) + 유의미 사건 추출기이며, MiroFish가 플랫폼별 actions.jsonl을 분리 저장하고(트위터/레딧), 프론트 실시간 표시를 위해 최근 액션을 제한(기본 50개)하는 방식은 그대로 패턴만 차용해 “월/주 단위 사건 카드”로 변환합니다. 

셋째, MVP 시간축은 월 단위 기본(무료/저가) + **주 단위 확대(프리미엄)**가 비용/UX 균형이 가장 좋고, MiroFish가 “소모가 크니 40라운드 이하로 먼저 시도”를 권고하는 점을 비용 경계 설정의 실증적 힌트로 사용합니다. 

넷째, 실시간 시뮬레이션 “느낌”을 제품 정체성으로 삼는다면, API 서버는 FastAPI + WebSocket 스트리밍이 가장 자연스럽고(공식 문서가 await websocket.receive_text()/send_text() 패턴을 제시), 장시간 작업은 Celery 같은 작업 큐로 분리하는 구성이 안정적입니다. 

다섯째, 페이월은 “연간 타임라인의 클라이맥스 카드”에서 걸고, MiroFish가 보고서를 섹션 단위로 생성/제공(섹션 목록 API)하며, 내부적으로 ReportAgent가 JSONL 상세 로그를 남기는 구조는 “무료 요약 + 유료 근거 카드/회피 루트/대화 스크립트”로 전환하기에 매우 적합합니다. 

(이하 각 산출물마다: 요약 → 구현 단계 → 공수/리스크 → 최소 데이터 예시 → 다음 3개 기술 작업을 제공합니다.)

리서치 전제와 MiroFish에서 “패턴만” 가져올 부분
AGPL 비수용 전제에서의 사용 범위
MiroFish 레포는 라이선스가 AGPL-3.0으로 명시됩니다. 

AGPL은 “네트워크 서버로 수정 버전을 제공할 때, 사용자에게 해당 수정 버전의 소스를 제공하도록 하는” 목적의 라이선스로 설명되며(AGPLv3 13조 취지), 공개 서버에서 수정 버전을 운용하면 그 수정 소스에 대한 접근 기회를 제공해야 한다는 설명이 GNU 측 문서에 명시되어 있습니다. 

따라서 “AGPL을 수용하지 않는다”는 전제에서 실무적으로 안전한 전략은 (1) MiroFish 코드를 배포/서버에 포함하지 않고, (2) 설계는 ‘기능 요구사항’만 추출해 별도 스펙으로 작성하고, (3) 구현은 클린룸 방식으로 독립 개발하는 것입니다(클린룸 설계 개념 일반). 

본 보고서에서 인용하는 MiroFish 코드는 “이 프로젝트가 어떤 패턴(로그 구조, 비동기 처리, 상태 모델)을 쓰는지”를 설명하기 위한 것이며, 그 코드를 그대로 재사용하는 구현 지시가 아니라 동일 목적을 달성하는 새 스키마/새 컴포넌트 설계로 치환합니다.

MiroFish에서 추출되는 핵심 패턴
MiroFish README는 5단계 워크플로(그래프 구축 → 환경搭建 → 시작模拟 → 보고서 생성 → 심화 상호작용)를 제시하며, 실행을 위해 LLM API 키(OpenAI SDK 포맷 호환)와 Zep API 키가 필요하다고 안내합니다. 또한 “소모가 크니 40 라운드 미만으로 먼저 시도”를 권고합니다. 

코드 레벨에서 우리가 “패턴만” 차용할 지점은 다음과 같습니다.

장시간 작업의 비동기화: 보고서 생성 API는 “즉시 task_id를 반환하고, 별도 상태 조회로 진행률을 확인”하는 구조를 사용합니다. 
실행 로그의 이원화: 시뮬레이션 러너는 플랫폼별 actions.jsonl(twitter/reddit)을 저장하고, 메인 로그를 파일로 남깁니다. 
프론트 실시간 UX를 위한 최근 로그 제한: recent_actions를 두고 최대 50개로 제한해 “실시간 화면”을 안정적으로 유지합니다. 
메모리 업데이트의 비동기 큐 + 배치 전송: Zep 그래프 업데이트는 Queue에 쌓고 플랫폼별 버퍼로 누적한 뒤 배치로 전송하며, 재시도/전송 간격을 둡니다. 
그래프 구축의 폴링 기반 처리 완료 확인: Graph Builder는 episode들의 processed 상태를 반복 조회하여 완료를 기다리는 루프를 갖습니다(사주 SaaS에서는 “월운/타임라인 배치 계산 완료 확인” 같은 곳에 대응). 
리포트 에이전트의 상세 행위 로깅(JSONL): ReportAgent는 agent_log.jsonl에 단계별 행동(도구 호출/섹션 생성 등)을 기록합니다. 
또한 MiroFish는 LLM 설정을 “OpenAI 형식”으로 통일하고, 모델/베이스 URL을 환경변수로 받습니다. 

이 패턴은 사주 SaaS에서도 “모델 교체 가능 + 비용 통제”의 기반이 됩니다.

마지막으로, MiroFish의 온톨로지 생성기는 Zep의 “커스텀 엔티티/엣지 타입 제한(각 10개)”에 대응하는 로직을 포함하고, 실제로 Zep 문서도 그래프별 커스텀 타입을 10개로 제한한다고 명시합니다. 사주 도메인은 엔티티 타입이 쉽게 확장되므로, Zep/Graph 기반을 그대로 쓰면 타입 제한이 설계 제약이 될 수 있다는 점을 리스크로 기록합니다. 

또한 본 보고서에서 언급하는 출생 정보(생년월일/출생지 등)는 개인정보 범주로 다뤄져야 하며(법률 정의 및 예시로 ‘생년월일’이 포함됨), 최소수집·목적명확·보안 설계가 필요합니다. 

(아래 설계는 이 패턴들을 “사주 시뮬레이터”에 맞게 재구성합니다.)

사주 규칙 정량화 데이터 모델
Executive summary
재현 가능한 사주 SaaS의 코어는 “LLM이 말로 풀기 전에”, 사주명리 요소(오행·십성·합충형파해·신살·용신·대운/세운/월운)를 결정론적 데이터 구조로 컴파일해 두는 것입니다. ssaju는 “원국/십성/합충형파해/신살/용신/대운/세운/월운까지 한 번에 산출”을 명시하고, LLM 입력에 적합한 toCompact()(약 950토큰)과 UI용 toMarkdown() 출력을 제공하므로 “사주→정량 벡터→LLM 설명” 파이프라인에 매우 잘 맞습니다. 

또한 한국 음력/절기 오차를 줄이기 위해 한국천문연구원 기반 데이터/오픈API 또는 그 기반 라이브러리를 앵커로 사용하는 것이 실무적으로 안전합니다. manseryeok-js는 KASI 데이터 기반과 “한국/중국 음력 차이(윤달 위치/시간대/절기 계산)”를 이유로 한국 데이터의 필요성을 강조합니다. 

제안 스키마 개요
아키텍처적으로는 3계층으로 분리합니다.

Input & Policy Layer: 사용자가 입력한 출생 정보 + 계산 정책(윤달/야자시/태양시/절기 기준)
Chart Compilation Layer (결정론): 4주(년·월·일·시) + 지장간 + 파생(오행·십성·합충형파해·신살·용신)
Fortune Timeline Layer (결정론): 대운/세운/월운을 “시간축별 계수”로 정규화
LLM은 “2)와 3)에서 나온 숫자/규칙/근거”를 서술로 변환하는 역할만 수행하도록 설계합니다(LLM 환각 억제 목적).

변수 정의·값 범위·가중치·충돌 규칙
아래 표는 “시뮬레이터가 읽는 최소 정량 변수”를 제안합니다. (가중치는 MVP 기본값이며 A/B + 백테스트로 조정)

변수 그룹	변수	정의	값 범위(권장)	기본 가중치/규칙
오행	element.vec5	목/화/토/금/수 분포 벡터	각 0.0~1.0, 합=1.0	천간/지지/지장간 기여를 합산 후 정규화(정규화는 고정 규칙)
오행	element.excess_deficit	과다/부족 벡터	-1.0~+1.0	vec5 - 0.2를 스케일링(0.2=균형 기준)
십성	tengod.vec10	십성 분포 벡터	각 0.0~1.0, 합=1.0	일간 기준 관계로 매핑(라이브러리 출력 활용)
강약/격	core.strength	일간 강약	0~100	ssaju의 강약(예시 출력에 강약/점수 존재) 기반 정규화 
용신	yongshin.targets	용신 후보(오행/천간/지지)	리스트 + weight 0~1	“필요 오행”은 시뮬레이터에서 완충/보정 계수로 사용
합충형파해	relations.hits[]	합/충/형/파/해/원진/방합/삼합/육합 등 이벤트	type, strength 0~1	natal-natal / natal-fortune / fortune-fortune로 scope 분리
신살	stars.tags[]	신살/길흉신	tag, polarity(-1~+1)	기본은 “참고 레이어”; 영향은 낮게 시작(과적합/유파 분쟁 방지)
월운 계수	month.modifiers	월 단위 환경 변화(리스크/기회)	도메인별 -1.0~+1.0	오행/십성/관계 히트의 월별 델타를 “도메인 계수”로 투영
도메인 리소스	domain.weights	재물/건강/관계/커리어 중요도	0~1	사용자 목표/질문 카테고리로 보정(기본 0.25씩)
충돌 규칙	merge.policy	동시 신호 충돌 해결	규칙 집합	“결정 규칙(하드) → 가중 규칙(소프트) → 서술(LLM)” 3단계

충돌 규칙(핵심만)

하드 레이어: 간지/합충 판정은 무조건 결정(같은 입력은 같은 출력)
소프트 레이어: 사건 발생 확률은 month.modifiers × 사용자 현실(일기/감정/지출 등) × 선택 성향(상태머신)으로 확률화
서술 레이어: LLM은 “확률/근거/대안”을 문장으로 만드는 역할만 수행
이 구조는 ssaju가 이미 “월운/세운/대운”까지 산출한다는 점과 결합할 때 구현 난이도가 낮습니다. 

예시 JSON
아래는 “실제 서비스의 최소 산출물”로, **차트 컴파일 결과 + 월운 타임라인(12개월)**이 한 API에서 나오도록 설계한 예시입니다. (값은 예시이며, 실제는 엔진 출력으로 채움)

json
복사
{
  "schema_version": "saju.v1",
  "chart_id": "chart_01HXYZ...",
  "input": {
    "calendar": "solar",
    "birth_local": "1990-10-10T14:30:00+09:00",
    "timezone": "Asia/Seoul",
    "gender": "male",
    "birth_place": { "city": "Seoul", "lat": 37.5665, "lon": 126.9780 },
    "policy": {
      "use_solar_time": false,
      "early_zi_time": true,
      "jieqi_month_rule": "kasi_based",
      "source": "KASI/OpenAPI + engine"
    }
  },
  "chart_core": {
    "pillars": {
      "year": { "stem": "경", "branch": "오" },
      "month": { "stem": "정", "branch": "유" },
      "day": { "stem": "갑", "branch": "자" },
      "hour": { "stem": "무", "branch": "신" }
    },
    "hidden_stems": {
      "오": ["정", "기"],
      "유": ["신"],
      "자": ["계"],
      "신": ["경", "임", "무"]
    },
    "strength": { "score": 62, "label": "중강" }
  },
  "features": {
    "element": {
      "vec5": { "wood": 0.24, "fire": 0.10, "earth": 0.18, "metal": 0.28, "water": 0.20 },
      "excess_deficit": { "wood": 0.04, "fire": -0.10, "earth": -0.02, "metal": 0.08, "water": 0.00 }
    },
    "tengod": {
      "vec10": {
        "bijian": 0.15, "geopjae": 0.05,
        "siksin": 0.08, "sanggwan": 0.07,
        "jeongjae": 0.10, "pyeonjae": 0.12,
        "jeonggwan": 0.14, "pyeongwan": 0.09,
        "jeongin": 0.12, "pyeonin": 0.08
      }
    },
    "relations": {
      "hits": [
        { "scope": "natal", "type": "충", "a": "자", "b": "오", "strength": 0.7, "note": "예시" }
      ]
    },
    "stars": {
      "tags": [
        { "tag": "역마", "polarity": 0.3, "weight": 0.2 },
        { "tag": "화개", "polarity": 0.2, "weight": 0.2 }
      ]
    },
    "yongshin": {
      "targets": [
        { "kind": "element", "value": "fire", "weight": 0.6 },
        { "kind": "element", "value": "earth", "weight": 0.4 }
      ]
    }
  },
  "fortune_timeline": {
    "monthly": [
      {
        "month": "2026-01",
        "start": "2026-01-01",
        "end": "2026-01-31",
        "modifiers": {
          "element_delta": { "wood": 0.02, "fire": -0.05, "earth": 0.01, "metal": 0.00, "water": 0.02 },
          "domain": { "wealth": -0.10, "career": 0.05, "relationship": -0.02, "health": 0.00 }
        },
        "relation_hits": [
          { "scope": "natal_vs_month", "type": "합", "a": "갑", "b": "기", "strength": 0.4 }
        ]
      }
    ],
    "meta": { "engine": "ssaju_or_sajupy", "engine_version": "pinned", "kasi_anchor": true }
  }
}
이 구조는 (a) ssaju가 산출하는 정보 범위를 직접 포함하고, (b) 월운을 “도메인 계수(domain modifiers)”로 투영해 시뮬레이터가 읽기 쉽게 만든 것이 핵심입니다. 

구체 구현 단계
엔진 선택: TS 중심이면 ssaju(의존성 0, toCompact/toMarkdown 제공), Python 중심이면 sajupy(태양시/절기/조자시 옵션 제공)로 결정합니다. 
정규화 정책 고정: KASI 오픈API/데이터 기반 절기·윤달 처리를 기준으로 “policy 버전”을 고정하고, 입력/출력 테스트 벡터를 구축합니다. 
컴파일러 구현: 엔진 출력(오행/십성/합충/용신/월운)을 위 스키마로 매핑하고, schema_version과 engine_version을 함께 저장합니다.
월운 투영 함수: 월운의 오행/관계 변화를 domain(재물/건강/관계/커리어)로 투영하는 룰(초기 고정 테이블)을 만든 뒤, 백테스트로 보정합니다.
예상 공수(일)와 리스크
항목	추정 공수(일)	주요 리스크
스키마 확정 + 엔진 선택	3~5	유파 차이(용신/신살 해석), 입력정책 분쟁
컴파일러 구현 + 테스트	5~8	달력/절기 경계 오류(신뢰 붕괴), 회귀테스트 부재
월운→도메인 투영 룰	6~10	“근거 없는 숫자”로 보일 위험(설명카드 필요), 과대해석 리스크

리스크 메모

개인정보: 생년월일/출생지는 개인정보로 취급될 수 있으므로 최소 수집·암호화·삭제권을 전제로 설계해야 합니다. 
다음 3개 우선 기술 작업
schema_version=saju.v1 기준으로 Pydantic/JSON Schema를 먼저 고정(서버·워커·프론트 계약).
ssaju 또는 sajupy로 “입력 20개 골든셋”을 만들고 동일 입력=동일 출력 회귀테스트 구축. 
월운 투영 룰(오행/십성/합충 → 도메인 계수) “초기 룰 테이블”을 코드로 명문화하고, 근거 카드에 연결될 rule_id 체계를 설계.
이벤트 로그 스키마와 유의미한 사건 추출기
Executive summary
“사주 시뮬레이터가 다이내믹하게 보이게” 만드는 핵심은, 시뮬레이션/추론 과정에서 생성되는 방대한 로그를 그대로 보여주는 것이 아니라, (1) 재사용 가능한 사건 단위(event)로 정규화해 저장하고, (2) 중요 사건만 추출해 카드/UI/리포트/페이월/백테스트/추천까지 일관되게 재활용하는 것입니다.

MiroFish는 실행 단계에서 플랫폼별 actions.jsonl 로그(트위터/레딧)를 유지하고, 실시간 UI를 위해 recent_actions를 별도 리스트로 관리하며 상한(50개)을 둡니다. 이 “원본 로그(대량) + 최근/요약(소량)”의 분리 패턴을 사주 SaaS에 그대로 적용해, 원본은 append-only로 쌓고, 사용자 노출은 ‘사건 카드’로 제한하는 설계를 추천합니다. 

또한 MiroFish는 메모리 업데이트에서 Queue에 이벤트를 적재하고 플랫폼별 버퍼를 배치 전송하며(전송 간격/재시도 포함), 이는 우리 서비스에서 “이벤트 로그 인덱싱/요약/임베딩”을 워커로 넘기는 패턴에 바로 대응됩니다. 

이벤트 로그 스키마(필드 정의)
이벤트 로그는 **DB의 사실 소스(Source of Truth)**가 되어야 하므로, “리포트/추천/백테스트”까지 확장 가능한 최소 필드를 아래처럼 제안합니다.

필드	타입	의미	재사용 포인트
event_id	UUID	사건 고유 ID	결제 해금/공유/리포트 참조
run_id	UUID	시뮬레이션 실행(연간 리포트) ID	세션/과금 단위
time_bucket	string	YYYY-MM 또는 YYYY-Www	타임라인 UI
scope	enum	monthly/weekly	확대(프리미엄) 구분
domain	enum	wealth/career/relationship/health	대시보드 게이지
event_type	string	사건 유형(규격화)	추천/통계
actors	JSON	self/partner/npc 역할	궁합/동업 확장
cause	JSON	사주 근거: 오행 델타/십성/합충 히트/용신/월운 계수	근거 카드
impact	JSON	게이지 변화(±)	시뮬레이터 느낌
confidence	float	0~1 (규칙 기반일수록 ↑)	백테스트/필터
importance	float	0~1 (추출기 산출)	페이월/요약
emotion_delta	float	-1~+1(선택)	현실 동기화
narrative_teaser	text	무료 티저 1~2문장	공유/유입
narrative_full	text	유료 상세(원인/회피/대안)	페이월
evidence_refs	JSON[]	rule_id, feature_id, log_ref	설명가능성
created_at	timestamptz	생성 시각	운영/감사

원본 로그 저장(권장)

raw_log는 별도 테이블/오브젝트 스토리지로 보관하고, event에는 log_ref만 둡니다.
MiroFish도 simulation.log와 actions.jsonl을 파일로 분리 저장합니다. 
점수화 공식(중요도)
유의미 사건 추출기는 “월/주 단위 후보 사건”을 많이 만들고, 그중 상위만 사용자에게 보여줘야 합니다. 아래는 MVP에서 튜닝 가능한 중요도 공식(0~1) 제안입니다.

importance = clamp01(
0.35·ImpactScore + 0.15·NoveltyScore + 0.15·UserFocusScore + 0.15·CausalClarityScore + 0.10·EmotionDeltaScore + 0.10·ConfidenceScore
)

ImpactScore: impact 벡터의 L2 norm(재물/건강/관계/커리어 변화량)
NoveltyScore: 최근 N버킷 내 동일 시그니처 발생 시 감점(중복 방지)
UserFocusScore: 사용자가 질문한 도메인(예: 이직)과 일치할수록 가점
CausalClarityScore: cause에 “룰 기반 근거(rule_id + feature snapshot)”가 포함되면 가점
EmotionDeltaScore: 사용자 일기/감정 입력이 있는 경우(아래) 사건 전후 변화량
ConfidenceScore: 규칙 기반이면 높게, LLM 추론 비중이 크면 낮게 시작
이 설계는 MiroFish가 “리포트 에이전트 실행 과정을 JSONL로 남겨 추적 가능성을 높이는 방식”과도 정합합니다(서술을 유료로 잠글 때 ‘근거 카드’를 제공하기 쉬움). 

중복 제거/클러스터링 알고리즘
문제: 월 단위 후보 사건이 50개 나오면 UX가 붕괴합니다.
해결: “사건 시그니처(signature)” 기반 클러스터링 후 대표 사건만 남깁니다.

signature 생성(예시)
sig = hash(domain + event_type + top2(cause.relation_hits) + top1(cause.element_delta) + actors_pair)
클러스터링(월 단위)
같은 time_bucket 안에서 sig가 동일/유사한 이벤트는 하나로 묶음
대표는 importance가 가장 높은 이벤트
나머지는 merged_into_event_id로 연결(리포트에 “유사 사건 n건”으로 표시 가능)
감정 변화 추적(현실 동기화)
감정 입력은 선택 기능으로 두되, 유의미 사건 추출기에는 강력한 신호가 됩니다.

매일(또는 주 2~3회) 입력: mood(1~5), stress(1~5), sleep_hours, spend_level(1~5)
emotion_delta는 사건 발생 전후 윈도우(예: 7일) 평균 차이로 계산
emotion_delta가 큰 사건은 “체감이 큰 사건”이므로 importance에 반영
개인정보 측면에서 일기/감정은 민감도가 높을 수 있으므로 저장기간/삭제권/암호화를 디폴트로 둬야 합니다. 

원인-결과 연결 규칙(인과 그래프)
사주 시뮬레이터의 설득력은 “왜?”를 연결할 때 생깁니다. 이벤트 로그에 아래 3단계를 엣지로 남깁니다.

운(환경) 변화: 월운/세운 change (fortune_timeline.monthly.modifiers)
성향/상태 변화: 상태머신의 avoidance_bias/risk_tolerance가 변경
사건(결과): event_log 생성 + impact 반영
이 DAG 구조는 리포트에서 “근거 카드”로 바로 변환됩니다.

백테스트·결제 해금·추천으로의 재사용
백테스트: 사용자가 “2023년에 실제로 있었던 일”을 라벨링하면, 라벨은 event_id + time_bucket + domain에 매칭됩니다.
결제 해금: narrative_teaser는 무료, narrative_full + evidence_refs + avoidance_plan은 유료로 gating.
추천 시스템: 사용자별 feature_vector(오행/십성/월운)와 event_signature의 co-occurrence로 “다음 달 관심 사건” 추천.
예시 쿼리/의사결정 로직
SQL 예시(월 타임라인 상단 사건 3개)

sql
복사
SELECT event_id, time_bucket, domain, event_type, importance, narrative_teaser
FROM event_log
WHERE run_id = :run_id
  AND scope = 'monthly'
  AND time_bucket BETWEEN '2026-01' AND '2026-12'
ORDER BY time_bucket ASC, importance DESC
LIMIT 36;
페이월 후보(클라이맥스 카드) 선택 로직(의사코드)

python
복사
events = get_top_events(run_id, scope="monthly", top_k=2_per_month)
climax = max(events, key=lambda e: e.importance)

# 페이월을 "가장 중요하지만, 불확실성이 낮고(=설명 가능한) 행동지침이 존재"하는 곳에 둠
if climax.confidence >= 0.6 and has_avoidance_plan(climax):
    paywall_target_event_id = climax.event_id
구체 구현 단계
Event 후보 생성(규칙 기반): 월운·합충·오행 델타로 월별 후보 사건을 생성(LLM 호출 0).
Event 정규화 저장: append-only로 DB 저장 후, 워커가 중요도 계산/클러스터링.
LLM은 “서술 캐시 생성”만: top 사건의 narrative_teaser/full을 생성하고 저장(재요청 시 재사용).
Report 섹션 빌더: event_log를 조합하여 섹션(커리어/연애/재물/건강)을 생성.
MiroFish도 보고서 섹션을 리스트로 제공하는 API 구조를 갖습니다. 
예상 공수(일)와 리스크
항목	추정 공수(일)	주요 리스크
이벤트 스키마/DB 마이그레이션	2~4	스키마 잦은 변경(버전 관리 필요)
중요도 점수화 + 클러스터링	5~8	“중요 사건이 안 뽑힘” UX 리스크
LLM 서술 캐싱 파이프라인	4~7	토큰 비용(캐시 미흡 시 폭탄), 프롬프트 누수
근거 카드(evidence_refs)	3~6	설명 부족 시 신뢰 붕괴

리스크 메모(LLM 비용)
MiroFish 자체도 LLM 소모가 큼을 명시적으로 경고합니다. 이 경고는 “round 기반 시뮬”의 비용이 실제로 커질 수 있다는 경험적 신호로 해석할 수 있습니다. 

다음 3개 우선 기술 작업
event_log 테이블(또는 문서형 저장)을 먼저 만들고, “월 후보 사건 1개 생성→저장→조회” end-to-end를 완성.
중요도 공식/클러스터링을 구현하고, “월별 상단 1~3개 사건만 노출” UI를 먼저 연결.
evidence_refs 표준(rule_id, feature_snapshot_hash, diary_window_ref)을 정의해 “근거 카드” 렌더러를 구축.
시간축 매핑 MVP 설계
Executive summary
사주 시뮬레이터의 MVP 시간축은 **월 단위(기본) + 주 단위 확대(프리미엄)**가 비용과 UX를 동시에 만족시키는 ‘스윗스팟’입니다. 이유는 간단합니다.

사용자는 12개월 타임라인을 한눈에 보고 싶어하고(월운 소비 형태),
운영자는 라운드 수가 늘수록 로그/LLM 비용이 기하급수적으로 증가합니다.
MiroFish README가 “소모가 크니 40라운드 미만으로 먼저 시도”를 권고하는 점은 라운드 기반 시뮬레이션의 운영비가 커질 수 있음을 시사합니다. 

또한 MiroFish 설정에는 기본 라운드 수(OASIS_DEFAULT_MAX_ROUNDS) 등 라운드 제어 값이 존재합니다. 

우리는 이 힌트를 사주 SaaS의 “월 라운드 + 주 확대”로 전환합니다.

라운드 정의
기본 모드(월 라운드): 1라운드 = 1개월(총 12라운드/연)
확대 모드(주 라운드): 특정 월을 선택하면 1라운드 = 1주(4~5라운드/월)
(옵션) 초디테일 모드(일 라운드): 프리미엄 단건(예: 2주=14라운드)로 제한
비용·UX 비교표(운영비 추정 포함)
운영비는 “LLM 호출 수 × (프롬프트 토큰 + 출력 토큰)”이 핵심입니다. ssaju는 toCompact()가 LLM 친화적으로 약 950토큰으로 압축됨을 명시하고 있으므로, 프롬프트의 차트 블록은 이를 사용하는 것을 기본으로 합니다. 

가정(예시):

월 라운드당 LLM 호출 1회(요약/서술 생성), 주 라운드당 1회
출력 토큰은 300~600 토큰 범위(서비스 정책으로 제한)
설계	연간 라운드 수	LLM 호출(예시)	UX 장점	UX 단점	운영비 리스크
1라운드=1일	365	365+	극도로 디테일	과도한 로그/피로	매우 높음
1라운드=1주	52	52+	사건 단위 자연	월운 감성 약함	중간
1라운드=1월(기본)	12	12+	한눈에 봄	디테일 부족	낮음
월 기본 + 주 확대	12 + (선택월×4~5)	12 + α	“줌인” 재미	구현 복잡도↑	관리 가능(프리미엄에 비용 전가)

이 표는 MiroFish가 “라운드 수가 커지면 소모가 커진다”고 경고하는 운영 현실과 일치하는 방향으로 설계하는 것입니다. 

샘플 타임라인 데이터(월 기본 + 주 확대)
월 기본(12개)은 무료/구독 모두에 쓰이고, 주 확대는 유료에서만 “상세 사건/회피 루트”를 제공합니다.

json
복사
{
  "run_id": "run_01H...",
  "horizon": { "year": 2026, "base": "month", "zoom": "week" },
  "monthly_index": [
    { "bucket": "2026-01", "tension": 0.32, "opportunity": 0.41, "top_domains": ["career"] },
    { "bucket": "2026-02", "tension": 0.55, "opportunity": 0.28, "top_domains": ["relationship"] }
  ],
  "zoom_weeks": {
    "2026-02": [
      { "bucket": "2026-W05", "tension": 0.62, "events_preview": ["conflict_risk"] },
      { "bucket": "2026-W06", "tension": 0.48, "events_preview": ["networking_gain"] }
    ]
  }
}
Mermaid: 타임라인 매핑 다이어그램
mermaid
복사
flowchart LR
  A[Birth Input] --> B[Chart Compile]
  B --> C[Daewoon/Seawoon Compute]
  C --> D[Monthly Modifiers 12개]
  D --> E{사용자 클릭?}
  E -- 아니오 --> F[월 단위 사건 카드 1~3개/월]
  E -- 예: 특정 월 선택 --> G[주 단위 확대 4~5개]
  G --> H[상세 사건 + 회피 루트(유료)]
구체 구현 단계
월운 배치 계산: 가입/차트 생성 시점에 12개월 monthly.modifiers를 생성하여 캐시(재사용).
월 사건 후보 생성: 월별 Top 사건 1~3개만 만든 뒤 event_log에 저장.
주 확대는 온디맨드: 사용자가 관심 월을 클릭하면 워커가 주 단위 후보 생성 → WebSocket으로 스트리밍. (유료 플랜만)
비용 보호: 확대 모드는 월별 최대 호출 수/토큰 상한을 강제(서술 길이 제한 + 캐시).
예상 공수(일)와 리스크
항목	추정 공수(일)	주요 리스크
월운/월사건 배치 파이프라인	4~7	오프바이원(절기 경계) 오류
주 확대(온디맨드)	6~10	확대 UX가 지연되면 몰입감 하락
비용/쿼터 가드(토큰 제한)	3~6	제한이 너무 강하면 결과 빈약

다음 3개 우선 기술 작업
월 기본(12)만으로 “연간 타임라인 UI + 상단 사건 카드”를 먼저 완성(줌인은 나중).
주 확대를 “이벤트 생성(규칙)만” 먼저 구현하고, LLM 서술은 마지막에 붙여 비용을 통제.
확대 모드의 “최대 호출/월”과 “토큰 상한”을 정책으로 고정하고, 결제 플랜과 연결.
FastAPI + WebSocket 스트리밍 백본 설계
Executive summary
실시간 시뮬레이션 UX(게이지가 움직이고 사건 카드가 “생성되는 느낌”)를 만들려면 HTTP 폴링보다 WebSocket 스트리밍이 자연스럽습니다. FastAPI 공식 문서는 WebSocket 엔드포인트에서 accept() 후 receive_text()/send_text() 루프를 제시하며, FastAPI의 WebSocket은 Starlette에서 가져온다고 명시합니다. 

장시간 작업(월 사건 배치, 주 확대, 리포트 생성, 이미지 렌더링)은 요청-응답 사이클에서 분리해야 하며, Celery는 “실시간 처리에 집중한 task queue + 스케줄링 지원”을 공식 문서에서 밝힙니다. 

MiroFish도 보고서 생성이 비동기 작업이며 task_id를 즉시 반환하고(상태 조회 API로 진행률 확인), ReportAgent가 JSONL 로그를 남기는 구조입니다. 이 구조는 사주 SaaS의 “유료 리포트 생성/근거 카드/감사” 구조로 패턴 차용 가치가 큽니다. 

Mermaid: 전체 아키텍처 다이어그램
mermaid
복사
flowchart TB
  subgraph Client[Web/Mobile Client]
    UI[Dashboard + Timeline + Cards]
    WS[WebSocket Stream]
  end

  subgraph API[FastAPI (ASGI)]
    Auth[Auth/RateLimit]
    Rest[REST API]
    WSHub[WS Hub]
  end

  subgraph Queue[Async Workers]
    CeleryW[Celery Workers]
    Beat[Celery Beat (optional)]
  end

  subgraph Store[Storage]
    PG[(PostgreSQL + JSONB)]
    Redis[(Redis Cache/Streams)]
    S3[(Object Storage: logs/images)]
  end

  subgraph LLM[LLM Providers]
    LLMAPI[OpenAI-compatible API]
  end

  UI --> Rest
  UI <--> WS
  WS <--> WSHub
  Rest --> Auth
  Rest --> PG
  Rest --> Redis

  Rest -->|enqueue| CeleryW
  CeleryW --> PG
  CeleryW --> Redis
  CeleryW --> S3
  CeleryW --> LLMAPI

  Redis --> WSHub
  WSHub --> WS
근거 연결(패턴 출처)

MiroFish는 LLM 설정을 OpenAI 포맷으로 통일(베이스 URL/모델명 환경변수)합니다. 
MiroFish는 보고서 생성 비동기화(task_id 즉시 반환)를 사용합니다. 
엔드포인트 목록(제안)
목적	메서드/경로	비고
차트 컴파일	POST /v1/charts/compile	입력 정책 포함, chart_id 반환
차트 조회	GET /v1/charts/{chart_id}	features + monthly modifiers
시뮬 실행 생성	POST /v1/runs	연간 run 생성(월 기본)
런 상태 조회	GET /v1/runs/{run_id}	queued/running/completed
이벤트 조회	GET /v1/runs/{run_id}/events?bucket=2026-02	월/주별
주 확대 실행	POST /v1/runs/{run_id}/zoom	특정 월→주 단위
리포트 생성	POST /v1/reports	task_id와 report_id 반환(비동기)
리포트 섹션 조회	GET /v1/reports/{report_id}/sections	무료/유료 분리
WebSocket 스트림	WS /v1/runs/{run_id}/stream	진행률/새 사건 push
결제 웹훅	POST /v1/billing/webhook	결제사별

MiroFish의 API도 “create_simulation”, “report_generate(비동기)”, “sections 조회” 등 유사한 리소스 구조를 이미 갖추고 있습니다. 

비동기 워커(Celery) 경계
API 서버(FastAPI)

요청 검증/권한
작업 enqueue
WebSocket으로 진행 이벤트 push(WS Hub)
워커(Celery)

차트 컴파일(엔진 호출)
월운 타임라인 계산(12개월)
월 사건 후보 생성 + 클러스터링
주 확대(4~5주) 사건 생성
리포트 섹션 생성(유료 텍스트/근거 카드)
공유용 이미지 렌더링
Celery가 “실시간 처리 + 스케줄링”을 지원한다고 명시한 점은 “매월 1일 자동 월운 갱신” 같은 배치에도 적합합니다. 

토큰/메모리 관리 전략
전략 A: ‘차트 텍스트’를 표준 압축 포맷으로 고정

ssaju.toCompact()는 LLM 입력을 위해 약 950토큰으로 압축한다고 명시합니다. 이 문자열을 “차트 컨텍스트 블록”으로 고정하면 LLM 비용을 예측할 수 있습니다. 
전략 B: LLM 호출을 “서술 캐시 생성”으로 제한

사건 후보 생성은 규칙 기반으로 하고, LLM은 narrative_teaser/full 생성에만 사용
동일 사건은 캐시(HIT) 시 재생성 금지
전략 C: 이벤트 스트림은 append-only로, 요약은 별도 뷰

Redis Streams는 “append-only” 로그 구조라고 문서에 명시합니다. 실시간 푸시(WS)에는 Redis Streams를 쓰고, 영구 저장은 Postgres에 둡니다. 
전략 D: jsonb 적극 활용 + 필요한 필드만 인덱싱

PostgreSQL의 jsonb는 JSON을 바이너리로 저장해 처리에 유리하며, JSON 관련 연산/연산자 체계를 제공합니다. 
전략 E: Async DB 세션 안전성

SQLAlchemy 문서는 Session/AsyncSession이 상태를 갖는 mutable 객체라서 동시 task 공유가 안전하지 않다고 명시합니다. FastAPI async 환경에서는 요청 스코프 세션을 철저히 분리해야 합니다. 
로컬(맥북 32GB) vs 클라우드 분배 권장
MiroFish는 로컬 실행을 지원하지만, LLM 소모가 크다고 직접 경고합니다. 

따라서 맥북 32GB 기준 권장 분배는 아래와 같습니다.

로컬(개발/자동화/테스트): 차트 컴파일러, 룰 엔진, 이벤트 추출기, API 계약 테스트, 프론트 UI 개발
클라우드(운영/확장): 멀티 유저 동시 실행, 대량 리포트 생성, 이미지 렌더(공유 카드), 임베딩/추천 배치, 결제 웹훅 처리
혼합: “저비용 모드(월 기본)”는 로컬에서도 가능하지만, 프로덕션은 장애/확장 요구로 클라우드 전환이 일반적
예상 공수(일)와 리스크
항목	추정 공수(일)	주요 리스크
FastAPI REST/WS 기본 골격	6~10	WS 연결/재연결/백프레셔
Celery 작업 큐 + 상태 추적	5~9	작업 중복 실행/멱등성
Redis Streams + WS fanout	4~7	스트림 누락/재처리 설계
비용/레이트리밋 가드	4~8	토큰 폭탄, 프롬프트 주입

라이선스 리스크(핵심)
MiroFish는 AGPL-3.0이며, 수정 버전을 서버로 제공할 때 소스 제공 요구 취지가 명시된 라이선스입니다. 본 설계는 “패턴만 참고”하고 코드 재사용을 전제로 하지 않습니다. 

다음 3개 우선 기술 작업
REST + WS 최소 골격: /runs 생성 → WS로 진행률 push → /events 조회를 1주 안에 end-to-end로 연결.
워커 멱등성: job_key = hash(chart_id + bucket + mode)로 중복 실행 방지.
토큰 정책: max_tokens_per_run, max_zoom_per_month를 플랜과 결합하고, 캐시 HIT율을 KPI로 측정.
무료/유료 경계와 페이월 UX 프로토타입
Executive summary
사주 앱을 “텍스트 운세”가 아닌 “다이내믹 시뮬레이터”로 보이게 하려면, 무료는 **움직임(게이지/타임라인/티저 사건)**을 보여주되, 유료는 **근거(왜) + 회피 루트(어떻게) + 분기 비교(만약)**를 해금하는 구조가 전환율이 좋습니다.

MiroFish는 보고서를 비동기로 생성하고 섹션 단위 결과를 제공하며, ReportAgent는 agent_log.jsonl로 생성 과정을 남겨 “근거 연동”이 가능한 구조입니다. 이 패턴은 “무료=요약 섹션, 유료=근거 카드/상세 섹션”으로 거의 그대로 치환할 수 있습니다. 

페이월 위치 추천(클라이맥스 카드)
추천 위치: “연간 타임라인에서 importance가 가장 높은 월”에 클라이맥스 카드를 배치하고, 다음을 유료로 잠급니다.

(무료 공개) “그 달에 위험/기회가 크다” + 1~2문장 티저
(유료 해금) 원인(합충/월운/오행 델타) + 실패 루트/회피 루트 + 대안 행동 스크립트 + 분기 비교
이때 사건 카드는 이벤트 추출기의 importance를 그대로 활용합니다(설계 일관성).

섹션별 무료/유료 배치(제안 매트릭스)
섹션/기능	무료	단건	구독
차트 요약(오행/십성/강약)	✅		✅
연간 월 히트맵(12칸)	✅(요약)		✅
월별 사건 카드(상위 1개)	✅(티저)		✅
월별 사건 카드(상위 3개 + 상세)			✅
주 확대(선택 월 4~5주)		✅(1회권)	✅(월 n회)
근거 카드(evidence)		✅	✅(상세)
회피 루트/대화 스크립트		✅(고가)	✅(Pro)
과거연도 백테스트		✅	✅(연간 1회 포함)
공유 이미지(기본)	✅		✅
공유 이미지(프리미엄/브랜딩 제거)		✅	✅

MiroFish의 보고서 API가 섹션을 배열로 제공하는 방식은 “섹션 단위 paywall” 구현에 잘 맞습니다. 

결제 훅 설계(클라이맥스 카드)
클라이맥스 카드는 심리적 장치이지만, 기술적으로는 “importance 최대 이벤트”를 선택하는 자동 로직입니다.

hook 조건(예시)
importance >= 0.75
confidence >= 0.6 (허무한 낚시 방지)
has_actionable_plan == true (회피/대안 제공 가능)
MiroFish는 시뮬레이션 러너에서 “최근 행동(recent_actions)”을 실시간 UI용으로 따로 관리합니다. 사주 서비스에서도 “최근 사건/진행률”을 실시간으로 보여주다가 클라이맥스에서 유료 해금하는 흐름이 자연스럽습니다. 

A/B 테스트 가설과 KPI(제안)
A/B 가설

A: 클라이맥스 카드에서 “위험(리스크) 중심” 카피 → 결제전환↑, 환불/불만↑ 가능
B: 클라이맥스 카드에서 “해결(회피 루트) 중심” 카피 → 전환율은 약간 낮아도 LTV↑ 가능
C: “분기 비교(2개 선택지 결과)”를 미리 보여주고, “3번째 최적 루트”를 유료로 숨김 → 호기심 기반 전환↑
KPI

1차: 결제 전환율(CVR), 페이월 도달률, 결제당 평균 토큰비용
2차: 7일/30일 재방문, 구독 유지율, 백테스트 참여율(라벨 데이터 수집)
리스크: 환불률, CS 티켓, “불쾌/불안” 신고 비율(안전장치 지표)
구체 구현 단계
리포트 섹션 생성기를 먼저 만든다: 월 사건 카드 → 도메인별 섹션으로 묶기. (LLM 없이도 초안 가능)
티저/유료 본문 분리 저장: narrative_teaser와 narrative_full을 이벤트 로그에 분리 저장(캐시).
결제 후 해금은 ‘컨텐츠’가 아니라 ‘근거+대안’으로: 근거 카드(evidence_refs)와 회피 루트는 유료.
공유용 이미지: 무료는 워터마크 강제, 유료는 “상세 사건 숨김 해제/커스터마이즈”를 제공.
예상 공수(일)와 리스크
항목	추정 공수(일)	주요 리스크
페이월 UI/결제 플로우	6~12	결제 실패/중복, 법무(약관/고지)
섹션 생성/게이팅	5~9	“유료 가치 부족” 인식
공유 이미지 생성	4~7	개인정보 노출(타인/정확한 출생정보)
A/B 테스트 인프라	3~6	통계적 유의성 부족(초기 트래픽)

프라이버시 리스크(중요)
생년월일/출생지 등은 개인정보로서 취급될 수 있고, 일기/감정은 민감도가 높을 수 있으므로 저장/공유(이미지/링크)에서 익명화/최소화가 필수입니다. 