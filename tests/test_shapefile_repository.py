"""
행정동 shapefile 레포지토리 테스트
"""
import pytest
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon
from unittest.mock import patch, MagicMock

from src.infrastructure.shapefile import ShapefileRepository
from src.domain.entity import AdministrativeDong


@pytest.fixture
def mock_busan_gdf():
    """부산시 행정동 GeoDataFrame 목업"""
    # 테스트용 행정동 데이터 생성
    data = {
        'ADM_CD': ['2611010100', '2611010200', '2611010300'],
        'ADM_NM': ['중앙동', '동광동', '대청동'],
        'geometry': [
            Polygon([(129.02, 35.10), (129.03, 35.10), (129.03, 35.11), (129.02, 35.11)]),
            Polygon([(129.03, 35.10), (129.04, 35.10), (129.04, 35.11), (129.03, 35.11)]),
            Polygon([(129.04, 35.10), (129.05, 35.10), (129.05, 35.11), (129.04, 35.11)])
        ]
    }
    return gpd.GeoDataFrame(data, crs="EPSG:4326")


@pytest.fixture
def mock_hospitals():
    """테스트용 동물병원 데이터"""
    return [
        {
            "id": "12345678",
            "name": "행복한동물병원",
            "address": "부산광역시 중구 중앙동 123-45",
            "latitude": 35.105,
            "longitude": 129.025,
            "phone": "051-123-4567",
            "place_url": "http://place.map.kakao.com/12345678"
        },
        {
            "id": "87654321",
            "name": "사랑동물병원",
            "address": "부산광역시 중구 동광동 123-45",
            "latitude": 35.105,
            "longitude": 129.035,
            "phone": "051-765-4321",
            "place_url": "http://place.map.kakao.com/87654321"
        },
        {
            "id": "12348765",
            "name": "희망동물병원",
            "address": "부산광역시 중구 대청동 123-45",
            "latitude": 35.105,
            "longitude": 129.045,
            "phone": "051-123-8765",
            "place_url": "http://place.map.kakao.com/12348765"
        }
    ]


class TestShapefileRepository:
    """행정동 shapefile 레포지토리 테스트 클래스"""
    
    @patch('geopandas.read_file')
    def test_load_dongs(self, mock_read_file, mock_busan_gdf):
        """행정동 로드 테스트"""
        # 목업 설정
        mock_read_file.return_value = mock_busan_gdf
        
        # 레포지토리 초기화 및 행정동 로드
        repo = ShapefileRepository()
        dongs = repo.load_dongs("mock_shapefile_path.shp")
        
        # 결과 검증
        assert len(dongs) == 3
        assert isinstance(dongs[0], AdministrativeDong)
        assert dongs[0].code == "2611010100"
        assert dongs[0].name == "중앙동"
        
        # read_file 호출 검증
        mock_read_file.assert_called_once_with("mock_shapefile_path.shp")
    
    @patch('geopandas.read_file')
    def test_get_dong_by_code(self, mock_read_file, mock_busan_gdf):
        """코드로 행정동 조회 테스트"""
        # 목업 설정
        mock_read_file.return_value = mock_busan_gdf
        
        # 레포지토리 초기화 및 행정동 로드
        repo = ShapefileRepository()
        repo.load_dongs("mock_shapefile_path.shp")
        
        # 코드로 행정동 조회
        dong = repo.get_dong_by_code("2611010200")
        
        # 결과 검증
        assert dong is not None
        assert dong.code == "2611010200"
        assert dong.name == "동광동"
        
        # 존재하지 않는 코드 조회
        dong = repo.get_dong_by_code("9999999999")
        assert dong is None
    
    @patch('geopandas.read_file')
    def test_get_dong_by_point(self, mock_read_file, mock_busan_gdf):
        """위경도 좌표로 행정동 조회 테스트"""
        # 목업 설정
        mock_read_file.return_value = mock_busan_gdf
        
        # 레포지토리 초기화 및 행정동 로드
        repo = ShapefileRepository()
        repo.load_dongs("mock_shapefile_path.shp")
        
        # 위경도 좌표로 행정동 조회
        dong = repo.get_dong_by_point(latitude=35.105, longitude=129.025)
        
        # 결과 검증
        assert dong is not None
        assert dong.code == "2611010100"
        assert dong.name == "중앙동"
        
        # 다른 위경도 좌표 테스트
        dong = repo.get_dong_by_point(latitude=35.105, longitude=129.035)
        assert dong is not None
        assert dong.code == "2611010200"
        assert dong.name == "동광동"
        
        # 경계 밖의 좌표 테스트
        dong = repo.get_dong_by_point(latitude=35.200, longitude=129.200)
        assert dong is None
    
    @patch('geopandas.read_file')
    def test_spatial_join_hospitals(self, mock_read_file, mock_busan_gdf, mock_hospitals):
        """동물병원 데이터와 행정동 데이터 공간 조인 테스트"""
        # 목업 설정
        mock_read_file.return_value = mock_busan_gdf
        
        # 레포지토리 초기화 및 행정동 로드
        repo = ShapefileRepository()
        repo.load_dongs("mock_shapefile_path.shp")
        
        # 공간 조인 수행
        joined = repo.spatial_join_hospitals(mock_hospitals)
        
        # 결과 검증
        assert len(joined) == 3
        assert joined.iloc[0]["ADM_CD"] == "2611010100"
        assert joined.iloc[1]["ADM_CD"] == "2611010200"
        assert joined.iloc[2]["ADM_CD"] == "2611010300"
        
        # 병원 ID 확인
        assert joined.iloc[0]["id"] == "12345678"
        assert joined.iloc[1]["id"] == "87654321"
        assert joined.iloc[2]["id"] == "12348765"
    
    @patch('geopandas.read_file')
    def test_count_hospitals_by_dong(self, mock_read_file, mock_busan_gdf, mock_hospitals):
        """행정동별 동물병원 개수 집계 테스트"""
        # 목업 설정
        mock_read_file.return_value = mock_busan_gdf
        
        # 레포지토리 초기화 및 행정동 로드
        repo = ShapefileRepository()
        repo.load_dongs("mock_shapefile_path.shp")
        
        # 행정동별 동물병원 개수 집계
        counts = repo.count_hospitals_by_dong(mock_hospitals)
        
        # 결과 검증
        assert len(counts) == 3
        assert counts["2611010100"] == 1
        assert counts["2611010200"] == 1
        assert counts["2611010300"] == 1
