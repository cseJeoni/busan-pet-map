"""
동물병원 데이터 수집 및 가공 유즈케이스
"""
from typing import List, Dict, Any, Optional

from src.domain.entity import VetHospital
from src.domain.repository import VetHospitalRepository, AdministrativeDongRepository
from src.infrastructure.kakao_api import KakaoMapAPI


class CollectVetHospitalsUseCase:
    """동물병원 데이터 수집 및 가공 유즈케이스"""
    
    def __init__(
        self,
        vet_hospital_repository: VetHospitalRepository,
        dong_repository: AdministrativeDongRepository,
        kakao_api: Optional[KakaoMapAPI] = None
    ):
        """
        동물병원 데이터 수집 유즈케이스 초기화
        
        Args:
            vet_hospital_repository: 동물병원 레포지토리
            dong_repository: 행정동 레포지토리
            kakao_api: 카카오맵 API 클라이언트 (없으면 자동 생성)
        """
        self.vet_hospital_repository = vet_hospital_repository
        self.dong_repository = dong_repository
        self.kakao_api = kakao_api or KakaoMapAPI()
    
    def execute(self, city: str = "부산") -> List[VetHospital]:
        """
        동물병원 데이터 수집 및 가공 실행 (동별+키워드별+페이지별 반복)
        Args:
            city: 도시 이름 (예: "부산")
        Returns:
            처리된 동물병원 목록
        """
        # 여러 키워드로 검색해서 더 많은 병원 데이터 수집
        search_keywords = [
            f"{city} 동물병원",
            f"{city} 동물의료센터", 
            f"{city} 반려동물병원",
            f"{city} 24시동물병원",
            f"{city} 동물클리닉"
        ]
        
        all_hospitals = []
        all_ids = set()
        
        # 각 키워드별로 검색 및 결과 병합
        for keyword in search_keywords:
            # 현재 키워드로 검색
            current_hospitals = self.kakao_api.search_direct_keyword(keyword)
            
            # 중복 제거하며 추가
            for hospital in current_hospitals:
                if hospital.id not in all_ids:
                    all_ids.add(hospital.id)
                    all_hospitals.append(hospital)
                    
        print(f"\n=== 총 검색된 동물병원: {len(search_keywords)}개 키워드, {len(all_ids)}개 중복제거 결과 ====")
        hospitals = all_hospitals
        # 4. 수집된 병원 정보 로깅
        print(f"\n=== 수집된 전체 동물병원 개수: {len(hospitals)} ====")
        print(f"\n=== 주소 예시(10개) ====")
        for i, h in enumerate(hospitals[:10]):
            print(f"{i+1}. {h.name}: {h.address}")
        
        # 5. 행정동 정보와 공간 조인
        hospitals_dict = [self._hospital_to_dict(h) for h in hospitals]
        joined = self.dong_repository.spatial_join_hospitals(hospitals_dict)
        print(f"\n=== 공간조인 결과 회수: {len(joined)} ====")
        
        # 6. 행정동 정보 추가 및 부산시(ADM_CD 26 또는 주소에 '부산' 포함) 필터링
        busan_hospitals = []
        
        for hospital in hospitals:
            # 1) 주소에 부산이 포함된 경우
            is_busan_address = '부산' in hospital.address if hospital.address else False
            
            # 2) 공간조인으로 부산 ADM_CD가 있는 경우
            hospital_joined = joined[joined["id"] == hospital.id]
            is_busan_dong = False
            
            # 공간조인 결과가 있는 경우
            if not hospital_joined.empty:
                dong_code = hospital_joined.iloc[0].get("ADM_CD")
                dong_name = hospital_joined.iloc[0].get("ADM_NM")
                hospital.dong_code = dong_code
                hospital.dong_name = dong_name
                
                # 부산시인지 확인 (ADM_CD가 26으로 시작하면 부산)
                if dong_code and str(dong_code).startswith("26"):
                    is_busan_dong = True
            
            # 주소에 부산이 포함되거나 공간조인으로 부산 동으로 확인되면 포함
            if is_busan_address or is_busan_dong:
                busan_hospitals.append(hospital)
        
        print(f"\n=== 부산시 동물병원 필터링 결과: {len(busan_hospitals)} ====")
        print(f"\n=== 부산 병원 예시(10개) ====")
        for i, h in enumerate(busan_hospitals[:10]):
            print(f"{i+1}. {h.name}: {h.address} (동코드: {h.dong_code}, 동명: {h.dong_name})")
        
        # 7. 레포지토리에 저장 (부산만)
        self.vet_hospital_repository.save_hospitals(busan_hospitals)
        return busan_hospitals
    
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
