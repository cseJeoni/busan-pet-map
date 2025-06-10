"""
카카오맵 API 테스트
"""
import pytest
import json
import os
from unittest.mock import patch, MagicMock

from src.infrastructure.kakao_api import KakaoMapAPI
from src.domain.entity import VetHospital


@pytest.fixture
def mock_kakao_response():
    """카카오맵 API 응답 목업 데이터"""
    return {
        "meta": {
            "total_count": 45,
            "pageable_count": 45,
            "is_end": False
        },
        "documents": [
            {
                "id": "12345678",
                "place_name": "행복한동물병원",
                "category_name": "동물병원",
                "category_group_code": "HP8",
                "category_group_name": "병원",
                "phone": "051-123-4567",
                "address_name": "부산광역시 해운대구 우동 123-45",
                "road_address_name": "부산광역시 해운대구 해운대로 123",
                "x": "129.1234567",
                "y": "35.1234567",
                "place_url": "http://place.map.kakao.com/12345678",
                "distance": ""
            },
            {
                "id": "87654321",
                "place_name": "사랑동물병원",
                "category_name": "동물병원",
                "category_group_code": "HP8",
                "category_group_name": "병원",
                "phone": "051-765-4321",
                "address_name": "부산광역시 남구 대연동 123-45",
                "road_address_name": "부산광역시 남구 수영로 123",
                "x": "129.0987654",
                "y": "35.0987654",
                "place_url": "http://place.map.kakao.com/87654321",
                "distance": ""
            }
        ]
    }


class TestKakaoMapAPI:
    """카카오맵 API 테스트 클래스"""
    
    @patch.dict(os.environ, {"KAKAO_API_KEY": "test_api_key"})
    def test_init_with_env_var(self):
        """환경변수에서 API 키를 로드하는지 테스트"""
        api = KakaoMapAPI()
        assert api.api_key == "test_api_key"
    
    def test_init_with_param(self):
        """생성자 파라미터로 API 키를 설정하는지 테스트"""
        api = KakaoMapAPI(api_key="param_api_key")
        assert api.api_key == "param_api_key"
    
    @patch('src.infrastructure.kakao_api.requests.get')
    def test_search_keyword(self, mock_get, mock_kakao_response):
        """키워드 검색 기능 테스트"""
        # 목업 응답 설정
        mock_response = MagicMock()
        mock_response.json.return_value = mock_kakao_response
        mock_get.return_value = mock_response
        
        # API 호출
        api = KakaoMapAPI(api_key="test_api_key")
        result = api.search_keyword(
            keyword="부산 동물병원",
            x="129.1234567",
            y="35.1234567"
        )
        
        # 결과 검증
        assert result == mock_kakao_response
        assert len(result["documents"]) == 2
        assert result["documents"][0]["place_name"] == "행복한동물병원"
        
        # requests.get 호출 검증
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert args[0] == "https://dapi.kakao.com/v2/local/search/keyword.json"
        assert kwargs["headers"]["Authorization"] == "KakaoAK test_api_key"
        assert kwargs["params"]["query"] == "부산 동물병원"
        assert kwargs["params"]["x"] == "129.1234567"
        assert kwargs["params"]["y"] == "35.1234567"
    
    @patch('src.infrastructure.kakao_api.KakaoMapAPI.search_keyword')
    def test_collect_vet_hospitals(self, mock_search, mock_kakao_response):
        """동물병원 수집 기능 테스트"""
        # 목업 검색 결과 설정
        mock_search.return_value = mock_kakao_response
        
        # API 호출
        api = KakaoMapAPI(api_key="test_api_key")
        hospitals = api.collect_vet_hospitals(city="부산")
        
        # 결과 검증
        assert len(hospitals) == 2
        assert isinstance(hospitals[0], VetHospital)
        assert hospitals[0].name == "행복한동물병원"
        assert hospitals[0].latitude == 35.1234567
        assert hospitals[0].longitude == 129.1234567
        
        # search_keyword 호출 검증
        mock_search.assert_called()
        args, kwargs = mock_search.call_args_list[0]
        assert kwargs["keyword"] == "부산 동물병원"
