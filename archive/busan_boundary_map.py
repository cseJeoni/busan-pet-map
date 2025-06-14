import geopandas as gpd
import matplotlib.pyplot as plt

# 1. 한글 폰트 설정 (Mac 기준, 없으면 NanumGothic 등 사용)
plt.rcParams['font.family'] = 'AppleGothic'   # 또는 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

# 2. shp/zip 파일 불러오기
shp_path = "BND_ADM_DONG_PG/BND_ADM_DONG_PG.shp"  # 또는 .shp 경로

gdf = gpd.read_file(shp_path)
print(gdf.columns)
print(gdf.head(3))   # 컬럼/동 이름/코드 확인

# 3. 부산광역시만 추출 (ADM_CD 앞 두자리가 26이면 부산, 21이면 서울)
gdf_busan = gdf[gdf['ADM_CD'].astype(str).str.startswith('21')]
print(f"부산 동 개수: {len(gdf_busan)}")

# 4. 지도 시각화 및 동 이름 표시
fig, ax = plt.subplots(figsize=(12, 12))
gdf_busan.plot(ax=ax, edgecolor='black', alpha=0.7, linewidth=0.8)

plt.title('부산광역시 행정동 경계', fontsize=16)

# 동 이름을 각 폴리곤 중심에 표시
for idx, row in gdf_busan.iterrows():
    try:
        # 여러 폴리곤이 있는 경우 가장 큰 폴리곤의 중심 사용
        centroid = row['geometry'].centroid
        plt.annotate(row['ADM_NM'], 
                     xy=(centroid.x, centroid.y),
                     ha='center', va='center', fontsize=7, color='navy')
    except:
        pass  # 폴리곤에 문제가 있을 경우는 생략

plt.axis('off')
plt.tight_layout()
plt.show()