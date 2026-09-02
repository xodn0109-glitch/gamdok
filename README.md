# 시험감독 시간표

교사 이름으로 2026년 9월 2일 전국연합학력평가 시험감독 배정을 조회하는 정적 웹앱입니다.

## Codex에서의 기본 작업

Codex는 저장소 최상위의 `AGENTS.md`를 작업 규칙으로 사용합니다. 현재 화면의 데이터 기준 원본은 다음 파일입니다.

저장소 최상위의 9월 2일 전국연합학력평가 PDF

원본을 고친 다음 아래 순서로 실행합니다.

```bash
make build
make check
make serve
```

`make serve`는 기본적으로 `http://localhost:4181`에서 화면을 엽니다. 다른 포트가 필요하면 `make serve PORT=8000`처럼 지정합니다.

## 명령어

| 명령 | 용도 |
| --- | --- |
| `make build` | 기준 PDF에서 `schedule_data.js` 재생성 |
| `make check` | 데이터 형식·필수값·감독 시간 중복 검사 |
| `make serve` | 정적 웹 서버 실행 |
| `make test` | Python/JavaScript 문법 및 데이터 검사 |

`schedule_data.js`는 생성 파일이므로 직접 편집하지 않습니다. HWP/HWPX/XLSX는 원본 증빙 파일이므로 별도 요청 없이 수정하지 않습니다.

## 파일 구성

- `index.html`, `script.js`, `style.css`: 조회 화면
- `parse_supervision_pdf.py`: 현재 기준 PDF를 웹앱 데이터로 변환
- `check_anomalies.py`: 생성 데이터의 구조·시간·중복 배정 검사
- `schedule_data.js`: 웹앱에서 불러오는 생성 데이터
- `AGENTS.md`: Codex 작업 규칙

이전 변환 도구와 목요일 시간표 관련 파일은 보관용으로 유지합니다. 현재 9월 2일 시험감독 화면을 갱신할 때에는 위 기준 PDF와 `parse_supervision_pdf.py`만 사용합니다.
