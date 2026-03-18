# 2026-03-18 — backend 문서 거버넌스 이식 및 구현 상태 반영

## 완료 항목

- `unityctl`의 문서 운영 구조를 `backend/`에 이식
- `backend/docs/ref/`, `backend/docs/status/`, `backend/docs/daily/`, `backend/docs/weekly/` 생성
- `backend/docs/DEVELOPMENT.md` 추가
- `backend/docs/status/PROJECT-STATUS.md` 추가
- `backend/docs/ref/getting-started.md` 추가
- `backend/docs/ref/architecture.md` 추가
- `backend/README.md`를 문서 허브로 추가
- `backend/.gitignore` 추가

## 반영한 운영 원칙

- 장기 설계와 현재 상태를 같은 문서에 섞지 않는다.
- 현재 구현 현황은 `docs/DEVELOPMENT.md`와 `docs/status/PROJECT-STATUS.md`를 우선한다.
- 작업 기록은 날짜별로 `docs/daily/`에 남긴다.
- 새 backend 기능을 추가할 때는 구현과 함께 상태 문서를 갱신한다.

## 현재 코드 기준 상태 요약

- Python 코어와 FastAPI API 구현 완료
- 11개 pytest 통과
- monthly baseline simulator까지 구현됨
- weekly/branch/debate는 아직 미구현
