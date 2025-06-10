"""
동물병원 및 행정동 엔티티 정의
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class VetHospital:
    """동물병원 엔티티"""
    id: str
    name: str
    address: str
    latitude: float
    longitude: float
    phone: Optional[str] = None
    place_url: Optional[str] = None
    dong_code: Optional[str] = None  # 행정동 코드 (spatial join 후 할당)
    dong_name: Optional[str] = None  # 행정동 이름 (spatial join 후 할당)
    
    @classmethod
    def from_kakao_api_result(cls, item: Dict[str, Any]) -> 'VetHospital':
        """카카오 API 결과로부터 동물병원 객체 생성"""
        return cls(
            id=item.get('id'),
            name=item.get('place_name'),
            address=item.get('address_name'),
            latitude=float(item.get('y')),
            longitude=float(item.get('x')),
            phone=item.get('phone'),
            place_url=item.get('place_url')
        )


@dataclass
class AdministrativeDong:
    """행정동 엔티티"""
    code: str  # 행정동 코드
    name: str  # 행정동 이름
    geometry: Any  # 행정동 경계 폴리곤 (shapely.geometry.Polygon)
    vet_hospitals_count: int = 0  # 동물병원 수
    
    @classmethod
    def from_geopandas_row(cls, row) -> 'AdministrativeDong':
        """GeoPandas DataFrame 행으로부터 행정동 객체 생성"""
        return cls(
            code=row['ADM_CD'],
            name=row['ADM_NM'],
            geometry=row['geometry']
        )
