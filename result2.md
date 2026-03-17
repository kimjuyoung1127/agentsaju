MiroFish 기반 사주 시뮬레이터 SaaS 딥리서치
MiroFish 모듈별 재사용과 교체 지도
MiroFish는 “현실 세계의 씨앗 정보”를 넣어 “평행 디지털 세계(다중 에이전트 시뮬레이션)”를 만들고, 그 안에서 상호작용을 돌린 뒤 보고서를 생성하는 흐름을 명시적으로 안내합니다. 리포지토리 문서 기준으로 워크플로는 그래프 구축 → 환경/프로필 생성 → 시뮬레이션 → 보고서 생성 → 세계/에이전트와 대화의 5단계로 설명됩니다. 

또한 시뮬레이션 엔진으로 OASIS를 사용한다고 밝힙니다. 

중요한 전제는, 이 코드베이스는 AGPL-3.0로 표기되어 있어서(패키지 메타데이터에 license: AGPL-3.0) 그대로 가져다 상업용 SaaS에 섞는 순간 라이선스 전략이 제품 전략을 사실상 “강제”할 수 있다는 점입니다. 

따라서 아래의 “재사용 가능”은 두 층위로 나눠 읽어야 합니다.

개념/아키텍처 패턴 재사용(아이디어): 가능 (단, 코드/표현/SSO(구조·순서·조직) 복제 위험 관리 필요) 
코드 재사용(파일/함수 복사, 파생작업): AGPL을 수용하지 않는다면 원칙적으로 “가져오면 안 된다”에 가깝게 접근하는 게 실무적으로 안전합니다. 
아래는 질문에 지정된 모듈(그래프 빌더, 온톨로지, 시뮬 매니저, 리포트 에이전트, 메모리 업데이터)을 “사주 서비스”로 전환할 때의 **재사용 범위(개념/코드)**와 교체 공수를 코드 레벨 근거와 함께 정리한 것입니다.

Graph Builder
MiroFish에서 하는 일(코드 관찰 포인트)
그래프 빌더는 외부 입력(문서/요구사항)을 기반으로 Zep 그래프에 “에피소드(episode) 등 기억 단위”를 쌓고, 내부적으로 특정 상태가 될 때까지 폴링으로 대기하는 루프를 포함합니다. 실제로 graph_builder.py는 에피소드가 준비될 때까지 반복 확인/대기하는 흐름이 보입니다. 

사주 서비스로 바꿀 때 유지할 것(개념)

“입력 → 표준(정규화) JSON → 내부 그래프/메모리 형태로 컴파일”이라는 컴파일러 관점은 그대로 가져갈 가치가 큽니다.
“비동기 빌드” 자체는 유지(사용자가 결제 후 기다리는 긴 작업을 처리해야 함).
제거·대체할 것(개념/구현)

입력이 “뉴스/이슈 텍스트”가 아니라 **생년월일시(+출생지)**로 바뀌므로, 그래프 빌더의 추출 파이프라인은 사실상 전면 교체가 자연스럽습니다.
특히 “에피소드 폴링” 같은 동기식 대기 루프는(TPS·동시접속 증가 시) 백엔드 스레드/프로세스를 잡아먹기 쉬워서, SaaS 운영 관점에서는 작업 큐 기반으로 바꾸는 편이 안전합니다(아래 Celery/Streams 섹션 참고). 폴링 자체를 쓰더라도, API 서버가 아니라 워커에서 수행하는 게 더 안전한 패턴입니다.
(현 코드가 폴링/대기 루프를 포함한다는 근거) 
교체 공수(AGPL 미수용 기준)

코드 재사용 0을 전제로 하면: 중상(약 24주)
“사주 차트 컴파일러” 설계/검증 + “그래프/타임라인 생성” + “테스트 벡터(샘플 명식) 구축”이 핵심입니다.
Ontology Generator
MiroFish에서 하는 일(코드 관찰 포인트)
ontology_generator.py의 시스템 프롬프트는 명확히 “소셜미디어 여론 시뮬레이션”을 전제합니다. 예를 들어 “实体必须是现实中真实存在的、可以在社媒上发声和互动的主体(현실에 존재하며 소셜에서 발화하는 주체)”로 제한하고, 추상 개념/감정/트렌드 같은 것을 ‘엔티티’로 두지 말라고 강하게 금지합니다. 

출력 포맷도 entity_types/edge_types를 가진 JSON을 요구하며, “정확히 10개 엔티티 타입” 등 구조적 제약이 있습니다. 

사주 서비스로 바꿀 때 유지할 것(개념)

“도메인 온톨로지(타입/관계) 정의를 별도 산출물로 만들고, 그 산출물로 타입 시스템(Pydantic 등)을 자동 생성”하는 발상은 매우 유용합니다. 실제로 이 파일은 온톨로지 정의를 Python 코드로 변환하는 함수도 포함합니다. 
제거·대체할 것(개념/구현)

사주에서는 엔티티가 “현실의 사람/회사/정부”가 아니라, 명식 구성요소(간지, 오행, 십성, 신살, 대운/세운/월운) 및 “인생 자원(재물/건강/관계/커리어)”가 핵심입니다. 즉, 현재 온톨로지 프롬프트/스키마는 도메인 전제가 맞지 않아 거의 전면 교체가 필요합니다. 
교체 공수(AGPL 미수용 기준)

중(약 1~2주)
핵심은 “사주 데이터 모델”을 먼저 확정한 뒤, 그 모델을 표현하는 온톨로지/스키마(고정 타입 + 확장 타입)를 만드는 것입니다.
Simulation Manager
MiroFish에서 하는 일(코드 관찰 포인트)
simulation_manager.py는 준비 단계에서 Zep 그래프에서 엔티티를 읽고(ZepEntityReader), 그 엔티티를 기반으로 프로필을 생성하며(OasisProfileGenerator), 이어서 LLM으로 시뮬레이션 설정을 생성합니다. 

또한 결과적으로 실행 커맨드(트위터/레딧/병렬)를 조립해 “어떤 스크립트를 실행하라”는 형태의 지시를 반환합니다. 

사주 서비스로 바꿀 때 유지할 것(개념)

“시뮬레이션 = 준비(상태/프로필/설정) + 실행(러너) + 관측(로그)”로 나누는 관리 계층은 그대로 가져갈 수 있습니다.
“설정 생성(LLM)과 런타임 실행(프로세스/워커)을 분리”하는 구조적 분리는 운영상 유리합니다. 
제거·대체할 것(개념/구현)

현재는 플랫폼이 twitter/reddit로 고정된 흔적이 강합니다(PlatformType, 프로필 포맷, OASIS 요구 CSV/JSON 등). 사주 시뮬레이터는 “플랫폼”이 아니라 “삶의 영역(커리어/연애/재물/건강)”이 축이 되어야 하므로, 프로필 생성기·설정 생성기는 재설계 대상입니다. 
교체 공수(AGPL 미수용 기준)

상(약 3~6주)
이유: “프로필 생성 → 이벤트 엔진 → 타임라인(대운/세운/월운) → 리포트”까지 전체 연결부(오케스트레이션)를 다시 짜야 합니다.
Report Agent
MiroFish에서 하는 일(코드 관찰 포인트)
report_agent.py는 Zep 검색 도구(ZepToolsService)를 포함한 툴 기반 리포트 에이전트로 설계되어 있습니다. 파일에는 도구 설명(InsightForge, PanoramaSearch, QuickSearch, InterviewAgents)이 상수로 정의되어 있고, 특히 “실제 시뮬레이션 에이전트를 인터뷰하는 API(/api/simulation/interview/batch)를 호출한다”는 취지가 명시되어 있습니다. 

또한 ReACT 스타일의 “생각-도구호출-결과-작성” 로그를 JSONL로 남기는 상세 로깅 구조가 포함됩니다. 

사주 서비스로 바꿀 때 유지할 것(개념)

“보고서 생성 = (근거 검색 → 근거 카드화 → 섹션별 서술)”이라는 구조는 그대로 가져갈 수 있습니다.
특히 JSONL 기반의 상세 로그(생각/도구/결과/섹션완료)는, 사주 서비스에서 결제 해금(근거 공개) / 백테스트 / 품질 모니터링에 매우 직접적으로 재활용 가능합니다. 
제거·대체할 것(개념/구현)

도구 자체가 “Zep 그래프의 여론 시뮬레이션 결과”를 향해 있어, 사주 서비스에서는 도구군을 “명식 계산/규칙 엔진/타임라인 조회/이벤트 로그 조회/다중 명식 관계 분석”으로 교체해야 합니다.
교체 공수(AGPL 미수용 기준)

중상(약 24주)
UI/결제와 맞물려 “근거 카드 → 페이월 → 해금 후 상세 근거/대안 시나리오” 설계를 함께 해야 합니다.
Memory Updater
MiroFish에서 하는 일(코드 관찰 포인트)
메모리 업데이터는 zep_graph_memory_updater.py에 구현돼 있으며, 시뮬레이션 행동 로그를 받아 큐에 쌓고, 플랫폼별 버퍼에 모아 배치 전송합니다. DO_NOTHING 유형은 건너뛰며(필터링), 워커 스레드가 큐를 소비합니다. 

시뮬레이션 러너는 actions.jsonl을 읽다가 업데이터가 활성화되어 있으면 add_activity_from_dict로 메모리 업데이트에 전달합니다. 

사주 서비스로 바꿀 때 유지할 것(개념)

“시뮬레이션 도중 발생한 이벤트/행동을 장기 저장소(그래프/벡터/DB)에 비동기 반영”하는 이중화(operational write vs analytic write) 패턴은 매우 적합합니다.
“DO_NOTHING/노이즈 이벤트 필터링” 같은 개념도 그대로 유효합니다. 
제거·대체할 것(개념/구현)

사주 서비스에서는 장기기억이 꼭 그래프일 필요는 없습니다. DB 이벤트소싱(append-only) + 요약/임베딩 인덱스 조합이 비용·복잡도에서 더 유리할 수 있습니다(아래 DB/Streams 설계 참고).
“플랫폼별 버퍼(twitter/reddit)”는 “영역별 버퍼(재물/건강/관계/커리어)”로 전환하는 편이 자연스럽습니다.
교체 공수(AGPL 미수용 기준)

중(약 1~2주)
이벤트 스키마 확정이 먼저이며, 그 후에 큐/배치/재시도 메커니즘을 붙이면 됩니다.
AGPL을 수용하지 않고 상업용 SaaS를 만들 때 필요한 클린룸 재구현 수준
AGPL의 핵심 리스크
MiroFish의 패키지 메타데이터는 이 프로젝트의 라이선스를 AGPL-3.0으로 명시합니다. 

Free Software Foundation 문서에서 AGPL은 “서버에서 수정 버전을 운영하면서 네트워크로 사용자가 상호작용할 경우, 그 수정 버전의 소스(‘Corresponding Source’)를 제공해야 한다”는 목적을 명확히 밝힙니다. 

특히 **AGPLv3 13조(Remote Network Interaction)**는 “네트워크로 원격 상호작용하는 사용자에게 해당 버전의 소스를 제공할 기회를 제공해야 한다”고 규정합니다. 

즉, “AGPL 코드(또는 파생물)를 SaaS로 제공하면서 소스 공개를 피하고 싶다”는 목표와는 정면 충돌할 가능성이 큽니다(구체적 범위는 법률 자문 필요). 

안전한 선택지 비교
상업용 SaaS + 비공개 코어를 유지하려는 목표가 확고하다면, 실무적으로는 다음 3가지 중 하나로 수렴합니다.

저작권자에게 상업용 라이선스(듀얼 라이선스) 협상: 가장 깔끔하지만 가능 여부 불확실.
AGPL을 수용하고 ‘오픈코어’ 전략으로 가기: 서버 코드 공개를 감수하고, 운영/데이터/모델/콘텐츠/브랜드/엔터프라이즈 기능에서 수익화.
클린룸 방식으로 ‘아이디어만 참고’하고 전면 재구현: 기술적으로는 어렵지만 목표에 부합.
“클린룸 설계(Chinese wall)”는 일반적으로 분석자(스펙 작성)와 구현자(코드 작성)를 분리해, 독립 창작임을 입증하기 쉽게 만드는 방어 전략으로 설명됩니다. 

또한 한국에서도 AGPL 13조 관련 문의에 대해 “수정이 있을 경우 네트워크 사용자에게도 소스 제공” 취지를 짚는 안내가 존재합니다. 

“어디까지 클린룸이어야 하는가”에 대한 실무적 답
법률 조언을 대체할 수는 없지만(반드시 자문 권장), 실무적으로 분쟁 리스크를 가장 낮추는 전략은 다음과 같습니다.

MiroFish 코드를 ‘읽고 그대로 구현’하는 경로를 끊기
구현자는 MiroFish 소스/주석/프롬프트를 보지 않고, “사주 시뮬레이터 요구사항 명세(스펙)”만 보고 구현. 
산출물(스펙)에서 ‘표현’을 제거
클래스명/함수명/파일 경로/프롬프트 문장/상수 구조(SSO)를 베껴오지 않도록, 스펙은 “입력·출력·불명확성 처리·테스트 벡터” 중심으로 작성.
감사 가능한 증빙을 남기기
ADR(Architecture Decision Record), 스펙 버전 관리, 테스트 벡터의 출처(공개 자료/자체 생성) 기록.
이 접근은 “아이디어(기능) 자체”보다 “표현(구현, 구조, 문장)”이 저작권 분쟁의 핵심이 되는 경향을 방어하기 위한 실무식 설계입니다. (클린룸의 일반적 개념/목적) 

사주 규칙을 시뮬레이터가 읽는 정량 변수로 바꾸는 데이터 모델
재현성의 기준
사주 서비스에서 “재현성 높은 모델”의 기준은 대체로 아래 3가지를 만족해야 합니다.

같은 입력이면 언제나 같은 명식/대운/세운/월운이 나온다
각 단계의 변환이 추적 가능하다(어떤 규칙이 어떤 변수를 만들었는지)
LLM이 없는 상태에서도 최소한의 일관된 결과를 만든다(LLM은 서술/해석/조언에 한정)
이를 위해 전체를 “컴파일 파이프라인”으로 보면 안정적입니다.

입력 정규화: 출생 정보(양력/음력, 시간대, 출생지, 표준시/태양시 보정 정책)
차트 컴파일: 년/월/일/시의 천간·지지(4주=8자) 산출
파생 피처 계산: 오행 분포, 음양, 십성, 합·충·형·파·해, 신살, 대운·세운·월운
정량 매핑: 시뮬레이터 상태·가중치·충돌규칙으로 변환
서술/플레이: LLM이 개입하되 근거(규칙/변수/로그)를 참조
“4주 8자(년·월·일·시의 천간·지지)”가 핵심 구조라는 점은 Four Pillars/BaZi 설명에서 확인할 수 있습니다. 

만세력/달력 계산 라이브러리 선택
한국 사주 서비스는 “절기/윤달/시간대”에서 오차가 나면 바로 신뢰가 붕괴합니다. 따라서 “한국 음력 데이터 기반”을 우선하는 것이 합리적입니다.

한국천문연구원의 천문우주지식정보는 음양력 정보 조회 Open API를 제공합니다. 
@fullstackfamily/manseryeok(manseryeok-js)는 “한국천문연구원 음양력변환계산 데이터 기반”을 명시하고, 한국/중국 음력 차이(윤달 위치/절기 계산/시간대) 때문에 한국 데이터가 필수라고 설명합니다. 
Python쪽으로는 sajupy가 “만세력 데이터 기반, 절기 시간 반영, 태양시 보정, 조자시/야자시 처리” 등을 특징으로 내세웁니다. 
실무 추천은 다음 중 하나입니다.

프론트/백 모두 TS 중심이면 manseryeok 계열로 “명식 계산 마이크로서비스”를 만들기 쉬움. 
Python 중심 백엔드면 sajupy 같은 검증된 라이브러리를 “차트 컴파일러”로 채택. 
정확도 기준 데이터로는 KASI API를 부분적으로 활용(검증/회귀테스트에 특히 유용). 
정량 변수 설계안
아래는 “명리학 개념을 시뮬레이터 변수로 바꾸는” 목적에 맞춘 제안 모델입니다(해석 유파 차이는 플러그인으로 분리).

ChartCore
pillars: {year, month, day, hour} 각각 stem, branch
hidden_stems: 각 지지의 장간 리스트
time_corrections: 표준시/태양시/절기경계 정책 및 적용 결과
이 레벨은 완전 결정적이어야 합니다.

FeatureVector
element_balance: 오행 벡터(목/화/토/금/수)
값 범위: 0.0~1.0 합=1.0(정규화)
산출: 천간/지지/장간에 가중치를 두고 합산(가중치는 정책으로)
yin_yang_balance: -1.0~+1.0 (음 과다 ↔ 양 과다)
ten_gods_distribution: 십성(비견/겁재/식신/상관/편재/정재/편관/정관/편인/정인) 가중치 합
십성은 “일간(자기)을 기준으로 다른 오행/음양과의 관계”로 정의되는 층위라는 설명이 널리 알려져 있습니다. 
relations_matrix: 합/충/형/파/해를 (원국 내부, 운(대/세/월)과의 교차)로 나눠 기록
예: relations_matrix["natal_vs_monthly"] = [ {a:"戊", b:"癸", type:"합", strength:0.7}, ...]
stars: 신살/격국/용신 등은 텍스트 리스트 + 신뢰도/가중치로 분리
권장: “신살은 참고 레이어”로 두고, 핵심 모델은 오행·십성·합충 중심으로 설계(유파 분쟁 완화).
충돌 규칙과 가중치(운영 친화형)
이 모델에서 “재현성”을 해치기 쉬운 부분은 충돌 규칙입니다. 추천은 3단계 충돌 처리입니다.

결정 규칙(하드 룰): 달력/간지/합충 판정은 무조건 결정
가중 규칙(소프트 룰): 합/충이 실제로 “사건”으로 발현될 확률은 컨텍스트(사용자 현실 변수, 최근 감정/사건)와 함께 확률화
서술 규칙(LLM): 확률/근거를 사람이 읽기 좋게 서술
가중치의 기본 범위는 아래처럼 단순화하면 운영이 쉽습니다.

합(합/삼합/방합): +0.2~+0.8
충(충/형/파/해): -0.2~-0.8
용신 방향과 일치: “완충(bonus buffer)” +0.1~+0.4
사용자 현실 변수(직업/관계상태/자산/건강): 영역별 스케일러(예: 재물 이벤트 민감도)
이렇게 하면 “명리는 룰 기반, 발현은 확률 기반”으로 분리돼 LLM 환각을 억제하기 쉽습니다.

시간축 매핑과 에이전트 설계
대운·세운·월운을 시뮬레이션 시간축으로 매핑하는 비교
사주 서비스의 UX는 “한 번에 1년을 쭉 보여주는” 경험이 중요해 월운을 자주 언급합니다(예: 포스텔러 설명에 “월운 흐름”이 포함). 

운영비/UX 관점에서 3안을 비교하면 다음과 같습니다(제안).

라운드=1일
UX: 디테일은 뛰어나지만 사용자가 피로해지기 쉽고, “증거 로그”가 과잉 생성
비용: 에이전트/LLM 호출 빈도가 급증(토큰 폭탄 위험)
권장 사용처: “특정 월의 2주 디테일 모드” 같은 프리미엄 기능
라운드=1주
UX: “주간 사건” 단위로 사건화/요약이 쉬워 사용자가 이해하기 좋음
비용: 일 단위 대비 1/7 수준으로 안정화
권장: 기본 시뮬레이션 타임스텝으로 가장 균형이 좋음
월 단위 이벤트 엔진(라운드=1개월)
UX: 연간 타임라인을 한눈에 보여주기 좋음
비용: 가장 저렴
단점: “클라이맥스(결제 유도)”를 만들 디테일이 부족해질 수 있음
현실적인 추천은 “기본은 월 단위 엔진 + 주 단위 확대(zoom-in)”입니다.

무료/저가 플랜: 월 단위 이벤트(12개)
구독/프리미엄: “관심 월”을 주 단위로 확장(4~5 라운드)
단건 고가: “특정 2주를 일 단위로 디테일”
LLM 프롬프트와 비-LLM 상태머신의 분리 설계
사주 기반 에이전트는 “성향/강점/약점/회피 패턴”을 모두 프롬프트에 넣으면 토큰이 폭증하고, 장기 일관성이 흔들립니다. 따라서 아래 분리가 안정적입니다.

비-LLM 상태머신이 관리할 것
traits: (예: 결단성, 안정추구, 관계중심, 모험성) 0~100
resources: 건강/재물/관계/커리어 게이지 + 회복/손실 규칙
defense_patterns: 회피/돌파/의존/통제 등의 선택 편향(가중치)
current_luck_modifiers: 월운/세운에 의해 변하는 환경 변수(스트레스 민감도, 금전 리스크 등)
LLM이 할 것
“상황 설명 → 가능한 선택지 생성 → 선택의 정서적 설득력 있는 내러티브”
다만 선택지의 점수/확률은 상태머신이 계산하고, LLM은 설명자로 제한
MiroFish도 “LLM+툴”을 전제로 ReportAgent를 설계하고, 도구 호출과 결과를 로깅하는 구조를 갖습니다. 

이 패턴을 사주에도 그대로 적용하면 “LLM은 서술·요약, 룰엔진은 계산”으로 역할이 명확해집니다.

이벤트 스키마와 로그 저장 구조
MiroFish는 시뮬레이션 과정에서 actions.jsonl 같은 append-only 로그 파일을 읽어 상태를 갱신하고(최근 행동 50개 유지), 필요 시 Zep 메모리 업데이트로도 흘려보냅니다. 

사주 SaaS에서는 파일 대신 DB 이벤트소싱으로 옮기는 게 운영상 유리합니다. 아래 DB 섹션의 event_log 스키마가 그 기반입니다.

이벤트 스키마(제안)는 “나중에 리포트/백테스트/추천/결제 해금까지”를 목표로 최소 다음 필드를 갖추는 것이 좋습니다.

event_type: (career_change_risk, relationship_conflict, health_dip, windfall, etc.)
time_scope: year/month/week/day + ISO 기간
actors: 본인/상대(궁합)/NPC/환경
cause_features: 어떤 사주 파생 피처가 원인인지(합충/십성/오행 불균형/월운 변화 등)
impact_vector: 건강/재물/관계/커리어 게이지에 미친 영향(+-)
evidence_refs: 근거 카드(룰 ID, 계산 결과, 로그 링크)
llm_summary: 사용자 노출용 1~2문장(캐시 가능)
“유의미한 사건” 추출 로직
수만 줄 로그에서 의미 있는 사건만 뽑는 문제는 점수화 + 압축 + 인과 연결 3단계로 풀면 운영이 쉽습니다.

중요도 점수화
importance = w1*|impact_vector| + w2*novelty + w3*confidence + w4*user_focus_match
novelty는 “최근 30일(시뮬 기간) 내 유사 이벤트가 있었는지”로 감점
중복 제거(클러스터링)
같은 월/주에 같은 원인(예: 특정 충)으로 반복되는 이벤트는 “한 사건군”으로 묶어 대표 1개만 노출
감정 변화 추적
사용자 일기/감정 입력이 붙으면(아래 동기화 루프) 이벤트 전후의 감정 변화를 emotion_delta로 반영해, 실제 체감과 맞는 사건을 더 상단에 노출
원인-결과 연결 규칙
(원인) 월운 변화/합충 발생 → (중간) 행동 편향 변화(충동, 회피 등) → (결과) 재물/관계/커리어 사건
이 연결을 이벤트 로그에 “edge”로 남기면 리포트에서 “왜 이런 결론이 나왔는지” 근거 카드가 쉬워집니다.
과거 연도 백테스팅 기능
백테스트는 “맞췄다/틀렸다”를 단정하면 역효과가 나기 쉬워, 캘리브레이션 중심이 안전합니다.

사용자 입력 UX(제안)
사용자가 2023 같은 과거 연도를 선택
시스템은 월별로 “가능성 높은 사건 후보(카드)”를 제시
사용자는 (발생/미발생/애매/기억 안남) + 강도(1~5)로 라벨링
평가 지표(제안)
사건 검출: Precision/Recall/F1(월 단위)
강도 예측: Spearman 상관(순위)
확률 보정: Brier Score / reliability diagram(내부 KPI)
모델 보정 루프(제안)
유저 라벨 → “가중치(합충/십성/현실 변수) 업데이트”
단, 개인별로 과적합되지 않게 “전역 priors + 개인 편차” 분리
실시간 백엔드 선택과 작업 큐 전략
Flask 유지 vs FastAPI 전환
MiroFish 백엔드는 Flask 앱 팩토리를 명시하고, 실제로 from flask import Flask를 사용 ensures_ascii 등 Flask 설정을 적용합니다. 

또한 준비 작업은 백그라운드 스레드로 돌리고 상태 조회 API로 폴링하는 방식이 보입니다. 

실시간 시뮬레이션 + WebSocket 스트리밍이 목표라면, 선택지는 현실적으로 아래처럼 정리됩니다.

FastAPI(ASGI)
WebSocket 라우트에서 await로 메시지 수신/전송하는 문서가 공식으로 제공됩니다. 
FastAPI는 Starlette 기반이며, Starlette도 WebSocket 클래스를 제공한다고 명시합니다. 
결론: 실시간 스트리밍/비동기 IO에 “기본 모델이 맞는” 쪽.
Flask 유지 + Flask-SocketIO
Flask-SocketIO는 Flask 앱에 “저지연 양방향 통신”을 제공한다고 설명합니다. 
하지만 Socket.IO는 “WebSocket 구현이 아니며” 프로토콜/클라이언트가 다르다는 점을 Socket.IO 문서가 강조합니다. 즉, 프론트가 순수 WebSocket만 쓰면 붙지 않습니다. 
Flask 자체의 async 지원은 “ASGI 프레임워크처럼 이벤트루프에서 돌리는 방식이 아니라 별도 스레드에서 실행하는 절충”이라 성능 비용이 있다는 설명도 존재합니다. 
결론: 가능은 하지만, 스케일링/운영 복잡도가 올라가기 쉬움.
추천: “실시간 시뮬레이터”를 핵심 USP로 삼는다면 FastAPI 전환이 더 일관됩니다. (근거: WebSocket/ASGI 우위) 

비동기 잡 처리
MiroFish는 시뮬레이션 러너에서 외부 스크립트를 subprocess로 띄우고, 로그 파일로 stdout/stderr를 직접 쓰며, actions.jsonl을 읽어 상태를 업데이트합니다. 

이 방식은 단일 머신/데모에선 단순하지만, SaaS에서는 작업 격리/보안/스케줄링 때문에 작업 큐가 필요합니다.

Celery는 “분산 메시지 기반 작업 처리 시스템”이며 “실시간 처리와 스케줄링을 지원”한다고 문서에서 설명합니다. 
권장 아키텍처(제안):

API 서버(FastAPI): 요청 검증, 작업 enqueue, WebSocket push
워커(Celery): 차트 컴파일, 시뮬 실행, 요약/리포트 생성, 이미지 렌더
결과 저장: DB + 오브젝트 스토리지(S3 호환)
DB 스키마 제안과 이벤트 파이프라인
저장소 선택
기본 DB는 PostgreSQL 권장.

사건/근거/요약은 스키마가 변하기 쉬우므로 JSONB를 적극 활용하되, 조회 빈도가 높은 필드는 컬럼으로 정규화합니다.
PostgreSQL 문서는 jsonb가 바이너리 형태로 저장되어 “재파싱 없이 더 빠르게 처리”되고 “인덱싱 지원”이 장점이라고 설명합니다. 

실시간 이벤트 스트림/팬아웃: Redis Streams도 선택지.
Redis는 Streams를 “append-only log” 형태의 자료구조로 설명합니다. 

또한 Redis 공식 튜토리얼은 Streams를 마이크로서비스 간 통신에 활용할 수 있고, “메시지 저장/컨슈머그룹/리플레이” 등을 비교표로 정리합니다. 

테이블 수준 스키마
아래는 요청하신 테이블(user, chart, fortune_timeline, simulation_run, event_log, report_section, billing, feedback) 기준의 제안입니다. (DDL은 예시이며, 실제는 ORM/마이그레이션으로 관리)

sql
복사
-- user: 계정/동의/보안
CREATE TABLE "user" (
  id                uuid PRIMARY KEY,
  email             text UNIQUE NOT NULL,
  password_hash     text,              -- 소셜 로그인만이면 nullable
  display_name      text,
  locale            text DEFAULT 'ko-KR',
  timezone          text DEFAULT 'Asia/Seoul',
  created_at        timestamptz NOT NULL DEFAULT now(),
  deleted_at        timestamptz,

  -- 동의/법적
  terms_accepted_at timestamptz,
  privacy_accepted_at timestamptz,
  marketing_opt_in  boolean DEFAULT false
);

-- chart: 사용자 1인(혹은 여러 프로필) 명식 원본/계산결과
CREATE TABLE chart (
  id               uuid PRIMARY KEY,
  user_id          uuid NOT NULL REFERENCES "user"(id),
  profile_label    text,               -- "나", "연인", "동업자A"
  birth_datetime   timestamptz NOT NULL, -- 표준화된 출생시각(입력 정책에 따라)
  birth_place      jsonb,              -- {country, city, lat, lon}
  input_policy     jsonb NOT NULL,     -- 절기/태양시/야자시 정책 버전
  compiled_core    jsonb NOT NULL,     -- pillars, hidden_stems, etc.
  compiled_features jsonb NOT NULL,    -- element_balance, ten_gods, relations...
  created_at       timestamptz NOT NULL DEFAULT now(),

  UNIQUE(user_id, profile_label)
);

-- fortune_timeline: 대운/세운/월운 등 시간축 계수(사전 계산 캐시)
CREATE TABLE fortune_timeline (
  id          uuid PRIMARY KEY,
  chart_id    uuid NOT NULL REFERENCES chart(id),
  timeline_type text NOT NULL,  -- 'daewoon'|'sewoon'|'monthly'|'weekly'
  start_date  date NOT NULL,
  end_date    date NOT NULL,
  factors     jsonb NOT NULL,   -- luck modifiers, relations vs natal, etc.
  version     text NOT NULL,    -- 룰 엔진 버전
  created_at  timestamptz NOT NULL DEFAULT now(),

  INDEX (chart_id, timeline_type, start_date)
);

-- simulation_run: "한 번의 시뮬레이션" 메타
CREATE TABLE simulation_run (
  id              uuid PRIMARY KEY,
  user_id         uuid NOT NULL REFERENCES "user"(id),
  run_type        text NOT NULL,   -- 'solo'|'synastry'|'team'
  charts          jsonb NOT NULL,  -- 참여 차트 ID 리스트 + 역할
  horizon         jsonb NOT NULL,  -- {year:2026, mode:'monthly+weekly'}
  status          text NOT NULL,   -- queued|running|completed|failed
  cost_estimate   jsonb,           -- 토큰/시간 추정(과금·제한)
  started_at      timestamptz,
  completed_at    timestamptz,
  created_at      timestamptz NOT NULL DEFAULT now(),
  error           text
);

-- event_log: 사건(유의미 이벤트 + 원본 로그/중간 상태) 저장
CREATE TABLE event_log (
  id              uuid PRIMARY KEY,
  simulation_run_id uuid NOT NULL REFERENCES simulation_run(id),
  occurred_at     timestamptz NOT NULL,
  time_bucket     text NOT NULL,   -- '2026-09' 같은 월 버킷
  event_type      text NOT NULL,
  actors          jsonb NOT NULL,   -- {self, other, npc, env}
  cause_features  jsonb NOT NULL,   -- 합충/십성/오행/월운 계수 등 근거
  impact_vector   jsonb NOT NULL,   -- {wealth:+12, health:-5, ...}
  confidence      real NOT NULL,    -- 0..1
  importance      real NOT NULL,    -- 0..1
  narrative       text,             -- 사용자 노출용 1~3문장(캐시)
  raw_payload     jsonb,            -- 필요시 원시 로그(디버깅/회귀)
  created_at      timestamptz NOT NULL DEFAULT now(),

  INDEX (simulation_run_id, time_bucket, importance DESC),
  INDEX (event_type, occurred_at)
);

-- report_section: 보고서 섹션 + 페이월 연결
CREATE TABLE report_section (
  id              uuid PRIMARY KEY,
  simulation_run_id uuid NOT NULL REFERENCES simulation_run(id),
  section_key     text NOT NULL,    -- 'year_overview','career','love',...
  title           text NOT NULL,
  content_free    text,             -- 무료 티저
  content_paid    text,             -- 유료 전체
  evidence_cards  jsonb,            -- 근거 카드(룰/이벤트/참조)
  paywall_gate    jsonb,            -- {requires:'subscription_pro'|purchase_id...}
  created_at      timestamptz NOT NULL DEFAULT now(),

  UNIQUE(simulation_run_id, section_key)
);

-- billing: 구독/단건 결제(결제대행사 이벤트도 저장)
CREATE TABLE billing (
  id            uuid PRIMARY KEY,
  user_id       uuid NOT NULL REFERENCES "user"(id),
  billing_type  text NOT NULL,   -- 'subscription'|'one_off'
  plan_code     text,            -- 'basic','pro', etc
  status        text NOT NULL,   -- active|canceled|past_due|refunded...
  provider      text NOT NULL,   -- 'stripe'|'toss'|'iamport' 등
  provider_ref  text,            -- 외부 결제 ID
  current_period_start timestamptz,
  current_period_end   timestamptz,
  created_at    timestamptz NOT NULL DEFAULT now()
);

-- feedback: 백테스트 라벨/만족도/정확도 평가
CREATE TABLE feedback (
  id              uuid PRIMARY KEY,
  user_id         uuid NOT NULL REFERENCES "user"(id),
  chart_id        uuid REFERENCES chart(id),
  simulation_run_id uuid REFERENCES simulation_run(id),
  feedback_type   text NOT NULL,    -- 'backtest_label'|'rating'|'bug'
  payload         jsonb NOT NULL,   -- 월별 발생 여부/강도/메모 등
  created_at      timestamptz NOT NULL DEFAULT now(),

  INDEX (feedback_type, created_at)
);
SQLAlchemy async 사용 시 주의점
FastAPI로 async DB를 붙일 경우 SQLAlchemy의 create_async_engine/AsyncSession을 사용하게 되는데, 문서에서는 AsyncSession이 “동기 Session의 얇은 프록시이며, 여러 asyncio task에서 동시에 하나를 공유하면 안전하지 않다”고 명시합니다. 

따라서 요청 스코프 세션 관리가 중요합니다.

제품·수익화 전략과 리스크 관리
UI/UX를 “텍스트 운세”가 아니라 “다이내믹 시뮬레이터”로 보이게 만드는 핵심
MiroFish가 시뮬레이션 행동을 로그(action)로 누적하고 최근 행동을 유지하는 구조는, “실시간으로 움직이는 세계” 감각을 만들기 좋은 재료입니다. 

이를 사주 서비스에 맞게 전환하면, UI에서 핵심은 텍스트가 아니라 대시보드 + 타임라인 + 게이지 + 근거 카드 조합입니다.

권장 UI 구성(제안):

연간 타임라인(12칸): 월별 “긴장도/기회도” 히트맵 + 클릭 시 사건 카드
4대 게이지: 건강/재물/관계/커리어(기본 무료는 변화 방향만, 유료는 원인/회피 루트까지)
근거 카드: “이번 달 재물 변동성↑(근거: 월운 계수 + 충돌룰 + 최근 감정 동기화)” 같은 형태로, 설명 가능한 AI 느낌을 강화
분기 비교: Q1~Q4 관점을 보여주면 “결정(이직/투자/결혼)”과 연결이 쉬움
페이월 위치: 가장 흥미로운 “클라이맥스 카드(예: 9월 충돌/손실 위험)”에서 “원인 분석+회피 시뮬”을 잠그기
결제가 가장 잘 터질 문제군과 근거
운세 앱/플랫폼은 통상 “연애/재물/커리어” 축을 강하게 전면에 둡니다. 예를 들어 포스텔러 소개는 “재물운, 연애운” 및 “월운 흐름” 같은 주제별 상세 풀이를 강조합니다. 

또한 FGI 인터뷰에서 “여성들도 큰 고민으로 취업·재물·커리어를 꼽는다”는 취지의 언급이 보도에 포함됩니다. 

따라서 “전환율 관점”에서 우선순위를 제안하면:

이직/커리어: 의사결정 긴급성(일정/면접/퇴사)이 있고, 결과 불확실성이 커서 결제 명분이 강함. (시장 콘텐츠가 커리어를 전면에 둠) 
연애/궁합: 반복 사용(관계 변동/재회/결혼)이 많고, “다중 명식” 기능으로 업셀링이 용이
재물/투자: 강력하지만 법적·윤리적 문구(투자 자문 오해 방지) 설계가 중요
건강·시험도 유의미하지만, “다이내믹 시뮬레이터” USP를 살리려면 **결정이 필요한 갈림길(이직/연애/동업/이사)**가 더 적합합니다.

무료/유료 경계 설계
국내 운세 서비스는 “신년운세/다양한 콘텐츠 무료 제공”으로 트래픽을 모으는 전략이 널리 보입니다. 

권장 경계(제안):

무료: 명식 요약(오행/십성 분포), 연간 월별 히트맵(티저), “상위 3개 사건 카드”
유료 구독: 월별 사건 상세 + 근거 카드 + “회피 루트 시뮬(대안 3가지)”
단건 결제:
궁합/동업 시뮬(다중 명식)
과거연도 백테스트(연간 리포트)
공유용 이미지 패키지(스토리 카드 자동 생성)
공유용 요약 이미지와 바이럴 루프
공유 이미지는 “나만의 결과를 보여주고 싶은 욕구”를 이용합니다. 설계 포인트는 개인정보 유출을 막으면서도 자랑거리를 주는 것입니다.

공유 카드 구성(제안)
“2026 내가 가장 위험한 달 TOP1” (월만 공개, 날짜/구체 사건은 숨김)
“내 오행 밸런스 레이더(아이콘화)”
“이번 해의 키워드 3개”
워터마크 + 링크(초대 코드)
생성 방식(제안)
서버: HTML 템플릿 → headless 렌더(PNG) → CDN 캐시
또는 클라이언트: Canvas 렌더(비용 0, 다만 폰 기기별 품질 조정 필요)
바이럴 루프(제안)
공유한 사람이 유입을 만들면: “다중 명식 1회 무료” 같은 리워드
악용 시나리오 방어
악용 유형은 “유명인/타인 생년월일 입력 + 자극적 결과 유포”입니다. 사주 입력은 개인 정보 맥락에서 문제될 수 있습니다. 

대응(제안):

입력 권한 모델: “본인”은 무료, “타인”은 본인 동의 체크 + 관계(연인/동업) 선택 + 최소한의 확인(예: 상대가 초대 링크로 동의)
공유 제한: 타인 데이터 포함 리포트는 공유 카드 자동 비활성화(또는 익명화 강제)
유명인 패턴 탐지: 유명인 이름/직업 키워드가 포함되면 “엔터테인먼트 목적” 고지 강화 + 유해 표현 필터
약관/면책: “오락/자기성찰 목적, 의료·법률·투자 자문 아님”과 “타인 정보 무단 입력 금지” 조항을 강하게
B2B 확장 가능성: 팀 궁합/채용/협업 리스크 분석
여기서 “법적·윤리적 리스크”가 급격히 커집니다.

개인정보 측면: 출생정보는 개인과 결부되면 개인정보로 취급될 수 있고, 정부 사이트에서도 생년월일을 개인정보 예시로 듭니다. 
채용 절차 측면(한국): 채용 절차에서 직무와 무관한 정보 요구를 제한하는 취지의 정책 안내가 있으며, 금지되는 개인정보 항목을 예시로 듭니다. 
AI 채용의 공정성 이슈(한국): 고용노동부는 AI 채용 관련 조사 결과에서 구직자들이 공정성·불투명성 등을 우려하며 “정확성/편향성 검증, 사전고지” 필요를 응답했다고 밝힙니다. 
EU 규제 관점: European Union의 AI Act 계열 정리 문서에서 고용/채용 영역의 AI가 “high-risk”로 분류될 수 있음을 Annex III에서 언급합니다. 
따라서 “채용/평가/승진/해고” 같은 의사결정에 사주 기반 분석을 붙이는 것은 사업성보다 리스크가 더 앞서는 선택이 될 가능성이 큽니다(국가·지역 확장 시 규제 리스크 누적). 

현실적인 B2B는 아래처럼 “의사결정 도구”가 아니라 “팀 커뮤니케이션/온보딩/팀빌딩 콘텐츠”로 포지셔닝하는 편이 안전합니다(제안).

팀 워크숍용 “케미스트리 리포트”(익명화/집계 기반)
개인 성향을 “대화 스타일/갈등 트리거”로 번역한 커뮤니케이션 가이드
단, 채용 선발/탈락 판단에 사용 금지를 계약/약관과 제품 UI에 강제(체크박스/로그)
사용자 일기·감정 입력을 반영하는 현실 동기화 루프
감정 일기 앱 시장성 연구는 “정신건강/정서적 웰빙 관심 증가”와 함께 감정 기반 서비스 수요를 언급합니다. 

이걸 사주 시뮬레이터에 붙이면 “운(運)→현실 체감”을 연결하는 중요한 신호가 됩니다.

동기화 루프(제안):

매일 10초 입력: 기분(이모지) + 스트레스/수면/지출/갈등 여부
시스템은 다음을 업데이트:
상태머신의 resources(특히 건강/멘탈)
다음 월/주 이벤트 민감도(예: 스트레스가 높으면 관계 충돌 이벤트 확률↑)
장기적으로는 “사용자 체감 라벨(좋았던 시기/힘든 시기)”이 백테스트 데이터가 됨
점성술/타로까지 붙이는 플러그인형 아키텍처
포스텔러 같은 앱은 사주뿐 아니라 점성술/타로/주역 등 다장르를 함께 제공한다고 설명합니다. 

이런 확장을 위해서는 “코어 시뮬레이터”와 “운명학 엔진”을 분리한 플러그인 구조가 필요합니다.

플러그인 설계(제안):

DivinationPlugin 인터페이스
compile(input)->core_model
timeline(core_model, horizon)->timeline_factors
rules(core_model, timeline)->event_candidates
explain(event)->evidence_cards
출력 표준화
모든 플러그인은 “impact_vector(재물/건강/관계/커리어)”로 귀결
다르면 비교 불가/대시보드 불가
이렇게 하면 사주/점성술/타로가 내부적으로 다르더라도, UI/결제/로그는 공통으로 재사용됩니다.

지금 당장 다시 돌리기 좋은 우선순위 다섯 가지
요청하신 “핵심 5개”를 기준으로, 지금 바로 재딥리서치/프로토타입을 돌릴 때 ROI가 높은 순서 제안입니다.

사주 규칙 정량화 데이터 모델 확정: 오행/십성/합충/월운을 어떤 숫자·스키마로 저장할지부터 확정(이게 나머지 전부의 기반). 
이벤트 로그 스키마 + ‘유의미 사건’ 추출기: 보고서/페이월/백테스트/추천까지 한 번에 관통. (MiroFish도 로그 기반 흐름이 핵심) 
시간축 매핑 MVP: “월 단위(기본) + 주 단위 확대(프리미엄)” 형태로 타임라인 엔진을 먼저 고정. 
FastAPI + WebSocket 스트리밍 백본 구축: 실시간 시뮬레이터로 보이게 만드는 기술적 기반. 
무료/유료 경계와 페이월 UX 프로토타입: “클라이맥스 카드에서 해금”이 실제 전환을 좌우. (시장도 무료 콘텐츠로 유입을 먼저 잡는 경향) 