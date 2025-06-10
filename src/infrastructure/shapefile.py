"""
행정동 shapefile 처리 및 GeoDataFrame 관리
"""
import geopandas as gpd
from typing import List, Optional, Dict, Any
from shapely.geometry import Point

from src.domain.entity import AdministrativeDong
from src.domain.repository import AdministrativeDongRepository


class ShapefileRepository(AdministrativeDongRepository):
    """행정동 shapefile 레포지토리 구현"""
    
    def __init__(self):
        self.dongs: List[AdministrativeDong] = []
        self.gdf: Optional[gpd.GeoDataFrame] = None
    
    def load_dongs(self, shapefile_path: str) -> List[AdministrativeDong]:
        """
        행정동 경계 shapefile 로드
        
        Args:
            shapefile_path: shapefile 경로
            
        Returns:
            행정동 객체 목록
        """
        self.gdf = gpd.read_file(shapefile_path)
        
        # 부산시 데이터만 필터링 (행정동 코드가 '26'으로 시작하는 경우)
        busan_gdf = self.gdf[self.gdf['ADM_CD'].astype(str).str.startswith('26')]
        self.gdf = busan_gdf
        
        # 행정동 객체 생성
        self.dongs = [AdministrativeDong.from_geopandas_row(row) for _, row in busan_gdf.iterrows()]
        
        return self.dongs
    
    def get_dong_by_code(self, dong_code: str) -> Optional[AdministrativeDong]:
        """
        코드로 행정동 조회
        
        Args:
            dong_code: 행정동 코드
            
        Returns:
            행정동 객체 또는 None
        """
        for dong in self.dongs:
            if dong.code == dong_code:
                return dong
        return None
    
    def get_dong_by_point(self, latitude: float, longitude: float) -> Optional[AdministrativeDong]:
        """
        위경도 좌표가 속한 행정동 조회
        
        Args:
            latitude: 위도
            longitude: 경도
            
        Returns:
            행정동 객체 또는 None
        """
        if self.gdf is None:
            raise ValueError("행정동 데이터가 로드되지 않았습니다. load_dongs()를 먼저 호출하세요.")
        
        point = Point(longitude, latitude)  # shapely Point 객체 생성 (경도, 위도 순서)
        
        # 포인트가 포함된 행정동 찾기
        for idx, row in self.gdf.iterrows():
            if row.geometry.contains(point):
                return AdministrativeDong.from_geopandas_row(row)
        
        return None
    
    def get_all_dongs(self) -> List[AdministrativeDong]:
        """
        모든 행정동 목록 조회
        
        Returns:
            행정동 객체 목록
        """
        return self.dongs
    
    def get_dongs_geodataframe(self) -> gpd.GeoDataFrame:
        """
        행정동 GeoDataFrame 반환
        
        Returns:
            행정동 GeoDataFrame
        """
        if self.gdf is None:
            raise ValueError("행정동 데이터가 로드되지 않았습니다. load_dongs()를 먼저 호출하세요.")
        
        return self.gdf
    
    def spatial_join_hospitals(self, hospitals: List[Dict[str, Any]]) -> gpd.GeoDataFrame:
        """
        동물병원 데이터와 행정동 데이터를 공간 조인
        
        Args:
            hospitals: 동물병원 데이터 목록 (위도, 경도 포함)
            
        Returns:
            동물병원이 속한 행정동 정보가 포함된 GeoDataFrame
        """
        if self.gdf is None:
            raise ValueError("행정동 데이터가 로드되지 않았습니다. load_dongs()를 먼저 호출하세요.")
        
        # 동물병원 데이터로 GeoDataFrame 생성
        hospitals_df = gpd.GeoDataFrame(
            hospitals,
            geometry=[Point(h["longitude"], h["latitude"]) for h in hospitals],
            crs=self.gdf.crs
        )
        
        # 공간 조인 수행
        joined = gpd.sjoin(
            hospitals_df,
            self.gdf,
            how="left",
            predicate="within"
        )
        
        return joined
    
    def count_hospitals_by_dong(self, hospitals: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        행정동별 동물병원 개수 집계
        
        Args:
            hospitals: 동물병원 데이터 목록 (위도, 경도 포함)
            
        Returns:
            행정동 코드별 동물병원 개수 딕셔너리
        """
        joined = self.spatial_join_hospitals(hospitals)
        counts = joined.groupby("ADM_CD").size().to_dict()
        
        return counts
