"""
카카오맵 API를 통한 동물병원 데이터 수집
"""
import os
import time
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from src.domain.entity import VetHospital


class KakaoMapAPI:
    """카카오맵 API 클라이언트"""
    
    BASE_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        카카오맵 API 클라이언트 초기화
        
        Args:
            api_key: 카카오 API 키 (없으면 환경변수에서 로드)
        """
        load_dotenv()  # .env 파일에서 환경변수 로드
        self.api_key = api_key or os.getenv("KAKAO_API_KEY")
        if not self.api_key:
            raise ValueError("카카오 API 키가 설정되지 않았습니다. KAKAO_API_KEY 환경변수를 설정하세요.")
        
        self.headers = {
            "Authorization": f"KakaoAK {self.api_key}"
        }
    
    def search_keyword(self, 
                      keyword: str, 
                      x: Optional[str] = None, 
                      y: Optional[str] = None,
                      radius: int = 20000,
                      page: int = 1,
                      size: int = 15) -> Dict[str, Any]:
        """
        키워드로 장소 검색
        
        Args:
            keyword: 검색 키워드
            x: 중심 경도 (longitude)
            y: 중심 위도 (latitude)
            radius: 검색 반경 (미터)
            page: 페이지 번호
            size: 한 페이지 결과 수
            
        Returns:
            검색 결과 딕셔너리
        """
        params = {
            "query": keyword,
            "page": page,
            "size": size
        }
        
        # 좌표 기반 검색 설정
        if x and y:
            params.update({
                "x": x,
                "y": y,
                "radius": radius
            })
        
        response = requests.get(
            self.BASE_URL,
            headers=self.headers,
            params=params
        )
        
        response.raise_for_status()  # HTTP 에러 발생 시 예외 발생
        return response.json()
    
    def collect_vet_hospitals(self, 
                         city: str = "부산", 
                         dong_names: Optional[list] = None,
                         keywords: Optional[list] = None) -> List[VetHospital]:
        """
        도시 내 모든 동물병원 수집 (동별+키워드별 반복, 모든 페이지, 중복 제거)
        Args:
            city: 도시 이름 (예: "부산")
            dong_names: 행정동 이름 리스트
            keywords: 검색 키워드 리스트
        Returns:
            수집된 동물병원 목록
        """
        if dong_names is None:
            dong_names = []
        if keywords is None:
            keywords = ["동물병원", "동물의료센터", "반려동물병원", "24시동물병원", "동물클리닉"]
        all_hospitals = []
        seen_ids = set()
        for dong in dong_names:
            for keyword in keywords:
                page = 1
                while True:
                    query = f"{dong} {keyword}"
                    try:
                        result = self.search_keyword(query, page=page)
                        documents = result.get("documents", [])
                        if not documents:
                            break
                        for item in documents:
                            if item["id"] not in seen_ids:
                                seen_ids.add(item["id"])
                                hospital = VetHospital.from_kakao_api_result(item)
                                all_hospitals.append(hospital)
                        meta = result.get("meta", {})
                        if meta.get("is_end", True):
                            break
                        page += 1
                        time.sleep(0.2)
                    except Exception as e:
                        print(f"검색 중 오류 발생: {e} (query={query}, page={page})")
                        break
        return all_hospitals
        
    def search_direct_keyword(self, keyword: str) -> List[VetHospital]:
        """
        직접 키워드로 동물병원 검색 (모든 페이지 결과 수집)
        
        Args:
            keyword: 검색 키워드 (예: "부산 동물병원")
            
        Returns:
            수집된 동물병원 목록
        """
        all_hospitals = []
        seen_ids = set()
        page = 1
        
        print(f"키워드 '{keyword}'로 직접 검색 시작...")
        
        while True:
            try:
                # 키워드로 검색 (페이지 단위)
                result = self.search_keyword(keyword, page=page, size=15)
                documents = result.get("documents", [])
                
                # 검색 결과 없으면 종료
                if not documents:
                    break
                
                # 병원 객체 생성하며 중복 제거
                for item in documents:
                    if item["id"] not in seen_ids:
                        seen_ids.add(item["id"])
                        hospital = VetHospital.from_kakao_api_result(item)
                        all_hospitals.append(hospital)
                
                print(f"페이지 {page} 검색 완료: {len(documents)}개 결과 (누적: {len(all_hospitals)}개)")
                
                # 마지막 페이지면 종료
                meta = result.get("meta", {})
                if meta.get("is_end", True):
                    break
                    
                # 다음 페이지로
                page += 1
                time.sleep(0.2)  # API 호출 제한 방지
                
            except Exception as e:
                print(f"검색 중 오류 발생: {e} (keyword={keyword}, page={page})")
                break
                
        print(f"총 {len(all_hospitals)}개 동물병원 검색 완료")
        return all_hospitals
