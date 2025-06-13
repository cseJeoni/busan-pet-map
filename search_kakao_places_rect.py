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
import re

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

# 공원 관련 카테고리 키워드
PARK_KEYWORDS = [
    '도보여행',
    '둘레길',
    '하천',
    '공원',
    '산책로',
    '산책길',
    '산',
    '등산',
    '동산',
    '수목원',
    '생태공원',
    '체육공원',
    '문화공원',
    '도시공원',
    '국립공원',
    '자연공원'
]

# 제외할 키워드 (화장실, 주차장, 관리소 등)
PARK_EXCLUSION_KEYWORDS = [
    '화장실',
    '주차장',
    '주차타워',
    '주차시설',
    '공중화장실',
    '편의점',
    '관리소',
    '관리사무소',
    '매점',
    '기념품',
    '판매점',
    '체험관',
    '카페',
    '관광안내',
    '안내소',
    '전기차충전소'  # 전기차충전소 추가
]

def filter_park_only(places, strict_category=False):
    excluded_places = []  # 제외된 장소를 저장할 리스트
    """
    공원 관련 장소만 필터링하고 화장실, 주차장 등은 제외
    
    Args:
        places: 카카오 장소 API 결과 목록
        strict_category: True이면 '여행 > 관광,명소' 카테고리만 허용 (기본값: False)
        
    Returns:
        걸을 수 있는 공원 관련 장소만 필터링된 목록
    """
    filtered = []
    tourist_category = '여행 > 관광,명소'
    
    for place in places:
        # 카테고리 및 장소명 확인
        category_name = place.get('category_name', '')
        place_name = place.get('place_name', '')
        road_address = place.get('road_address_name', '')
        address = place.get('address_name', '')
        
        # 강력한 카테고리 필터링 모드일 때
        if strict_category:
            # 카테고리가 '여행 > 관광,명소' 또는 '여행 > 공원'으로 시작하는지 확인
            if category_name.startswith(tourist_category) or category_name.startswith('여행 > 공원'):
                is_excluded_by_name = False
                for ex_keyword in PARK_EXCLUSION_KEYWORDS:
                    if ex_keyword in place_name:
                        is_excluded_by_name = True
                        break
                if not is_excluded_by_name:
                    filtered.append(place)
                else:
                    place['reason_for_exclusion'] = f"place_name_contains_exclusion_keyword: {ex_keyword}"
                    excluded_places.append(place) # 이름으로 제외된 경우
            else:
                place['reason_for_exclusion'] = f"category_not_valid: {category_name}"
                excluded_places.append(place) # 카테고리가 맞지 않아 제외된 경우
            continue
        
        # 여기서부터는 일반 필터링 모드 (strict_category=False 일 때)
        # 제외 키워드 확인
        exclude = False
        for keyword in PARK_EXCLUSION_KEYWORDS:
            if (keyword in place_name or 
                keyword in category_name or 
                keyword in road_address or 
                keyword in address):
                exclude = True
                break
        
        if exclude:
            continue
            
        # 공원 관련 키워드 확인
        include = False
        for keyword in PARK_KEYWORDS:
            if (keyword in place_name or 
                keyword in category_name or 
                keyword in road_address or 
                keyword in address):
                include = True
                break
                
        # '여행 > 관광,명소' 카테고리도 포함
        if tourist_category in category_name:
            include = True
        
        if include:
            filtered.append(place)
    
    if strict_category:
        return filtered, excluded_places
    return filtered

def search_busan_places(keyword, api_key, output_file, apply_filter=False, strict_category=False):
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
    
    # 필터링 적용 옵션이 활성화된 경우
    if apply_filter and keyword == '공원':
        if strict_category:
            print(f"강력 필터링 전: {len(unique_places)}개")
            filtered_places, excluded_places = filter_park_only(unique_places, strict_category=True)
            print(f"강력 필터링 결과: {len(filtered_places)}개의 '{tourist_category}' 카테고리 장소만 선택됨 (제외: {len(unique_places) - len(filtered_places)}개)")
            excluded_output_file = output_file.replace('_filtered.json', '_excluded.json')
            with open(excluded_output_file, 'w', encoding='utf-8') as f:
                json.dump(excluded_places, f, ensure_ascii=False, indent=4)
            print(f"제외된 공원 목록이 {excluded_output_file}에 저장되었습니다.")
        else:
            print(f"일반 필터링 전: {len(unique_places)}개")
            # 일반 필터링 시에는 excluded_places를 받지 않음
            filtered_places = filter_park_only(unique_places, strict_category=False)
            print(f"일반 필터링 결과: {len(filtered_places)}개의 걸을 수 있는 공원 장소가 선택됨 (제외: {len(unique_places) - len(filtered_places)}개)")
        unique_places = filtered_places
    
    # 디렉토리 생성
    os.makedirs('data', exist_ok=True)
    
    # 결과 저장
    filename = output_file
    if apply_filter and '공원' in keyword:
        # 파일명에 필터링 타입 추가
        name, ext = os.path.splitext(output_file)
        if strict_category:
            filename = f"{name}_strict_filtered{ext}"
        else:
            filename = f"{name}_normal_filtered{ext}"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(unique_places, f, ensure_ascii=False, indent=2)
    
    print(f"결과가 {filename}에 저장되었습니다.")
    
    return unique_places

def main():
    # 명령줄 인자로 API 키 받기
    # 사용자 요청에 따라 API 키를 하드코딩합니다.
    # 보안 참고: 이 방식은 코드를 공유하거나 버전 관리할 경우 API 키 노출 위험이 있습니다.
    api_key = "f5567e7771d9d76bc8d6b4c5d82918d7" 
    print("알림: Kakao API 키가 코드 내에 하드코딩되어 사용됩니다.")
    
    # 1. 동물병원 검색
    print("1. 동물병원 데이터 검색...")
    hospitals = search_busan_places("동물병원", api_key, 'data/busan_vet_hospitals_all.json')
    
    # 2. 공원 검색 - 강력 필터링 적용 (여행 > 관광,명소 및 여행 > 공원 카테고리 포함)
    print("\n2. 공원 데이터 검색 (강력 필터링 모드)...")
    # 공원 검색 실행
    parks = search_kakao_places_by_rect("공원", 128.8, 34.9, 129.3, 35.4, api_key)
    parks = remove_duplicates(parks)
    print(f"검색 결과: 총 {len(parks)}개의 '공원' 장소를 찾았습니다. (중복 제거 전: {len(parks)})")
    
    # 강력 필터링 적용 - 여행 > 관광,명소 및 여행 > 공원 카테고리
    strict_filtered, excluded_places = filter_park_only(parks, strict_category=True)
    print(f"강력 필터링 결과: {len(strict_filtered)}개의 '여행 > 관광,명소' 또는 '여행 > 공원' 카테고리 장소 선택됨 (제외: {len(parks)-len(strict_filtered)}개)")
    
    # 결과 저장
    with open('data/busan_parks_strict_filtered.json', 'w', encoding='utf-8') as f:
        json.dump(strict_filtered, f, ensure_ascii=False, indent=2)
    print(f"결과가 data/busan_parks_strict_filtered.json에 저장되었습니다.")
    
    # 제외된 장소 저장
    with open('data/busan_parks_excluded.json', 'w', encoding='utf-8') as f:
        json.dump(excluded_places, f, ensure_ascii=False, indent=2)
    print(f"제외된 장소가 data/busan_parks_excluded.json에 저장되었습니다.")
    
    # 3. 공원 검색 - 일반 필터링 적용 (키워드 기반)
    print("\n3. 공원 데이터 검색 (일반 필터링 모드)...")
    # 일반 필터링 적용 - 키워드 기반
    normal_filtered = filter_park_only(parks, strict_category=False)
    print(f"일반 필터링 결과: {len(normal_filtered)}개의 걸을 수 있는 공원 장소가 선택됨 (제외: {len(parks)-len(normal_filtered)}개)")
    
    # 결과 저장
    with open('data/busan_parks_normal_filtered.json', 'w', encoding='utf-8') as f:
        json.dump(normal_filtered, f, ensure_ascii=False, indent=2)
    print(f"결과가 data/busan_parks_normal_filtered.json에 저장되었습니다.")
    
    # 4. 애견카페 검색 및 저장 - 필터링 미적용
    print("\n4. 애견카페 데이터 검색...")
    dog_cafes = search_busan_places("애견카페", api_key, 'data/busan_dog_cafes_all.json')
    
    print("모든 검색이 완료되었습니다.")

if __name__ == "__main__":
    main()
