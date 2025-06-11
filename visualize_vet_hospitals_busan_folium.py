"""
부산 동물병원 위치를 folium으로 지도에 빨간 점으로 시각화 (웹 브라우저에서 확인)
- 입력: data/vet_hospitals_busan.csv
- 출력: output/vet_hospitals_busan_map.html
"""
import os
import pandas as pd
import folium
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

df['lat'], df['lng'] = zip(*df.apply(lambda row: to_latlng(row[x_col], row[y_col]), axis=1))

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

# 9. 카카오 API로 검색한 부산 애견카페 위치를 파란색 점으로 표시
try:
    # 애견카페 데이터 로드
    with open('data/busan_dog_cafes.json', encoding='utf-8') as f:
        dog_cafes = json.load(f)
    
    # 애견카페 마커들을 FeatureGroup으로 묶음
    dog_cafe_group = folium.FeatureGroup(name='애견카페', show=False)
    
    # 카페 마커 추가
    for cafe in dog_cafes:
        name = cafe.get('place_name', '')
        x = float(cafe.get('x', 0))  # 경도
        y = float(cafe.get('y', 0))  # 위도
        address = cafe.get('address_name', '')
        road_address = cafe.get('road_address_name', '')
        phone = cafe.get('phone', '')
        
        # 팝업 내용 구성
        popup_html = f'''
            <div style="width:200px">
                <h4 style="margin-bottom:5px">{name}</h4>
                <div style="font-size:0.9em; color:#666;">📍 {road_address or address}</div>
                {f'<div style="font-size:0.9em; margin-top:2px;">☎️ {phone}</div>' if phone else ''}
            </div>
        '''
        
        # 파란색 원형 마커 추가
        folium.CircleMarker(
            location=[y, x],  # 카카오맵 API는 (경도, 위도) 순으로 좌표 제공
            radius=5,
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=250)
        ).add_to(dog_cafe_group)
    
    # 애견카페 그룹을 지도에 추가
    dog_cafe_group.add_to(m)
    print(f'애견카페 {len(dog_cafes)}개를 지도에 추가했습니다.')
    
except Exception as e:
    print(f'애견카페 데이터 로드 및 표시 중 오류 발생: {e}')

# 10. 카카오 API로 검색한 부산 공원 위치를 초록색 점으로 표시
try:
    # 공원 데이터 로드
    with open('data/busan_parks.json', encoding='utf-8') as f:
        parks = json.load(f)
    
    # 공원 마커들을 FeatureGroup으로 묶음
    park_group = folium.FeatureGroup(name='공원', show=False)
    
    # 공원 마커 추가
    for park in parks:
        name = park.get('place_name', '')
        x = float(park.get('x', 0))  # 경도
        y = float(park.get('y', 0))  # 위도
        address = park.get('address_name', '')
        road_address = park.get('road_address_name', '')
        phone = park.get('phone', '')
        
        # 팝업 내용 구성
        popup_html = f'''
            <div style="width:200px">
                <h4 style="margin-bottom:5px">{name}</h4>
                <div style="font-size:0.9em; color:#666;">📍 {road_address or address}</div>
                {f'<div style="font-size:0.9em; margin-top:2px;">☎️ {phone}</div>' if phone else ''}
            </div>
        '''
        
        # 초록색 원형 마커 추가
        folium.CircleMarker(
            location=[y, x],  # 카카오맵 API는 (경도, 위도) 순으로 좌표 제공
            radius=5,
            color='green',
            fill=True,
            fill_color='green',
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=250)
        ).add_to(park_group)
    
    # 공원 그룹을 지도에 추가
    park_group.add_to(m)
    print(f'공원 {len(parks)}개를 지도에 추가했습니다.')
    
except Exception as e:
    print(f'공원 데이터 로드 및 표시 중 오류 발생: {e}')

# 모든 레이어를 컨트롤할 수 있는 레이어 컨트롤 추가 (항상 펼쳐진 상태로 표시)
folium.LayerControl(collapsed=False).add_to(m)

os.makedirs('output', exist_ok=True)
output_path = 'output/vet_hospitals_busan_map.html'
m.save(output_path)
print(f'지도 시각화 완료: {output_path}')
