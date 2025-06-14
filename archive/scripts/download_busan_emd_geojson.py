"""
부산시 행정동(법정동, EMD) GeoJSON 자동 다운로드 및 부산만 추출
- 전국 EMD GeoJSON에서 부산시(시도코드 26)만 필터링
- 결과: data/busan_emd.geojson
"""
import os
import requests
import geopandas as gpd

# 1. 전국 EMD GeoJSON 다운로드
emd_url = "https://raw.githubusercontent.com/southkorea/southkorea-maps/master/kostat/emd/emd_202101.geojson"
data_dir = "data"
os.makedirs(data_dir, exist_ok=True)
nat_emd_path = os.path.join(data_dir, "emd_national.geojson")
busan_emd_path = os.path.join(data_dir, "busan_emd.geojson")

if not os.path.exists(nat_emd_path):
    print("전국 EMD GeoJSON 다운로드...")
    r = requests.get(emd_url)
    with open(nat_emd_path, "wb") as f:
        f.write(r.content)
else:
    print("전국 EMD GeoJSON 이미 존재")

# 2. 부산시만 필터링 (시도코드 26, 혹은 시도명 '부산광역시')
gdf = gpd.read_file(nat_emd_path)
if 'sidonm' in gdf.columns:
    busan_gdf = gdf[gdf['sidonm'].str.contains('부산')]
elif 'CTP_KOR_NM' in gdf.columns:
    busan_gdf = gdf[gdf['CTP_KOR_NM'].str.contains('부산')]
else:
    busan_gdf = gdf[gdf['EMD_CD'].astype(str).str.startswith('26')]

print(f"부산시 행정동 개수: {len(busan_gdf)}")
busan_gdf.to_file(busan_emd_path, driver="GeoJSON")
print(f"저장 완료: {busan_emd_path}")
