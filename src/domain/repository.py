"""
레포지토리 인터페이스 정의
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import geopandas as gpd

from src.domain.entity import VetHospital, AdministrativeDong


class VetHospitalRepository(ABC):
    """동물병원 데이터 레포지토리 인터페이스"""
    
    @abstractmethod
    def save_hospitals(self, hospitals: List[VetHospital]) -> None:
        """동물병원 목록 저장"""
        pass
    
    @abstractmethod
    def get_hospitals(self) -> List[VetHospital]:
        """저장된 동물병원 목록 조회"""
        pass
    
    @abstractmethod
    def get_hospitals_by_dong(self, dong_code: str) -> List[VetHospital]:
        """특정 행정동의 동물병원 목록 조회"""
        pass
    
    @abstractmethod
    def get_hospitals_count_by_dong(self) -> Dict[str, int]:
        """행정동별 동물병원 개수 조회"""
        pass


class AdministrativeDongRepository(ABC):
    """행정동 데이터 레포지토리 인터페이스"""
    
    @abstractmethod
    def load_dongs(self, shapefile_path: str) -> List[AdministrativeDong]:
        """행정동 경계 shapefile 로드"""
        pass
    
    @abstractmethod
    def get_dong_by_code(self, dong_code: str) -> Optional[AdministrativeDong]:
        """코드로 행정동 조회"""
        pass
    
    @abstractmethod
    def get_dong_by_point(self, latitude: float, longitude: float) -> Optional[AdministrativeDong]:
        """위경도 좌표가 속한 행정동 조회"""
        pass
    
    @abstractmethod
    def get_all_dongs(self) -> List[AdministrativeDong]:
        """모든 행정동 목록 조회"""
        pass
    
    @abstractmethod
    def get_dongs_geodataframe(self) -> gpd.GeoDataFrame:
        """행정동 GeoDataFrame 반환"""
        pass
