"""
엑셀 파일에서 동물병원 데이터를 수집하는 유즈케이스
"""
from typing import List, Dict, Any, Optional

from src.domain.entity import VetHospital
from src.domain.repository import VetHospitalRepository, AdministrativeDongRepository
from src.infrastructure.excel_repository import ExcelRepository


class CollectExcelHospitalsUseCase:
    """엑셀 파일에서 동물병원 데이터를 수집하는 유즈케이스"""
    
    def __init__(
        self,
        vet_hospital_repository: VetHospitalRepository,
        dong_repository: AdministrativeDongRepository,
        excel_repository: Optional[ExcelRepository] = None,
        excel_path: str = None
    ):
        """
        엑셀 파일 기반 동물병원 데이터 수집 유즈케이스 초기화
        
        Args:
            vet_hospital_repository: 동물병원 레포지토리
            dong_repository: 행정동 레포지토리
            excel_repository: 엑셀 레포지토리 (없으면 자동 생성)
            excel_path: 엑셀 파일 경로 (excel_repository가 None일 때만 사용)
        """
        self.vet_hospital_repository = vet_hospital_repository
        self.dong_repository = dong_repository
        
        if excel_repository is None and excel_path:
            self.excel_repository = ExcelRepository(excel_path)
        else:
            self.excel_repository = excel_repository
            
        if self.excel_repository is None:
            raise ValueError("엑셀 레포지토리 또는 엑셀 파일 경로가 필요합니다")
    
    def execute(self, city: str = "부산") -> List[VetHospital]:
        """
        엑셀 파일에서 동물병원 데이터 수집 및 가공 실행
        
        Args:
            city: 도시 이름 (예: "부산")
            
        Returns:
            처리된 동물병원 목록
        """
        # 1. 엑셀 파일에서 특정 도시의 동물병원 데이터 로드
        print(f"엑셀 파일에서 {city} 동물병원 데이터 수집 중...")
        hospitals = self.excel_repository.load_hospitals(city=city)
        
        # 2. 수집된 병원 정보 로깅
        print(f"\n=== 수집된 전체 동물병원 개수: {len(hospitals)} ====")
        print(f"\n=== 주소 예시(10개) ====")
        for i, h in enumerate(hospitals[:10]):
            print(f"{i+1}. {h.name}: {h.address}")
        
        # 3. 좌표가 있는 병원만 필터링
        hospitals_with_coords = [h for h in hospitals if h.latitude is not None and h.longitude is not None]
        if len(hospitals_with_coords) < len(hospitals):
            print(f"\n좌표가 없는 병원 {len(hospitals) - len(hospitals_with_coords)}개가 필터링되었습니다.")
        
        # 4. 행정동 정보와 공간 조인
        hospitals_dict = [self._hospital_to_dict(h) for h in hospitals_with_coords]
        joined = self.dong_repository.spatial_join_hospitals(hospitals_dict)
        print(f"\n=== 공간조인 결과 회수: {len(joined)} ====")
        
        # 5. 행정동 정보 추가
        for hospital in hospitals_with_coords:
            hospital_joined = joined[joined["id"] == hospital.id]
            
            # 공간조인 결과가 있는 경우
            if not hospital_joined.empty:
                dong_code = hospital_joined.iloc[0].get("ADM_CD")
                dong_name = hospital_joined.iloc[0].get("ADM_NM")
                hospital.dong_code = dong_code
                hospital.dong_name = dong_name
        
        # 6. 기존 부산 필터링은 이미 city 파라미터로 수행됐으므로 생략
        print(f"\n=== {city} 동물병원 예시(10개) ====")
        for i, h in enumerate(hospitals_with_coords[:10]):
            print(f"{i+1}. {h.name}: {h.address} (동코드: {h.dong_code}, 동명: {h.dong_name})")
        
        # 7. 레포지토리에 저장
        self.vet_hospital_repository.save_hospitals(hospitals_with_coords)
        print(f"총 {len(hospitals_with_coords)}개 동물병원 데이터 수집 완료")
        
        return hospitals_with_coords
    
    def _hospital_to_dict(self, hospital: VetHospital) -> Dict[str, Any]:
        """VetHospital 객체를 딕셔너리로 변환"""
        return {
            "id": hospital.id,
            "name": hospital.name,
            "address": hospital.address,
            "latitude": hospital.latitude,
            "longitude": hospital.longitude,
            "phone": hospital.phone,
            "place_url": hospital.place_url,
            "dong_code": hospital.dong_code,
            "dong_name": hospital.dong_name
        }
