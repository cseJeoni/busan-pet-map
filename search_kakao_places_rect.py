"""
카카오맵 API의 45개 결과 제한을 우회하기 위한 개선된 검색 방법
- rect 파라미터를 활용한 영역 분할 검색
- 재귀적으로 영역을 4등분하여 모든 결과 수집
"""
import os
import json
import requests
import time
import sys

def search_kakao_places_by_rect(keyword, start_x, start_y, end_x, end_y, api_key):
    """
    카카오맵 API 사각형 영역 검색 - 45개 제한 우회 버전
    
    Args:
        keyword: 검색어 (예: "부산 공원")
        start_x: 시작 경도(좌하단)
        start_y: 시작 위도(좌하단)
        end_x: 끝 경도(우상단)
        end_y: 끝 위도(우상단)
        api_key: 카카오 REST API 키
    
    Returns:
        검색 결과 목록
    """
    # API 요청 URL 및 헤더 설정
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    
    # 검색 결과를 담을 리스트와 페이지 번호 초기화
    all_data_list = []
    page_num = 1
    
    while True:
        # API 요청 파라미터 설정
        params = {
            'query': keyword,
            'page': page_num,
            'rect': f'{start_x},{start_y},{end_x},{end_y}'
        }
        
        try:
            # API 요청 실행
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            result = response.json()
            documents = result.get('documents', [])
            meta = result.get('meta', {})
            
            # 검색된 총 개수
            total_count = meta.get('total_count', 0)
            print(f"'{keyword}' 검색 결과 - 영역: [{start_x:.6f}, {start_y:.6f}, {end_x:.6f}, {end_y:.6f}], 총 개수: {total_count}")
            
            # 검색 결과가 45개 초과인 경우 영역 분할
            if total_count > 45:
                print("→ 검색 결과가 45개를 초과하여 영역을 4등분합니다.")
                # 영역 중간점 계산
                mid_x = (start_x + end_x) / 2
                mid_y = (start_y + end_y) / 2
                
                # 4등분 영역 각각 재귀적으로 검색
                # 좌하단
                all_data_list.extend(search_kakao_places_by_rect(keyword, start_x, start_y, mid_x, mid_y, api_key))
                # 우하단
                all_data_list.extend(search_kakao_places_by_rect(keyword, mid_x, start_y, end_x, mid_y, api_key))
                # 좌상단
                all_data_list.extend(search_kakao_places_by_rect(keyword, start_x, mid_y, mid_x, end_y, api_key))
                # 우상단
                all_data_list.extend(search_kakao_places_by_rect(keyword, mid_x, mid_y, end_x, end_y, api_key))
                
                return all_data_list
            else:
                # 이번 페이지 결과 추가
                all_data_list.extend(documents)
                
                # 마지막 페이지인 경우 종료
                if meta.get('is_end', True):
                    return all_data_list
                
                # 다음 페이지가 있는 경우 계속 요청
                page_num += 1
                print(f"→ 다음 페이지 ({page_num}) 조회 중")
                
                # API 호출 제한 방지를 위한 짧은 대기
                time.sleep(0.2)
                
        except Exception as e:
            print(f"API 요청 오류: {e}")
            return all_data_list

def remove_duplicates(places):
    """중복 결과 제거 (ID 기준)"""
    unique_places = {}
    for place in places:
        place_id = place.get('id')
        if place_id and place_id not in unique_places:
            unique_places[place_id] = place
    
    return list(unique_places.values())

def search_busan_places(keyword, api_key, output_file):
    """
    부산 지역 내 키워드로 검색하고 결과를 파일로 저장
    
    부산 대략적 좌표 범위:
    - 남서쪽(좌하단): 약 128.8, 34.9 
    - 북동쪽(우상단): 약 129.3, 35.4
    """
    print(f"카카오맵 API로 부산 지역 내 '{keyword}' 검색 중...")
    
    # 부산 전체 영역 좌표 (경도, 위도)
    # 좌하단(남서)과 우상단(북동) 좌표
    start_x, start_y = 128.8, 34.9  # 경도, 위도 (남서)
    end_x, end_y = 129.3, 35.4      # 경도, 위도 (북동)
    
    # 검색 실행
    places = search_kakao_places_by_rect(keyword, start_x, start_y, end_x, end_y, api_key)
    
    # 중복 제거
    unique_places = remove_duplicates(places)
    
    print(f"검색 결과: 총 {len(unique_places)}개의 '{keyword}' 장소를 찾았습니다. (중복 제거 전: {len(places)})")
    
    # 디렉토리 생성
    os.makedirs('data', exist_ok=True)
    
    # 결과 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_places, f, ensure_ascii=False, indent=2)
    
    print(f"결과가 {output_file}에 저장되었습니다.")
    
    return unique_places

def main():
    # 명령줄 인자로 API 키 받기
    if len(sys.argv) < 2:
        print("사용법: python3 search_kakao_places_rect.py <KAKAO_API_KEY>")
        return
        
    api_key = sys.argv[1]
    
    # 공원 검색 및 저장
    parks = search_busan_places("공원", api_key, 'data/busan_parks_all.json')
    
    # 애견카페 검색 및 저장
    dog_cafes = search_busan_places("애견카페", api_key, 'data/busan_dog_cafes_all.json')
    
    print("모든 검색이 완료되었습니다.")

if __name__ == "__main__":
    main()
