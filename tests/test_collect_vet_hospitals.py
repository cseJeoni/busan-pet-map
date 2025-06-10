"""
동물병원 수집 및 가공 유즈케이스 테스트
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon

from src.domain.entity import VetHospital, AdministrativeDong
from src.domain.repository import VetHospitalRepository, AdministrativeDongRepository
from src.infrastructure.kakao_api import KakaoMapAPI
from src.usecase.collect_vet_hospitals import CollectVetHospitalsUseCase


class TestCollectVetHospitalsUseCase:
    """동물병원 수집 및 가공 유즈케이스 테스트 클래스"""
    
    def setup_method(self):
        """테스트 셋업"""
        # 모의 객체 생성
        self.mock_vet_repo = Mock(spec=VetHospitalRepository)
        self.mock_dong_repo = Mock(spec=AdministrativeDongRepository)
        self.mock_kakao_api = Mock(spec=KakaoMapAPI)
        
        # 테스트 데이터 설정
        self.test_hospitals = [
            VetHospital(
                id="12345678",
                name="행복한동물병원",
                address="부산광역시 중구 중앙동 123-45",
                latitude=35.105,
                longitude=129.025,
                phone="051-123-4567",
                place_url="http://place.map.kakao.com/12345678"
            ),
            VetHospital(
                id="87654321",
                name="사랑동물병원",
                address="부산광역시 중구 동광동 123-45",
                latitude=35.105,
                longitude=129.035,
                phone="051-765-4321",
                place_url="http://place.map.kakao.com/87654321"
            )
        ]
        
        # 모의 공간 조인 결과 설정
        self.mock_joined_gdf = pd.DataFrame({
            'id': ['12345678', '87654321'],
            'ADM_CD': ['2611010100', '2611010200'],
            'ADM_NM': ['중앙동', '동광동']
        })
    
    def test_execute(self):
        """유즈케이스 실행 테스트"""
        # 모의 객체 동작 설정
        self.mock_kakao_api.collect_vet_hospitals.return_value = self.test_hospitals
        self.mock_dong_repo.spatial_join_hospitals.return_value = self.mock_joined_gdf
        
        # 유즈케이스 생성 및 실행
        usecase = CollectVetHospitalsUseCase(
            vet_hospital_repository=self.mock_vet_repo,
            dong_repository=self.mock_dong_repo,
            kakao_api=self.mock_kakao_api
        )
        result = usecase.execute(city="부산")
        
        # 결과 검증
        assert result == self.test_hospitals
        
        # 행정동 정보 설정 검증
        assert self.test_hospitals[0].dong_code == "2611010100"
        assert self.test_hospitals[0].dong_name == "중앙동"
        assert self.test_hospitals[1].dong_code == "2611010200"
        assert self.test_hospitals[1].dong_name == "동광동"
        
        # 메서드 호출 검증
        self.mock_kakao_api.collect_vet_hospitals.assert_called_once_with(city="부산")
        self.mock_dong_repo.spatial_join_hospitals.assert_called_once()
        self.mock_vet_repo.save_hospitals.assert_called_once_with(self.test_hospitals)
    
    def test_execute_with_empty_result(self):
        """빈 결과 처리 테스트"""
        # 모의 객체 동작 설정 - 빈 결과
        self.mock_kakao_api.collect_vet_hospitals.return_value = []
        
        # 유즈케이스 생성 및 실행
        usecase = CollectVetHospitalsUseCase(
            vet_hospital_repository=self.mock_vet_repo,
            dong_repository=self.mock_dong_repo,
            kakao_api=self.mock_kakao_api
        )
        result = usecase.execute(city="부산")
        
        # 결과 검증
        assert result == []
        
        # 메서드 호출 검증
        self.mock_kakao_api.collect_vet_hospitals.assert_called_once_with(city="부산")
        self.mock_dong_repo.spatial_join_hospitals.assert_called_once()
        self.mock_vet_repo.save_hospitals.assert_called_once_with([])
    
    def test_execute_with_no_dong_match(self):
        """행정동 매칭 실패 처리 테스트"""
        # 모의 객체 동작 설정 - 빈 조인 결과
        self.mock_kakao_api.collect_vet_hospitals.return_value = self.test_hospitals
        self.mock_dong_repo.spatial_join_hospitals.return_value = pd.DataFrame({
            'id': ['12345678', '87654321'],
            # ADM_CD와 ADM_NM이 없는 경우
        })
        
        # 유즈케이스 생성 및 실행
        usecase = CollectVetHospitalsUseCase(
            vet_hospital_repository=self.mock_vet_repo,
            dong_repository=self.mock_dong_repo,
            kakao_api=self.mock_kakao_api
        )
        result = usecase.execute(city="부산")
        
        # 결과 검증
        assert result == self.test_hospitals
        
        # 행정동 정보가 설정되지 않았는지 검증
        assert self.test_hospitals[0].dong_code is None
        assert self.test_hospitals[0].dong_name is None
        assert self.test_hospitals[1].dong_code is None
        assert self.test_hospitals[1].dong_name is None
        
        # 메서드 호출 검증
        self.mock_kakao_api.collect_vet_hospitals.assert_called_once_with(city="부산")
        self.mock_dong_repo.spatial_join_hospitals.assert_called_once()
        self.mock_vet_repo.save_hospitals.assert_called_once_with(self.test_hospitals)
