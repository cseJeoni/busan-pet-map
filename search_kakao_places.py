"""
카카오맵 API를 사용하여 키워드로 검색하고 결과를 JSON으로 저장하는 개선된 버전
- 최대 10페이지(150개)까지 결과를 가져오도록 개선
"""
import os
import json
import requests
import time
import sys

def search_kakao_places(query, api_key, max_pages=10):
    """
    카카오맵 API로 장소 검색 - 페이지네이션 처리 개선
    
    Args:
        query: 검색어 (예: "부산 공원")
        api_key: 카카오 REST API 키
        max_pages: 최대 페이지 수 (기본값 10, 최대 45페이지까지 가능)
    
    Returns:
        검색 결과 목록
    """
    # API 요청 URL 및 헤더 설정
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    
    # 검색 결과를 담을 리스트
    all_places = []
    
    # 페이지 반복 요청
    for page in range(1, max_pages + 1):
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
                print(f"더 이상 결과가 없습니다. (마지막 페이지: {page-1})")
                break
                
            all_places.extend(places)
            print(f"페이지 {page} 검색 완료: 현재까지 {len(all_places)}개 결과")
            
            # 마지막 페이지 체크
            meta = data.get('meta', {})
            is_end = meta.get('is_end', False)
            total_count = meta.get('total_count', 0)
            pageable_count = meta.get('pageable_count', 0)
            
            if is_end or page >= pageable_count / 15:
                print(f"페이지네이션 종료 (총 개수: {total_count}, 페이지 가능 개수: {pageable_count})")
                break
            
            # API 호출 제한 방지를 위한 짧은 대기
            time.sleep(0.3)
                
        except Exception as e:
            print(f"API 요청 오류: {e}")
            break
    
    return all_places

def search_and_save(query, api_key, output_file, region_prefix="부산"):
    """
    지역 키워드로 검색하고 결과를 파일로 저장
    
    Args:
        query: 검색 키워드 (예: "공원", "애견카페")
        api_key: 카카오 REST API 키
        output_file: 결과를 저장할 파일 경로
        region_prefix: 지역 접두어 (기본값: "부산")
    """
    full_query = f"{region_prefix} {query}"
    print(f"카카오맵 API로 '{full_query}' 검색 중...")
    
    places = search_kakao_places(full_query, api_key)
    
    if not places:
        print(f"{query} 검색 결과가 없습니다.")
        return
    
    print(f"검색 결과: {len(places)}개의 {query}를(을) 찾았습니다.")
    
    # 디렉토리 생성
    os.makedirs('data', exist_ok=True)
    
    # 결과 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(places, f, ensure_ascii=False, indent=2)
    
    print(f"결과가 {output_file}에 저장되었습니다.")
    
    return places

def main():
    # 명령줄 인자로 API 키 받기
    if len(sys.argv) < 2:
        print("사용법: python3 search_kakao_places.py <KAKAO_API_KEY>")
        return
        
    api_key = sys.argv[1]
    
    # 공원 검색 및 저장
    parks = search_and_save("공원", api_key, 'data/busan_parks.json')
    
    # 애견카페 검색 및 저장
    dog_cafes = search_and_save("애견카페", api_key, 'data/busan_dog_cafes.json')
    
    # 강아지 친화적 장소 검색 및 저장 (추가 옵션)
    # dog_friendly = search_and_save("반려견 입장", api_key, 'data/busan_dog_friendly_places.json')
    
    print("모든 검색이 완료되었습니다.")

if __name__ == "__main__":
    main()
