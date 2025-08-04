# 📊 Data ETL API

FastAPI를 사용하여 **EIU, 관세청, 사회경제지수 데이터**를 수집·가공·적재하는 ETL 시스템

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![UV](https://img.shields.io/badge/UV-Package%20Manager-orange.svg)

## 🏠 프로젝트 개요

이 프로젝트는 **9가지 경제 및 무역 데이터를 자동으로 처리하는 ETL 시스템**입니다. 
웹 대시보드에서 Excel/CSV 파일을 업로드하면 데이터 품질 검증, 국가명 표준화, 데이터 적재까지 자동으로 처리합니다.

![Admin Dashboard](docs/images/dashboard-main.png)
*▲ Data ETL API Admin 대시보드 - 파일 업로드부터 처리 이력 관리까지 한 화면에서*

### 주요 목적
- 📈 **다중 경제지표 통합 관리**: EIU 경제지표부터 사회경제지수까지 한 곳에서 관리
- 🔄 **파일 기반 ETL 자동화**: Excel/CSV 업로드만으로 전체 프로세스 자동 실행
- 🌐 **지능형 국가명 매핑**: 영문/한글/ISO코드 간 자동 변환 및 표준화
- 📊 **이력 관리 시스템**: 모든 처리 과정을 추적하고 재처리 가능

## ✨ 주요 특징

### 🔥 핵심 기능
- **🗂️ 9가지 데이터 타입 지원**: 
  - **EIU**: 주요 경제지표, 주요 수출/수입국
  - **관세청**: 국가별 수출입규모, 주요 수출/수입품 (수출/수입 구분)
  - **사회경제지수**: 부패인식지수, 경제자유화지수, 인간개발지수, 세계경쟁력지수
- **🤖 지능형 국가명 매핑**: 영문/한글/ISO 코드 간 자동 변환
- **🛡️ 데이터 품질 검증**: 빈값, 형식 오류, 이상치 자동 감지 및 처리
- **📱 웹 기반 관리**: 파일 업로드부터 실행까지 원클릭 처리
- **📋 이력 관리**: 모든 처리 기록 추적 및 재처리 기능
- **⚡ 비동기 처리**: 대용량 Excel 파일 고속 처리

### 🎯 기술적 특징
- **RESTful API**: 표준화된 API 인터페이스
- **Docker 컨테이너화**: 환경 독립적 배포
- **MariaDB 연동**: 안정적인 데이터 저장
- **실시간 모니터링**: 처리 상태 실시간 확인

## 🛠 기술 스택

### Backend
- **Python 3.9+** - 메인 개발 언어
- **FastAPI** - 고성능 웹 프레임워크  
- **UV** - 빠른 Python 패키지 매니저
- **SQLAlchemy 2.0** - ORM 및 데이터베이스 추상화
- **Pydantic** - 데이터 검증 및 시리얼라이제이션
- **Pandas** - Excel/CSV 파일 처리 및 데이터 분석

### Database
- **MariaDB 11.4** - 메인 데이터베이스
- **aiomysql** - 비동기 MySQL 드라이버

### Infrastructure
- **Docker & Docker Compose** - 컨테이너화 및 오케스트레이션
- **Uvicorn** - ASGI 서버
- **Loguru** - 구조화된 로깅

### Frontend
- **Jinja2 Templates** - 서버사이드 렌더링
- **HTML5 + CSS3** - 반응형 Admin 대시보드
- **Vanilla JavaScript** - 파일 업로드 및 API 연동

## 📊 지원 데이터 타입

### 1. EIU (Economist Intelligence Unit) 
- **주요 경제지표**: GDP 성장률, 인플레이션, 환율 등 핵심 경제 지표
- **주요 수출/수입국**: 국가별 무역 파트너 분석 데이터
- **특징**: 실제/예측 데이터 구분, 경제 전망 포함

### 2. 관세청 데이터
- **국가별 수출입규모**: 국가별 총 수출입 금액 및 무역수지
- **주요 수출/수입품**: 품목별 수출실적 및 수입실적 (수출/수입 구분 처리)
- **출처**: [관세청 통계포털](https://unipass.customs.go.kr/ets/)
- **특징**: 한글 국가명, 복잡한 HS 코드 체계

### 3. 사회경제지수 데이터
- **부패인식지수**: [Transparency International CPI](https://www.transparency.org/en/cpi)
- **경제자유화지수**: [Heritage Foundation](https://www.heritage.org/index/)  
- **인간개발지수**: [UNDP HDI](https://hdr.undp.org/data-center)
- **세계경쟁력지수**: [World Economic Forum](https://www.weforum.org/reports/)
- **특징**: 영문 국가명, 순위 기반 데이터

## 🚀 빠른 시작

### 사전 요구사항
- Docker & Docker Compose
- 8090, 3306 포트 사용 가능

### 1. 프로젝트 복제
```bash
git clone https://github.com/your-repo/data-etl-api.git
cd data-etl-api
```

### 2. 환경 설정
```bash
# 환경변수 파일 생성 (선택사항)
cp .env.example .env
```

### 3. 시스템 실행
```bash
# Docker Compose로 전체 시스템 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f fastapi
```

### 4. 접속 확인
- **API 서버**: http://localhost:8090
- **Admin 대시보드**: http://localhost:8090/admin/
- **API 문서**: http://localhost:8090/docs
- **헬스체크**: http://localhost:8090/health

## 📁 프로젝트 구조

```
data-etl-api/
├── app/
│   ├── core/                    # 핵심 설정
│   │   ├── constants/           # 데이터 타입별 설정 (customs.py, eiu.py, socioeconomic.py)
│   │   ├── logger.py           # 로깅 설정
│   │   └── setting.py          # 환경 설정
│   ├── db/                     # 데이터베이스 관련
│   │   └── database.py         # DB 연결 및 세션
│   ├── endpoints/              # API 엔드포인트
│   │   ├── admin.py           # 관리자 대시보드 + API
│   │   ├── customs.py         # 관세청 데이터 처리 API
│   │   ├── eiu.py             # EIU 데이터 처리 API  
│   │   └── socioeconomic.py   # 사회경제지수 처리 API
│   ├── models/                 # 데이터베이스 모델
│   │   ├── customs.py         # 관세청 테이블 모델
│   │   ├── EIU.py             # EIU 테이블 모델
│   │   ├── socioeconomic.py   # 사회경제지수 모델
│   │   ├── history.py         # 처리 이력 모델
│   │   └── shared_models.py   # 공통 모델 (국가 정보 등)
│   ├── repositories/           # 데이터 접근 계층
│   ├── schemas/               # Pydantic 스키마
│   │   └── admin_schemas.py   # 작업 타입 매핑 및 API 스키마
│   ├── services/              # 비즈니스 로직
│   │   ├── *_service.py       # 각 데이터 타입별 처리 서비스
│   │   ├── *.ipynb           # 개발용 Jupyter 노트북
│   │   ├── file_service.py    # 파일 업로드/관리
│   │   └── history_service.py # 처리 이력 관리
│   ├── static/                # 정적 파일
│   │   ├── admin/             # Admin 대시보드 CSS/JS
│   │   └── uploads/           # 업로드된 파일 저장
│   ├── templates/             # Jinja2 HTML 템플릿
│   │   └── admin/             # 관리자 대시보드 템플릿
│   └── utils/                 # 유틸리티 함수
├── docker-compose.yml         # Docker 설정 (MariaDB + FastAPI)
├── Dockerfile                 # FastAPI 컨테이너 (UV 사용)
├── main.py                   # 애플리케이션 진입점
├── requirements.txt          # Python 의존성
└── README.md                # 프로젝트 문서
```

## 🔧 설정 및 환경변수

### 환경변수 설정
`.env` 파일을 생성하여 다음 설정을 커스터마이징할 수 있습니다:

```bash
# 애플리케이션 설정
APP_NAME=Data ETL API
DEBUG=false
VERSION=1.0.0
DESCRIPTION=EIU, 관세청, 사회경제지수 데이터 ETL API

# 데이터베이스 설정 (선택사항)
DATABASE=your_custom_database_url

# 로깅 설정
LOG_DIR=app/logs
LOG_LEVEL=INFO
LOG_FORMAT=<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <yellow>PID:{process}</yellow> | <cyan>"{name}"</cyan>, <cyan>{function}</cyan>, <cyan>{line}</cyan> : <level>{message}</level>
DATE_FORMAT=%Y/%m/%d %H:%M:%S

# 파일 처리 설정
CSV_OUTPUT_DIR=/storage/research/final
CSV_OUPUT_ENCOFING=utf-8
CSV_OUPUT_NA_REP=NULL
```

> **참고**: 대부분의 설정은 기본값으로 충분하며, 필요에 따라 일부만 오버라이드하면 됩니다.

### Docker Compose 커스터마이징
```yaml
# docker-compose.override.yml 예시
services:
  fastapi:
    ports:
      - "8091:8090"  # 포트 변경
    environment:
      - DEBUG=true   # 개발 모드
  
  mariadb:
    ports:
      - "3307:3306"  # MySQL 포트 변경
```

## 📚 API 문서

### Swagger UI
- **URL**: http://localhost:8090/docs
- **기능**: 모든 API 엔드포인트 테스트 가능

### 주요 API 엔드포인트

#### 1. 시스템 관리
```http
GET  /health                           # 헬스체크
GET  /                                # 시스템 정보
```

#### 2. Admin 대시보드 및 관리
```http
GET  /admin/                          # 관리자 대시보드 (HTML)
GET  /admin/api/history               # 처리 이력 조회
POST /admin/api/upload                # 파일 업로드 + 작업 등록
POST /admin/api/execute/{file_seq}    # 파일 처리 실행
GET  /admin/api/files                 # 업로드된 파일 목록
DELETE /admin/api/files/{filename}    # 파일 삭제
DELETE /admin/api/history/{file_seq}/{data_wrk_nm} # 이력 삭제
```

#### 3. 데이터 처리 (Internal APIs)
```http
POST /eiu/economic-indicator          # EIU 경제지표 처리
POST /eiu/major-trade-partner         # EIU 주요 수출입국 처리
POST /customs/trade/country           # 관세청 국가별 수출입 처리
POST /customs/trade/item-country/export # 관세청 품목별 수출 처리
POST /customs/trade/item-country/import # 관세청 품목별 수입 처리
POST /socioeconomic-index/corruption-perception    # 부패인식지수 처리
POST /socioeconomic-index/economic-freedom         # 경제자유화지수 처리
POST /socioeconomic-index/human-development        # 인간개발지수 처리
POST /socioeconomic-index/world-competitiveness   # 세계경쟁력지수 처리
```

### API 사용 예시
```python
import requests

# 1. 파일 업로드 (작업 유형과 함께)
files = {'file': open('customs_data.xlsx', 'rb')}
data = {'job_type': '국가별 수출입규모(관세청)'}

upload_response = requests.post(
    'http://localhost:8090/admin/api/upload',
    files=files,
    data=data
)

# 2. 업로드된 파일 처리 실행
file_seq = upload_response.json()['file_seq']
execute_response = requests.post(
    f'http://localhost:8090/admin/api/execute/{file_seq}'
)

print(execute_response.json())
```

## 💻 Admin 대시보드

### 접속 방법
1. 브라우저에서 http://localhost:8090/admin/ 접속
2. 직관적인 웹 인터페이스를 통한 시스템 관리

### 주요 기능

#### 📤 파일 업로드 및 작업 등록
- **지원 형식**: Excel (.xlsx, .xls), CSV
- **9가지 작업 유형**: 드롭다운에서 선택
  - 주요 경제지표(EIU) / 주요 수출/수입국(EIU)
  - 국가별 수출입규모(관세청) / 주요 수출/수입품(관세청) - 수출실적/수입실적
  - 부패인식지수 / 경제자유화지수 / 인간개발지수 / 세계경쟁력지수
- **실시간 검증**: 파일 크기 (최대 10MB), 형식 확인
- **History 자동 등록**: 업로드와 동시에 작업 이력 생성

#### 🚀 원클릭 처리 시스템
- **Execute 버튼**: 업로드된 파일을 선택해서 즉시 처리 실행
- **자동 라우팅**: 작업 유형에 따라 해당 처리 엔드포인트로 자동 전달
- **실시간 결과**: 처리 성공/실패 즉시 확인

#### 📋 완전한 이력 관리
- **모든 처리 기록**: 파일 업로드부터 처리 완료까지 전 과정 추적
- **상세 정보**: 파일명, 크기, 처리 시간, 처리 건수, 결과 메시지
- **재처리 기능**: 실패한 작업을 언제든 다시 실행 가능
- **삭제 기능**: 불필요한 파일과 이력 정리

## 🔄 데이터 처리 워크플로우

### 1. 파일 업로드 및 등록 단계
```
📁 Excel/CSV 파일 업로드 + 작업 유형 선택
    ↓
🔍 파일 검증 (형식, 크기 10MB 제한)
    ↓
💾 /appdata/storage에 파일 저장
    ↓
📋 History 테이블에 작업 정보 등록 (file_seq 생성)
    ↓
✅ 업로드 완료 (파일이 실행 대기 상태)
```

### 2. 작업 실행 단계
```
🚀 Execute 버튼 클릭 (file_seq 기준)
    ↓
📋 History에서 작업 유형 조회
    ↓
🔄 해당 작업 유형의 처리 엔드포인트 호출
    ↓
📊 Excel/CSV 파일 파싱 및 데이터 로드
```

### 3. 데이터 처리 단계
```
🧹 데이터 품질 검증
    ├── 필수 컬럼 존재 확인
    ├── 빈값/형식 오류 처리
    └── 데이터 타입 변환
    ↓
🗺️ 국가명 표준화 (작업 유형별 매핑 테이블 사용)
    ├── 한글 국가명 → ISO 코드 (관세청 데이터)
    ├── 영문 국가명 → ISO 코드 (사회경제지수)
    └── ISO 코드 → 표준 국가명
    ↓
🎯 최종 스키마로 변환 (작업 유형별 컬럼 매핑)
```

### 4. 데이터 적재 및 완료 단계
```
🗄️ 데이터베이스 트랜잭션 시작
    ↓
💾 해당 테이블에 배치 삽입 (pandas to_sql 사용)
    ↓
✅ 트랜잭션 커밋
    ↓
📝 History 테이블 업데이트 (처리 완료, 결과 메시지)
    ↓
🎉 Admin 대시보드에서 결과 확인 가능
```

### 국가명 매핑 프로세스
```mermaid
graph LR
    A[원천 국가명] --> B{매핑 테이블 조회}
    B -->|성공| C[ISO 코드 획득]
    B -->|실패| D[매핑 실패 로그]
    C --> E[표준 국가명 변환]
    E --> F[최종 데이터 생성]
    D --> G[수동 확인 필요]
```

## 🐛 트러블슈팅

### 자주 발생하는 문제와 해결책

#### 1. 컨테이너 실행 오류
```bash
# 문제: 포트 충돌
Error: Port 8090 is already in use

# 해결책: 포트 변경
docker-compose down
# docker-compose.yml에서 포트 수정 후
docker-compose up -d
```

#### 2. 데이터베이스 연결 실패
```bash
# 문제: MariaDB 컨테이너 미실행
sqlalchemy.exc.OperationalError: Can't connect to MySQL server

# 해결책: 컨테이너 상태 확인
docker-compose ps
docker-compose logs mariadb

# 데이터베이스 초기화
docker-compose down -v
docker-compose up -d
```

#### 3. 파일 업로드 오류
```bash
# 문제: 파일 크기 제한 초과 (현재 10MB 제한)
413 Request Entity Too Large

# 해결책: 코드에서 크기 제한 수정 (app/endpoints/admin.py)
# 또는 더 작은 파일 사용
```

#### 4. 국가명 매핑 실패
```bash
# 문제: 매핑되지 않은 국가명
Country mapping failed for: "대한민국 (Republic of Korea)"

# 해결책: 국가명 매핑 테이블 업데이트
# 1. Admin 대시보드에서 매핑 실패 로그 확인
# 2. 새로운 매핑 규칙 추가
# 3. 데이터 재처리
```

#### 5. 메모리 부족 오류
```bash
# 문제: 대용량 파일 처리 시 메모리 부족
MemoryError: Unable to allocate array

# 해결책: 청크 단위 처리 활성화
CHUNK_SIZE=1000  # 환경변수 추가
```

### 로그 확인 방법
```bash
# 실시간 로그 모니터링
docker-compose logs -f fastapi

# 특정 시간대 로그 확인
docker-compose logs --since="2024-01-01T00:00:00" fastapi

# 로그 파일 직접 확인
docker exec -it data-etl-api tail -f /app/logs/app.log
```

### 시스템 상태 확인
```bash
# 헬스체크 API 호출
curl http://localhost:8090/health

# 데이터베이스 연결 확인
curl http://localhost:8090/admin/status

# 컨테이너 리소스 사용량 확인
docker stats data-etl-api data-etl-mariadb
```

## ⚠️ 에러 처리

### 시스템 레벨 에러 처리

#### 1. API 응답 표준화
모든 API 응답은 다음 형태로 표준화됩니다:
```json
{
  "success": "true|false",
  "error_code": "ERROR_CODE",
  "message": "사용자 친화적 메시지",
  "detail": "상세 정보 (선택적)"
}
```

#### 2. 주요 에러 코드
- `INVALID_REQUEST_PARAMETER`: 요청 파라미터 오류
- `FILE_UPLOAD_ERROR`: 파일 업로드 실패
- `DATA_PROCESSING_ERROR`: 데이터 처리 중 오류
- `DATABASE_ERROR`: 데이터베이스 관련 오류
- `SYSTEM_ERROR`: 예상치 못한 시스템 오류

#### 3. 데이터 처리 에러 핸들링
```python
# 국가명 매핑 실패 시
if country_code is None:
    logger.warning(f"Country mapping failed: {country_name}")
    # 데이터 스킵하되 전체 처리는 계속 진행

# 필수 데이터 누락 시
if required_field is None:
    raise DataProcessingError(
        "Required field missing",
        detail={"field": "country_name", "row": row_index}
    )
```

#### 4. 로깅 및 모니터링
- **구조화된 로깅**: JSON 형태로 모든 에러 상세 정보 기록
- **에러 알림**: 치명적 오류 발생 시 관리자 알림
- **복구 메커니즘**: 일시적 오류에 대한 자동 재시도

---
