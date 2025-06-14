import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import json
import seaborn as sns

# 행정동별 시설 데이터 로드
print("행정동별 시설 데이터 로드 중...")
df = pd.read_csv('output/district_facility_counts_updated.csv')

# 필요한 특성만 선택
print(f"분석에 사용할 데이터 형태: {df.shape}")
print(df.head())

# 클러스터링을 위한 특성 선택 (hospital, cafe, park)
features = df[['hospital', 'cafe', 'park']].values

# 데이터 정규화 (스케일링)
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

# 최적의 클러스터 수 결정 (Elbow Method)
inertia = []
k_range = range(2, 10)
for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(features_scaled)
    inertia.append(kmeans.inertia_)

# Elbow Method 그래프 저장
plt.figure(figsize=(10, 6))
plt.plot(k_range, inertia, 'bo-')
plt.xlabel('클러스터 수 (k)')
plt.ylabel('왜곡 (Inertia)')
plt.title('Elbow Method로 최적 클러스터 수 찾기')
plt.grid(True)
plt.savefig('output/elbow_method.png')
print("Elbow Method 결과가 output/elbow_method.png에 저장되었습니다.")

# 적절한 클러스터 수 선택 (결과를 보고 적절히 조정)
optimal_k = 5  # 그래프 결과에 따라 조정 가능
print(f"선택된 클러스터 수: {optimal_k}")

# K-means 클러스터링 적용
kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
df['cluster'] = kmeans.fit_predict(features_scaled)

# 클러스터 중심점 (특성별 평균값) 계산
cluster_centers = scaler.inverse_transform(kmeans.cluster_centers_)
cluster_df = pd.DataFrame(cluster_centers, 
                         columns=['hospital', 'cafe', 'park'])
cluster_df = cluster_df.round(1)  # 소수점 첫째 자리까지 반올림

# 각 클러스터의 동네 수 계산
cluster_counts = df.groupby('cluster').size().reset_index(name='동네_수')
cluster_df = pd.merge(cluster_df, cluster_counts, on='cluster')

# 클러스터 특성에 따라 유형 이름 부여
def get_cluster_name(row):
    if row['hospital'] > 5 and row['park'] > 5:
        return "종합 인프라형"
    elif row['hospital'] > 5 and row['park'] <= 5:
        return "의료 중심형"
    elif row['hospital'] <= 5 and row['park'] > 10:
        return "여가 중심형"
    elif row['cafe'] > 1:
        return "카페 문화형"
    else:
        return "기본 인프라형"

cluster_df['유형'] = cluster_df.apply(get_cluster_name, axis=1)
print("\n클러스터별 특성:")
print(cluster_df)

# 클러스터 색상 지정
colors = ['#FF5733', '#33FF57', '#3357FF', '#FF33A8', '#FFD700']
cluster_df['색상'] = [colors[i] for i in range(len(cluster_df))]

# 결과를 CSV 파일로 저장
df.to_csv('output/district_clusters.csv', index=False)
print("\n행정동별 클러스터 결과가 output/district_clusters.csv에 저장되었습니다.")

# 클러스터 요약 정보 저장
cluster_df.to_csv('output/cluster_summary.csv', index=False)
print("클러스터 요약 정보가 output/cluster_summary.csv에 저장되었습니다.")

# 클러스터 정보를 JSON으로 저장 (JavaScript에서 사용)
cluster_info = cluster_df[['cluster', '유형', '색상', 'hospital', 'cafe', 'park', '동네_수']].to_dict('records')
with open('output/cluster_info.json', 'w', encoding='utf-8') as f:
    json.dump(cluster_info, f, ensure_ascii=False, indent=2)
print("클러스터 정보가 output/cluster_info.json에 저장되었습니다.")

# 행정동별 클러스터 정보를 JSON으로 저장
district_clusters = df[['district', 'cluster']].to_dict('records')
with open('output/district_clusters.json', 'w', encoding='utf-8') as f:
    json.dump(district_clusters, f, ensure_ascii=False, indent=2)
print("행정동별 클러스터 정보가 output/district_clusters.json에 저장되었습니다.")

# 클러스터별 특성을 레이더 차트로 시각화
features = ['hospital', 'cafe', 'park']
n_features = len(features)

# 각 클러스터에 대한 레이더 차트 생성
plt.figure(figsize=(15, 10))

for i, row in cluster_df.iterrows():
    values = row[features].values.flatten().tolist()
    values += values[:1]  # 닫힌 다각형을 위해 첫 값을 마지막에 복제
    
    angles = [n/float(n_features)*2*np.pi for n in range(n_features)]
    angles += angles[:1]  # 닫힌 다각형을 위해 첫 각도를 마지막에 복제
    
    ax = plt.subplot(2, 3, i+1, polar=True)
    plt.xticks(angles[:-1], features, color='grey', size=12)
    plt.yticks([])
    
    ax.set_title(f"클러스터 {row['cluster']} - {row['유형']}\n(동네 수: {row['동네_수']}개)", size=14)
    
    ax.plot(angles, values, linewidth=2, linestyle='solid', color=row['색상'])
    ax.fill(angles, values, color=row['색상'], alpha=0.4)

plt.tight_layout()
plt.savefig('output/cluster_radar_chart.png')
print("클러스터별 레이더 차트가 output/cluster_radar_chart.png에 저장되었습니다.")

print("\n클러스터링 분석이 완료되었습니다!")
