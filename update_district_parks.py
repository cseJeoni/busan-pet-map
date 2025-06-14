import pandas as pd
import json
import folium
from shapely.geometry import Point, Polygon
import geopandas as gpd
import os

# 필터링된 시설 데이터 읽기
df = pd.read_csv('output/facilities_with_district_filtered.csv')

# 부산 행정구역 경계 GeoJSON 파일이 있는지 확인
if not os.path.exists('data/busan_emd_wgs84.geojson'):
    print("부산 행정구역 경계 파일이 없습니다. 먼저 행정구역 경계 파일을 준비해주세요.")
    exit(1)

# 부산 행정구역 경계 데이터 로드
busan_districts = gpd.read_file('data/busan_emd_wgs84.geojson')
# 행정동 이름 필드 확인
print(f"GeoJSON 파일 컬럼: {busan_districts.columns}")

# 공원 데이터만 필터링
parks_df = df[df['type'] == '공원'].copy()

# 부산 지역으로 필터링
busan_lat_min, busan_lat_max = 34.8, 35.4
busan_lon_min, busan_lon_max = 128.7, 129.4

parks_df = parks_df[
    (parks_df['y'] >= busan_lat_min) & 
    (parks_df['y'] <= busan_lat_max) & 
    (parks_df['x'] >= busan_lon_min) & 
    (parks_df['x'] <= busan_lon_max)
]

print(f"부산 좌표 범위내 공원 수: {len(parks_df)}개")

# 좌표로 행정동 매핑 함수
def get_district(point, busan_districts):
    for idx, district in busan_districts.iterrows():
        polygon = district['geometry']
        if polygon.contains(point):
            # 행정동 이름 필드가 EMD_NM, EMD_KOR_NM, ADM_NM 등 다양할 수 있으므로 확인
            for field in ['EMD_KOR_NM', 'EMD_NM', 'adm_nm', 'ADM_NM', 'name']:
                if field in district:
                    return district[field]
    return "미확인"

# 공원 좌표를 행정동에 매핑
result = []
parks_with_districts = []

# 행정동 이름 필드 찾기
emd_field = None
for field in ['EMD_KOR_NM', 'EMD_NM', 'adm_nm', 'ADM_NM', 'name']:
    if field in busan_districts.columns:
        emd_field = field
        print(f"행정동 이름 필드: {emd_field}")
        break

if not emd_field:
    print("행정동 이름 필드를 찾을 수 없습니다.")
    exit(1)

# 기존 district_data.js 파일 불러오기
with open('output/district_data.js', 'r', encoding='utf-8') as f:
    content = f.read()
    
# 필요한 부분만 추출
import re
district_data_str = re.search(r'const districtData = \[([\s\S]*?)\];', content).group(1)
district_data_lines = [line.strip() for line in district_data_str.split('\n') if line.strip()]

# JavaScript 형식을 Python 딕셔너리로 변환
district_data = []
for line in district_data_lines:
    # 쉼표 제거
    if line.endswith(','):
        line = line[:-1]
    
    # 정규식으로 데이터 추출
    match = re.match(r'\{ district: \'(.*?)\', hospital: (\d+), cafe: (\d+), park: (\d+) \}', line)
    if match:
        district, hospital, cafe, park = match.groups()
        district_data.append({
            'district': district,
            'hospital': int(hospital),
            'cafe': int(cafe),
            'park': int(park)
        })

# 행정동 이름 목록
district_names = [d['district'] for d in district_data]
print(f"기존 데이터의 행정동 수: {len(district_names)}개")

# 공원 좌표를 Shapely Point 객체로 변환하여 행정동 찾기
for idx, park in parks_df.iterrows():
    point = Point(park['x'], park['y'])
    for _, district in busan_districts.iterrows():
        if district['geometry'].contains(point):
            # 행정동 이름 필드 찾기
            district_name = None
            for field in ['EMD_KOR_NM', 'EMD_NM', 'adm_nm', 'ADM_NM', 'name']:
                if field in district and district[field]:
                    district_name = district[field]
                    break
            
            if not district_name:
                continue
                
            parks_with_districts.append({
                'name': park['name'],
                'x': park['x'],
                'y': park['y'],
                'district': district_name
            })
            # 이미 결과에 있는 행정동인지 확인
            found = False
            for r in result:
                if r['district'] == district_name:
                    r['count'] += 1
                    found = True
                    break
            if not found:
                result.append({'district': district_name, 'count': 1})
            break

print(f"행정동별로 분류된 공원 수: {len(parks_with_districts)}개")
print(f"공원이 있는 행정동 수: {len(result)}개")

# 결과를 행정동별로 정렬
result.sort(key=lambda x: x['count'], reverse=True)

# 행정동별 공원 수 출력
print("\n행정동별 공원 수 (상위 10개):")
for i, item in enumerate(sorted(result, key=lambda x: x['count'], reverse=True)[:10]):
    print(f"{i+1}. {item['district']}: {item['count']}개")

# 기존 district_data에 공원 정보 업데이트
updated_district_data = []
for d in district_data:
    district_name = d['district']
    park_count = 0
    
    # 결과 데이터에서 해당 행정동의 공원 수 찾기
    for r in result:
        if r['district'] == district_name:
            park_count = r['count']
            break
    
    updated_district_data.append({
        'district': district_name,
        'hospital': d['hospital'],
        'cafe': d['cafe'],
        'park': park_count
    })

# JavaScript 파일로 저장
js_array = []
for row in updated_district_data:
    js_array.append(f"    {{ district: '{row['district']}', hospital: {row['hospital']}, cafe: {row['cafe']}, park: {row['park']} }}")

with open('output/updated_district_data.js', 'w', encoding='utf-8') as f:
    f.write("// 행정동별 시설 데이터 (필터링된 데이터 기준, 공원 데이터 정확히 매핑)\n")
    f.write("const districtData = [\n")
    f.write(",\n".join(js_array))
    f.write("\n];")

print(f"\n업데이트된 districtData가 output/updated_district_data.js 파일에 저장되었습니다.")

# CSV 파일로도 저장
df_result = pd.DataFrame(updated_district_data)
df_result.to_csv('output/district_facility_counts_updated.csv', index=False)

print(f"업데이트된 데이터가 output/district_facility_counts_updated.csv 파일에도 저장되었습니다.")
