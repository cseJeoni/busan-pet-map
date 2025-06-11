import json
import csv
import os
import pandas as pd
from shapely.geometry import Point, shape
from pyproj import Transformer

def load_geojson(file_path):
    """행정동 GeoJSON 파일 로드"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def count_facilities_by_district(geojson_data, facilities, district_name_field='ADM_NM'):
    """
    각 행정동별 시설 개수 계산
    
    Args:
        geojson_data: 행정동 경계 GeoJSON 데이터
        facilities: 시설 목록 (각 항목은 name, x, y 필드를 포함한 dict)
        district_name_field: GeoJSON에서 행정동 이름이 저장된 필드명
        
    Returns:
        dict: 행정동별 시설 개수
    """
    district_count = {}
    
    # 각 행정동의 폴리곤 객체와 이름 준비
    districts = []
    for feature in geojson_data['features']:
        district_name = feature['properties'].get(district_name_field, '알 수 없음')
        district_geom = shape(feature['geometry'])
        districts.append((district_name, district_geom))
        
        # 결과 딕셔너리 초기화
        if district_name not in district_count:
            district_count[district_name] = 0
    
    # 각 시설이 어느 행정동에 속하는지 확인
    facilities_with_district = []
    for facility in facilities:
        x, y = float(facility.get('x', 0)), float(facility.get('y', 0))
        point = Point(x, y)
        
        district_found = False
        for district_name, district_geom in districts:
            if district_geom.contains(point):
                district_count[district_name] += 1
                facilities_with_district.append({
                    **facility,
                    'district': district_name
                })
                district_found = True
                break
        
        # 어떤 행정동에도 속하지 않는 경우
        if not district_found:
            facilities_with_district.append({
                **facility,
                'district': '경계 외'
            })
    
    return district_count, facilities_with_district

def main():
    # 행정동 경계 데이터 로드
    busan_geojson = load_geojson('data/busan_emd_wgs84.geojson')
    
    # 동물병원 데이터 로드 및 좌표 변환
    vet_hospitals = []
    df = pd.read_csv('data/vet_hospitals_busan.csv')
    
    # 좌표 결측치 및 이상치 제거
    x_col = '좌표정보x(epsg5174)'
    y_col = '좌표정보y(epsg5174)'
    df = df[df[x_col].notnull() & df[y_col].notnull()]
    df = df[(df[x_col] != '') & (df[y_col] != '')]
    
    # 좌표를 float로 변환
    df[x_col] = df[x_col].astype(float)
    df[y_col] = df[y_col].astype(float)
    
    # UTM-K(EPSG:5174) → WGS84(경위도) 변환
    transformer = Transformer.from_crs("epsg:5174", "epsg:4326", always_xy=True)
    
    for _, row in df.iterrows():
        lng, lat = transformer.transform(row[x_col], row[y_col])
        vet_hospitals.append({
            'name': row.get('사업장명', ''),
            'x': lng,  # 경도
            'y': lat,  # 위도
            'type': '동물병원'
        })
    
    # 애견카페 데이터 로드
    dog_cafes = []
    try:
        with open('data/busan_dog_cafes_all.json', 'r', encoding='utf-8') as f:
            dog_cafes_data = json.load(f)
            for cafe in dog_cafes_data:
                dog_cafes.append({
                    'name': cafe.get('place_name', ''),
                    'x': float(cafe.get('x', 0)),
                    'y': float(cafe.get('y', 0)),
                    'type': '애견카페'
                })
    except Exception as e:
        print(f"애견카페 데이터 로드 중 오류: {e}")
    
    # 공원 데이터 로드
    parks = []
    try:
        with open('data/busan_parks_all.json', 'r', encoding='utf-8') as f:
            parks_data = json.load(f)
            for park in parks_data:
                parks.append({
                    'name': park.get('place_name', ''),
                    'x': float(park.get('x', 0)),
                    'y': float(park.get('y', 0)),
                    'type': '공원'
                })
    except Exception as e:
        print(f"공원 데이터 로드 중 오류: {e}")
    
    # 각 시설 유형별 행정동 카운트
    hospital_counts, hospitals_with_district = count_facilities_by_district(busan_geojson, vet_hospitals)
    cafe_counts, cafes_with_district = count_facilities_by_district(busan_geojson, dog_cafes)
    park_counts, parks_with_district = count_facilities_by_district(busan_geojson, parks)
    
    # 결과를 병합하여 모든 행정동과 시설 유형별 개수 생성
    all_districts = set(hospital_counts.keys()) | set(cafe_counts.keys()) | set(park_counts.keys())
    
    results = []
    for district in sorted(all_districts):
        results.append({
            '행정동': district,
            '동물병원': hospital_counts.get(district, 0),
            '애견카페': cafe_counts.get(district, 0),
            '공원': park_counts.get(district, 0),
            '총합': hospital_counts.get(district, 0) + cafe_counts.get(district, 0) + park_counts.get(district, 0)
        })
    
    # 시설 수 합계를 기준으로 내림차순 정렬
    results.sort(key=lambda x: x['총합'], reverse=True)
    
    # 결과를 CSV로 저장
    os.makedirs('output', exist_ok=True)
    with open('output/district_facility_counts_all.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['행정동', '동물병원', '애견카페', '공원', '총합'])
        writer.writeheader()
        writer.writerows(results)
    
    # 시설별 소속 행정동 정보도 저장
    all_facilities = hospitals_with_district + cafes_with_district + parks_with_district
    with open('output/facilities_with_district.csv', 'w', encoding='utf-8', newline='') as f:
        if all_facilities:
            writer = csv.DictWriter(f, fieldnames=['name', 'x', 'y', 'type', 'district'])
            writer.writeheader()
            writer.writerows(all_facilities)
    
    print(f"행정동별 시설 개수 분석 완료: output/district_facility_counts.csv")
    print(f"시설별 소속 행정동 정보: output/facilities_with_district.csv")
    
    return results

if __name__ == "__main__":
    main()
