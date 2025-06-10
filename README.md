# 부산시 행정동별 "강아지 키우기 좋은 동네" 데이터 분석 프로젝트

## 개요
부산시 내 행정동별로 반려견 친화 인프라, 산책로, 교통 접근성 등 다양한 지표를 공간 데이터 기반으로 분석하고, 사용자 가중치 기반 종합 점수 및 시각화 서비스를 제공하는 프로젝트입니다.

## 주요 폴더 구조
- `src/` : 서비스 소스 코드 및 모듈
  - `src/domain/` : 도메인 엔티티 및 레포지토리 인터페이스
  - `src/usecase/` : 비즈니스 로직 유즈케이스
  - `src/infrastructure/` : 외부 API 및 데이터 저장소 구현체
  - `src/interface/` : ETL 실행기 및 사용자 인터페이스
- `docs/` : 요구사항, 설계, UI, 체크리스트 등 문서
- `data/` : 원본/가공 데이터, 샘플 데이터
- `output/` : 시각화 결과물 저장 디렉토리
- `tests/` : 테스트 코드
- `BND_ADM_DONG_PG/` : 행정동 경계 GIS 데이터(shp)

## 주요 문서
- `docs/requirements.md` : 요구사항 및 기술 스택
- `docs/design.md` : 시스템 설계 문서
- `docs/ui_wireframe.svg` : UI 와이어프레임
- `docs/checklist.md` : 작업 순서 체크리스트

## 동물병원 ETL 파이프라인

### 기능 개요
- **추출(Extract)**: 카카오맵 API를 통해 부산시 동물병원 위치 데이터 수집
- **변환(Transform)**: 수집된 데이터를 행정동 경계와 공간 조인하여 행정동별 동물병원 매핑
- **적재(Load)**: 처리된 데이터를 JSON, CSV, GeoJSON 형식으로 저장
- **시각화(Visualize)**: 행정동별 동물병원 분포 지도 및 통계 차트 생성

### 설치 및 실행 방법

1. 필요 패키지 설치
```bash
pip install -r requirements.txt
```

2. 환경 변수 설정 (.env 파일 생성)
```
KAKAO_API_KEY=your_kakao_api_key_here
```

3. ETL 파이프라인 실행
```bash
python -m src.interface.etl_runner --shapefile BND_ADM_DONG_PG/BND_ADM_DONG_PG.shp
```

4. 실행 옵션
```bash
# 시각화 비활성화
python -m src.interface.etl_runner --shapefile BND_ADM_DONG_PG/BND_ADM_DONG_PG.shp --no-visualize

# 다른 도시 지정 (기본값: 부산)
python -m src.interface.etl_runner --shapefile BND_ADM_DONG_PG/BND_ADM_DONG_PG.shp --city 부산
```

### 결과물
- `data/vet_hospitals.json`: 동물병원 데이터 (JSON)
- `data/vet_hospitals.csv`: 동물병원 데이터 (CSV)
- `data/vet_hospitals.geojson`: 동물병원 데이터 (GeoJSON)
- `output/vet_hospitals_choropleth.png`: 행정동별 동물병원 수 지도
- `output/vet_hospitals_points.png`: 동물병원 위치 점 지도
- `output/top_dongs_bar_chart.png`: 동물병원 수 상위 행정동 차트
- `output/top_dongs_bar_chart.svg`: 동물병원 수 상위 행정동 차트 (SVG)

## 개발 환경
- Python 3.11+, FastAPI, PostgreSQL(PostGIS), React, Mapbox GL JS 등
- Docker, GitHub Actions, AWS 배포

## 라이선스
- 본 프로젝트는 MIT 라이선스를 따릅니다.
