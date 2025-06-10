# 부산시 행정동별 “강아지 키우기 좋은 동네” 데이터 분석 프로젝트

## 개요
부산시 내 행정동별로 반려견 친화 인프라, 산책로, 교통 접근성 등 다양한 지표를 공간 데이터 기반으로 분석하고, 사용자 가중치 기반 종합 점수 및 시각화 서비스를 제공하는 프로젝트입니다.

## 주요 폴더 구조
- `src/` : 서비스 소스 코드 및 모듈
- `docs/` : 요구사항, 설계, UI, 체크리스트 등 문서
- `data/` : 원본/가공 데이터, 샘플 데이터
- `BND_ADM_DONG_PG/` : 행정동 경계 GIS 데이터(shp)

## 주요 문서
- `docs/requirements.md` : 요구사항 및 기술 스택
- `docs/design.md` : 시스템 설계 문서
- `docs/ui_wireframe.svg` : UI 와이어프레임
- `docs/checklist.md` : 작업 순서 체크리스트

## 개발 환경
- Python 3.11+, FastAPI, PostgreSQL(PostGIS), React, Mapbox GL JS 등
- Docker, GitHub Actions, AWS 배포

## 라이선스
- 본 프로젝트는 MIT 라이선스를 따릅니다.
