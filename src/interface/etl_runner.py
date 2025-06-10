"""
동물병원 데이터 ETL 파이프라인 실행기
"""
import os
import argparse
from dotenv import load_dotenv
from typing import List

from src.domain.entity import VetHospital
from src.infrastructure.kakao_api import KakaoMapAPI
from src.infrastructure.excel_repository import ExcelRepository
from src.infrastructure.shapefile import ShapefileRepository
from src.infrastructure.vet_hospital_repository import FileVetHospitalRepository
from src.usecase.collect_vet_hospitals import CollectVetHospitalsUseCase
from src.usecase.collect_excel_hospitals import CollectExcelHospitalsUseCase
from src.usecase.visualize_vet_hospitals import VisualizeVetHospitalsUseCase


def run_api_etl_pipeline(shapefile_path: str, city: str = "부산", visualize: bool = True) -> List[VetHospital]:
    """
    카카오맵 API를 활용한 동물병원 데이터 ETL 파이프라인 실행
    
    Args:
        shapefile_path: 행정동 shapefile 경로
        city: 도시 이름 (예: "부산")
        visualize: 시각화 생성 여부
        
    Returns:
        수집된 동물병원 목록
    """
    print(f"=== {city} 동물병원 데이터 ETL 파이프라인 시작 (API 기반) ===")
    
    # 1. 레포지토리 초기화
    print("레포지토리 초기화 중...")
    dong_repository = ShapefileRepository()
    vet_hospital_repository = FileVetHospitalRepository(data_dir="data")
    
    # 2. 행정동 데이터 로드
    print(f"행정동 데이터 로드 중... (파일: {shapefile_path})")
    dongs = dong_repository.load_dongs(shapefile_path)
    print(f"총 {len(dongs)}개 행정동 로드 완료")
    
    # 3. 카카오맵 API 클라이언트 초기화
    print("카카오맵 API 클라이언트 초기화 중...")
    kakao_api = KakaoMapAPI()
    
    # 4. 동물병원 데이터 수집 유즈케이스 실행
    print(f"{city} 동물병원 데이터 수집 중...")
    collect_usecase = CollectVetHospitalsUseCase(
        vet_hospital_repository=vet_hospital_repository,
        dong_repository=dong_repository,
        kakao_api=kakao_api
    )
    hospitals = collect_usecase.execute(city=city)
    print(f"총 {len(hospitals)}개 동물병원 데이터 수집 완료")
    
    return hospitals


def run_excel_etl_pipeline(shapefile_path: str, excel_path: str, city: str = "부산", visualize: bool = True) -> List[VetHospital]:
    """
    엑셀 파일을 활용한 동물병원 데이터 ETL 파이프라인 실행
    
    Args:
        shapefile_path: 행정동 shapefile 경로
        excel_path: 동물병원 엑셀 파일 경로
        city: 도시 이름 (예: "부산")
        visualize: 시각화 생성 여부
        
    Returns:
        수집된 동물병원 목록
    """
    print(f"=== {city} 동물병원 데이터 ETL 파이프라인 시작 (엑셀 기반) ===")
    
    # 1. 레포지토리 초기화
    print("레포지토리 초기화 중...")
    dong_repository = ShapefileRepository()
    vet_hospital_repository = FileVetHospitalRepository(data_dir="data")
    excel_repository = ExcelRepository(excel_path)
    
    # 2. 행정동 데이터 로드
    print(f"행정동 데이터 로드 중... (파일: {shapefile_path})")
    dongs = dong_repository.load_dongs(shapefile_path)
    print(f"총 {len(dongs)}개 행정동 로드 완료")
    
    # 3. 동물병원 데이터 수집 유즈케이스 실행
    print(f"{city} 동물병원 엑셀 데이터 수집 중...")
    collect_usecase = CollectExcelHospitalsUseCase(
        vet_hospital_repository=vet_hospital_repository,
        dong_repository=dong_repository,
        excel_repository=excel_repository
    )
    hospitals = collect_usecase.execute(city=city)
    print(f"총 {len(hospitals)}개 동물병원 데이터 수집 완료")
    
    return hospitals


def run_etl_pipeline(shapefile_path: str, city: str = "부산", visualize: bool = True, 
                    data_source: str = "api", excel_path: str = None) -> None:
    """
    동물병원 데이터 ETL 파이프라인 실행
    
    Args:
        shapefile_path: 행정동 shapefile 경로
        city: 도시 이름 (예: "부산")
        visualize: 시각화 생성 여부
        data_source: 데이터 소스 ("api" 또는 "excel")
        excel_path: 엑셀 파일 경로 (data_source가 "excel"일 때만 사용)
    """
    # 데이터 소스에 따라 적절한 파이프라인 실행
    if data_source == "excel" and excel_path:
        hospitals = run_excel_etl_pipeline(
            shapefile_path=shapefile_path,
            excel_path=excel_path,
            city=city,
            visualize=False  # 시각화는 아래에서 공통으로 처리
        )
    else:  # 기본값은 API
        hospitals = run_api_etl_pipeline(
            shapefile_path=shapefile_path,
            city=city,
            visualize=False  # 시각화는 아래에서 공통으로 처리
        )
    
    # 레포지토리 및 데이터 설정 (공통)
    dong_repository = ShapefileRepository()
    vet_hospital_repository = FileVetHospitalRepository(data_dir="data")
    dongs = dong_repository.load_dongs(shapefile_path)
    
    # 5. 행정동별 동물병원 개수 출력
    hospital_counts = vet_hospital_repository.get_hospitals_count_by_dong()
    print("\n=== 행정동별 동물병원 개수 ===")
    for dong in dongs:
        count = hospital_counts.get(dong.code, 0)
        if count > 0:
            print(f"{dong.name}: {count}개")
    
    # 6. 시각화 생성
    if visualize:
        print("\n=== 시각화 생성 중... ===")
        visualize_usecase = VisualizeVetHospitalsUseCase(
            vet_hospital_repository=vet_hospital_repository,
            dong_repository=dong_repository,
            output_dir="output"
        )
        output_files = visualize_usecase.create_all_visualizations()
        print(f"시각화 파일 {len(output_files)}개 생성 완료:")
        for file_path in output_files:
            print(f"- {file_path}")
    
    print("\n=== ETL 파이프라인 완료 ===")


if __name__ == "__main__":
    # .env 파일에서 환경변수 로드
    load_dotenv()
    
    # 인자 파싱
    parser = argparse.ArgumentParser(description="부산시 동물병원 데이터 ETL 파이프라인")
    parser.add_argument(
        "--shapefile", 
        type=str, 
        default="BND_ADM_DONG_PG/BND_ADM_DONG_PG.shp",
        help="행정동 shapefile 경로"
    )
    parser.add_argument(
        "--city", 
        type=str, 
        default="부산",
        help="도시 이름 (예: '부산')"
    )
    parser.add_argument(
        "--no-visualize", 
        action="store_true",
        help="시각화 생성 비활성화"
    )
    parser.add_argument(
        "--data-source",
        type=str,
        choices=["api", "excel"],
        default="excel",  # 엑셀 파일을 기본값으로 변경
        help="데이터 소스 (api 또는 excel)"
    )
    parser.add_argument(
        "--excel-path",
        type=str,
        default="data/fulldata_02_03_01_P_동물병원.xlsx",
        help="동물병원 엑셀 파일 경로 (--data-source=excel일 때 사용)"
    )
    
    args = parser.parse_args()
    
    # ETL 파이프라인 실행
    run_etl_pipeline(
        shapefile_path=args.shapefile,
        city=args.city,
        visualize=not args.no_visualize,
        data_source=args.data_source,
        excel_path=args.excel_path
    )
