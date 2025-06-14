"""
부산 동물병원 위치를 지도 위에 빨간 점으로 시각화
- 입력: data/vet_hospitals_busan.csv
- 출력: output/vet_hospitals_busan_map.png
"""
import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt

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

# 4. GeoDataFrame 생성 (EPSG:5174, UTM-K)
gdf = gpd.GeoDataFrame(
    df,
    geometry=[Point(x, y) for x, y in zip(df[x_col], df[y_col])],
    crs='EPSG:5174'
)

# 5. EPSG:4326(경위도)로 변환
busan_gdf = gdf.to_crs(epsg=4326)

# 6. 지도 시각화
fig, ax = plt.subplots(figsize=(10, 10))
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
# 대한민국만 필터링 (혹은 world 전체)
world[world['name'] == 'South Korea'].plot(ax=ax, color='lightgray', edgecolor='k')

busan_gdf.plot(ax=ax, color='red', markersize=20, alpha=0.7, label='Busan Vet Hospital')

plt.title('부산 동물병원 위치 분포 (빨간 점)', fontsize=16)
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.legend()
plt.tight_layout()

os.makedirs('output', exist_ok=True)
plt.savefig('output/vet_hospitals_busan_map.png', dpi=200)
plt.close()

print('지도 시각화 완료: output/vet_hospitals_busan_map.png')
