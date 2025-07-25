"""
부산 동물병원 위치를 folium으로 지도에 빨간 점으로 시각화 (웹 브라우저에서 확인)
- 입력: data/vet_hospitals_busan.csv
- 출력: output/vet_hospitals_busan_map.html
"""
import os
import pandas as pd
import folium
import re
import json
# 1. 데이터 로드
csv_path = "data/vet_hospitals_busan.csv"
df = pd.read_csv(csv_path)

# 2. 좌표 결측치 및 이상치 제거
x_col = '좌표정보x(epsg5174)'
y_col = '좌표정보y(epsg5174)'
df = df[df[x_col].notnull() & df[y_col].notnull()]
df = df[(df[x_col] != '') & (df[y_col] != '')]

# 3. 좌표를 float로 변환 (문자열일 수 있음)
df[x_col] = df[x_col].astype(float)
df[y_col] = df[y_col].astype(float)

# 4. UTM-K(EPSG:5174) → WGS84(경위도) 변환 함수
from pyproj import Transformer
transformer = Transformer.from_crs("epsg:5174", "epsg:4326", always_xy=True)
def to_latlng(x, y):
    lng, lat = transformer.transform(x, y)
    return lat, lng

# 부산시 경계 좌표 (WGS84)
busan_lat_min = 34.8
busan_lat_max = 35.4
busan_lng_min = 128.7
busan_lng_max = 129.3

# 행정구역으로 필터링할 부산시 구/군 목록
busan_districts = [
    '중구', '서구', '동구', '영도구', '부산진구', '동래구', '남구', '북구', 
    '해운대구', '사하구', '금정구', '강서구', '연제구', '수영구', '사상구', 
    '기장군', '기장읍', '일광읍', '장안읍', '부산'
]

# 공원 필터링을 위한 키워드 및 함수 (search_kakao_places_rect.py에서 가져옴)
PARK_KEYWORDS = [
    '도보여행', '둘레길', '하천', '공원', '산책로', '산책길', '산', '등산', '동산',
    '수목원', '생태공원', '체육공원', '문화공원', '도시공원', '국립공원', '자연공원'
]

PARK_EXCLUSION_KEYWORDS = [
    '화장실', '주차장', '주차타워', '주차시설', '공중화장실', '편의점', '관리소',
    '관리사무소', '매점', '기념품', '판매점', '체험관', '카페', '관광안내', '안내소',
    '전기차충전소'  # 전기차충전소 추가
]

def filter_park_only(places, strict_category=False):
    """
    공원 관련 장소만 필터링하고 화장실, 주차장 등은 제외
    
    Args:
        places: 카카오 장소 API 결과 목록 (딕셔너리 리스트)
        strict_category: True이면 '여행 > 관광,명소' 카테고리만 허용 (기본값: False)
        
    Returns:
        걸을 수 있는 공원 관련 장소만 필터링된 목록
    """
    filtered = []
    tourist_category = '여행 > 관광,명소'
    
    for place in places:
        category_name = place.get('category_name', '')
        place_name = place.get('place_name', '')
        road_address = place.get('road_address_name', '')
        address = place.get('address_name', '')
        
        if strict_category:
            # 카테고리가 '여행 > 관광,명소'로 시작하는지 확인
            if category_name.startswith(tourist_category):
                is_excluded_by_name = False
                # 장소 이름에 제외 키워드가 포함되어 있는지 확인
                for ex_keyword in PARK_EXCLUSION_KEYWORDS:
                    if ex_keyword in place_name:
                        is_excluded_by_name = True
                        break
                if not is_excluded_by_name:
                    filtered.append(place)
            continue  # strict_category 모드에서는 다른 조건 검사 없이 다음 장소로 넘어감
        
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
            
        include = False
        for keyword in PARK_KEYWORDS:
            if (keyword in place_name or 
                keyword in category_name or 
                keyword in road_address or 
                keyword in address):
                include = True
                break
                
        if tourist_category in category_name:
            include = True
        
        if include:
            filtered.append(place)
    
    return filtered

df['lat'], df['lng'] = zip(*df.apply(lambda row: to_latlng(row[x_col], row[y_col]), axis=1))

# 5. 부산 지역 좌표 범위로 동물병원 데이터 필터링
print(f"동물병원 데이터 좌표 변환 후: {len(df)}개")
original_vet_count = len(df)
df = df[
    (df['lat'].notna()) & (df['lng'].notna()) &
    (df['lat'] >= busan_lat_min) &
    (df['lat'] <= busan_lat_max) &
    (df['lng'] >= busan_lng_min) &
    (df['lng'] <= busan_lng_max)
]
df.dropna(subset=['lat', 'lng'], inplace=True) # NaN이 포함된 행이 있다면 제거
print(f"부산 좌표 범위 및 유효한 좌표로 필터링된 동물병원 수: {len(df)} (원래 {original_vet_count}개)")

# 다음 단계 주석 번호는 수동으로 업데이트 필요 (예: # 5. 지도 생성 -> # 6. 지도 생성)

# 5. 지도 생성 (중심: 부산시청 위경도, zoom 조정)
map_center = [35.1796, 129.0756]
# 부산 대략적 영역: 북서(34.85, 128.8), 남동(35.35, 129.3)
busan_bounds = [[34.85, 128.8], [35.35, 129.3]]
m = folium.Map(location=map_center, zoom_start=11, tiles='cartodbpositron', max_bounds=True)
m.fit_bounds(busan_bounds)

# 6. 부산시 행정동(emd) geojson overlay (로컬 파일 사용)
# 원래 파일은 EPSG:5186 좌표계였고, transform_geojson_crs.py 로 변환한 WGS84 파일 사용
import json
with open('data/busan_emd_wgs84.geojson', encoding='utf-8') as f:
    busan_emd_data = json.load(f)

# 행정동 경계를 FeatureGroup으로 묶음 (토글 가능하게)
boundary_group = folium.FeatureGroup(name='행정동 경계', show=True)

# 임의의 색상 생성하는 함수
def color_by_code(code):
    """ 행정동 코드를 기반으로 일관된 색상 생성 """
    import hashlib
    color_hash = hashlib.md5(str(code).encode())
    hue = int(color_hash.hexdigest(), 16) % 360
    return f'hsl({hue}, 50%, 80%)'  # 연한 파스텔 색상

# 행정동 경계를 GeoJson으로 추가
folium.GeoJson(
    data=busan_emd_data,
    name='Busan EMD',
    style_function=lambda feature: {
        'fillColor': color_by_code(feature['properties']['ADM_CD']) if 'ADM_CD' in feature['properties'] else '#cccccc',
        'color': 'black',
        'weight': 2,
        'fillOpacity': 0.1,
        'opacity': 1.0
    },
    highlight_function=lambda x: {'weight': 5, 'color': '#ff6600'},
    tooltip=folium.GeoJsonTooltip(
        fields=['ADM_NM'],
        aliases=[''],
        style="background-color: rgba(255,255,255,0.8); color: #333; font-weight: bold; font-size: 12px; padding: 5px; border-radius: 3px; box-shadow: 0 0 3px rgba(0,0,0,0.2);",
        sticky=False
    )
).add_to(boundary_group)

# 경계 그룹을 지도에 추가
boundary_group.add_to(m)

# 이름 마커를 위한 FeatureGroup 생성
name_group = folium.FeatureGroup(name='행정동 이름', show=False)

# 이름은 폴리곤의 모든 좌표 평균값(경계 중심 근사치)에 표시
for feature in busan_emd_data['features']:
    name = feature['properties'].get('ADM_NM') or feature['properties'].get('EMD_NM')
    geom = feature['geometry']
    coords = []
    if geom['type'] == 'Polygon':
        coords = geom['coordinates'][0]
    elif geom['type'] == 'MultiPolygon':
        coords = geom['coordinates'][0][0]
    if coords and name:
        lngs, lats = zip(*coords)
        lat = sum(lats) / len(lats)
        lng = sum(lngs) / len(lngs)

                # 아이콘과 마커를 완전히 제거하고 텍스트만 표시
        folium.map.Marker(
            [lat, lng],
            icon=folium.DivIcon(
                icon_size=(0, 0),  # 아이콘 크기를 0으로 설정
                icon_anchor=(0, 0),  # 아이콘 위치를 어긋히게 설정
                html=f'<div style="background:none; border:none; box-shadow:none; font-weight:bold; font-size:10pt; color:#000; text-shadow:1px 1px 1px #fff, -1px -1px 1px #fff, 1px -1px 1px #fff, -1px 1px 1px #fff; white-space:nowrap; display:inline-block; transform:translate(-50%,-50%); width:auto;">{name}</div>',
                class_name='transparent'
            )
        ).add_to(name_group)

# 이름 그룹을 지도에 추가
name_group.add_to(m)

# 중복 코드 제거 - 이미 name_group에 이름이 추가되었음

# 8. 병원 위치 빨간 점으로 표시 (팝업 가로) - 레이어 컨트롤용 FeatureGroup 사용
# 동물병원 레이어를 위한 FeatureGroup 생성
hospital_group = folium.FeatureGroup(name='동물병원', show=True)

for _, row in df.iterrows():
    name = row.get('사업장명', '')
    popup_html = f'<span style="white-space:nowrap">{name}</span>'
    folium.CircleMarker(
        location=[row['lat'], row['lng']],
        radius=4,
        color='red',
        fill=True,
        fill_color='red',
        fill_opacity=0.7,
        popup=folium.Popup(popup_html, max_width=200)
    ).add_to(hospital_group)
    
# FeatureGroup을 지도에 추가
hospital_group.add_to(m)

# 9. 통합 데이터(CSV)에서 모든 시설 정보 불러오기
# 필터링이 적용된 시설 데이터 로드 (단일 파일에서 모든 시설 정보 로드)
try:
    facilities_file = 'output/facilities_with_district_filtered.csv'
    
    if os.path.exists(facilities_file):
        facilities_df = pd.read_csv(facilities_file)
        print(f"필터링된 통합 시설 데이터 로드: {len(facilities_df)}개")
        print(f"시설 유형별 개수:\n{facilities_df['type'].value_counts()}")
    else:
        print(f"오류: 필터링된 시설 데이터 파일({facilities_file})을 찾을 수 없습니다.")
        facilities_df = pd.DataFrame()  # 빈 데이터프레임 생성
    # 공원 데이터 필터링
    parks_df = facilities_df[facilities_df['type'] == '공원'].copy()
    print(f"공원 데이터: {len(parks_df)}개")
    
    # 행정동명에 부산 구/군이 포함된 데이터 필터링
    filtered_parks_district = []
    for district in parks_df['district']:
        is_busan = False
        if isinstance(district, str):
            for busan_district in busan_districts:
                if busan_district in district:
                    is_busan = True
                    break
        filtered_parks_district.append(is_busan)
    
    # 좌표와 행정구역 기반으로 부산 지역 공원만 필터링
    parks_df = parks_df[
        (parks_df['y'] >= busan_lat_min) & 
        (parks_df['y'] <= busan_lat_max) & 
        (parks_df['x'] >= busan_lng_min) & 
        (parks_df['x'] <= busan_lng_max) &
        filtered_parks_district
    ]
    
    print(f"부산 지역으로 필터링된 공원 데이터: {len(parks_df)}개")
        
    # 행정동명에 부산 구/군이 포함된 데이터 필터링 (모든 시설 대상)
    filtered_districts = []
    for district in facilities_df['district']:
        is_busan = False
        if isinstance(district, str):
            for busan_district in busan_districts:
                if busan_district in district:
                    is_busan = True
                    break
            if district.endswith('동') or district.endswith('읍'):
                is_busan = True
        filtered_districts.append(is_busan)
    
    # 애견카페 데이터만 facilities_df에서 필터링
    # 애견카페 데이터 필터링 (좌표와 행정구역 기준)
    dog_cafes_df = facilities_df[
        (facilities_df['type'] == '애견카페') &
        (facilities_df['y'] >= busan_lat_min) & 
        (facilities_df['y'] <= busan_lat_max) & 
        (facilities_df['x'] >= busan_lng_min) & 
        (facilities_df['x'] <= busan_lng_max) &
        filtered_districts
    ]
    
    # 동물병원 데이터 필터링 (직접적으로 사용하지는 않지만, 정보 표시용)
    animal_hospitals_df = facilities_df[facilities_df['type'] == '동물병원']
    
    print(f'부산 지역 데이터로 필터링 결과:')
    print(f'- 동물병원: {len(animal_hospitals_df)}개')
    print(f'- 애견카페: {len(dog_cafes_df)}개')
    print(f'- 공원: {len(parks_df)}개')
    print(f'- 총 시설: {len(dog_cafes_df) + len(parks_df) + len(animal_hospitals_df)}개')
    
    # 애견카페 마커들을 FeatureGroup으로 묶음
    dog_cafe_group = folium.FeatureGroup(name='애견카페', show=False)
    
    # 카페 마커 추가
    for _, cafe in dog_cafes_df.iterrows():
        name = cafe.get('name', '')
        x = float(cafe.get('x', 0))  # 경도
        y = float(cafe.get('y', 0))  # 위도
        district = cafe.get('district', '')
        
        # 팝업 내용 구성
        popup_html = f'''
            <div style="width:200px">
                <h4 style="margin-bottom:5px">{name}</h4>
                <div style="font-size:0.9em; color:#666;">📍 {district} 소재</div>
            </div>
        '''
        
        # 파란색 원형 마커 추가
        folium.CircleMarker(
            location=[y, x],
            radius=5,
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=250)
        ).add_to(dog_cafe_group)
    
    # 애견카페 그룹을 지도에 추가
    dog_cafe_group.add_to(m)
    print(f'애견카페 {len(dog_cafes_df)}개를 지도에 추가했습니다.')
    
    # 공원 마커들을 FeatureGroup으로 묶음
    park_group = folium.FeatureGroup(name='공원', show=False)
    
    # 공원 마커 추가
    for _, park in parks_df.iterrows():
        name = park.get('name', '')
        x = float(park.get('x', 0))  # 경도
        y = float(park.get('y', 0))  # 위도
        district = park.get('district', '')
        
        # 팝업 내용 구성
        popup_html = f'''
            <div style="width:200px">
                <h4 style="margin-bottom:5px">{name}</h4>
                <div style="font-size:0.9em; color:#666;">📍 {district} 소재</div>
            </div>
        '''
        
        # 초록색 원형 마커 추가
        folium.CircleMarker(
            location=[y, x],
            radius=5,
            color='green',
            fill=True,
            fill_color='green',
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=250)
        ).add_to(park_group)
    
    # 공원 그룹을 지도에 추가
    park_group.add_to(m)
    print(f'공원 {len(parks_df)}개를 지도에 추가했습니다.')
    
except Exception as e:
    print(f'시설 데이터 로드 및 표시 중 오류 발생: {e}')

# 모든 레이어를 컨트롤할 수 있는 레이어 컨트롤 추가 (항상 펼쳐진 상태로 표시)
folium.LayerControl(collapsed=False).add_to(m)

os.makedirs('output', exist_ok=True)
output_path = 'output/vet_hospitals_busan_map.html'
m.save(output_path)
print(f'지도 시각화 완료: {output_path}')
