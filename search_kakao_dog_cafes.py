"""
카카오맵 API를 사용하여 "부산 애견카페" 키워드로 검색하고 결과를 JSON으로 저장
- 출력: data/busan_dog_cafes.json
"""
import os
import json
import requests
from dotenv import load_dotenv

def search_kakao_places(query, api_key=None):
    """
    카카오맵 API로 장소 검색
    
    Args:
        query: 검색어 (예: "부산 애견카페")
        api_key: 카카오 REST API 키 (없으면 환경변수에서 가져옴)
    
    Returns:
        검색 결과 목록
    """
    # API 키 가져오기 (환경 변수 또는 직접 입력)
    if not api_key:
        load_dotenv()  # .env 파일에서 환경 변수 로드
        api_key = os.environ.get('KAKAO_API_KEY')
        
        if not api_key:
            print("KAKAO_API_KEY를 .env 파일에 설정하거나 함수 인자로 전달해주세요.")
            return []
    
    # API 요청 URL 및 헤더 설정
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    
    # 검색 결과를 담을 리스트
    all_places = []
    
    # 페이지 반복 요청 (최대 3페이지, 총 45개 결과)
    for page in range(1, 4):
        params = {
            "query": query,
            "page": page,
            "size": 15,  # 페이지당 결과 수 (최대 15)
            "sort": "accuracy"  # 정확도 순 정렬
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # HTTP 오류 체크
            
            data = response.json()
            places = data.get('documents', [])
            
            # 결과가 없으면 더 이상 페이지 요청하지 않음
            if not places:
                break
                
            all_places.extend(places)
            
            # 마지막 페이지인 경우
            meta = data.get('meta', {})
            if page >= meta.get('pageable_count', 0) / 15:
                break
                
        except Exception as e:
            print(f"API 요청 오류: {e}")
            break
    
    return all_places

def main():
    # 검색 실행
    print("카카오맵 API로 '부산 애견카페' 검색 중...")
    places = search_kakao_places("부산 애견카페")
    
    if not places:
        print("검색 결과가 없거나 API 키가 설정되지 않았습니다.")
        return
    
    print(f"검색 결과: {len(places)}개의 장소를 찾았습니다.")
    
    # 디렉토리 생성
    os.makedirs('data', exist_ok=True)
    
    # 결과를 JSON 파일로 저장
    output_file = 'data/busan_dog_cafes.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(places, f, ensure_ascii=False, indent=2)
    
    print(f"결과 파일 저장 완료: {output_file}")
    
    # 검색 결과 미리보기
    for i, place in enumerate(places[:5], 1):
        print(f"{i}. {place.get('place_name')} - {place.get('address_name')} ({place.get('x')}, {place.get('y')})")
    
    if len(places) > 5:
        print(f"...외 {len(places) - 5}개")

if __name__ == "__main__":
    main()
