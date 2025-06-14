import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import seaborn as sns

# 간소화된 클러스터링 접근법
print("행정동별 시설 데이터 로드 중...")
df = pd.read_csv('output/district_facility_counts_updated.csv')
print(f"분석에 사용할 데이터 형태: {df.shape}")
print(df.head())

# 각 시설 유형별로 분포를 확인 (상위 25%, 50%, 75% 기준)
hospital_q = df['hospital'].quantile([0.5, 0.75, 0.9]).values
cafe_q = df['cafe'].quantile([0.5, 0.75, 0.9]).values
park_q = df['park'].quantile([0.5, 0.75, 0.9]).values

print(f"\n동물병원 분위수: 50%={hospital_q[0]}, 75%={hospital_q[1]}, 90%={hospital_q[2]}")
print(f"애견카페 분위수: 50%={cafe_q[0]}, 75%={cafe_q[1]}, 90%={cafe_q[2]}")
print(f"공원 분위수: 50%={park_q[0]}, 75%={park_q[1]}, 90%={park_q[2]}")

# 특성에 따라 수동 클러스터링 (규칙 기반)
def assign_cluster(row):
    # 클러스터 0: 종합 인프라형 (병원, 카페, 공원 모두 풍부)
    if row['hospital'] >= hospital_q[1] and row['cafe'] >= cafe_q[1] and row['park'] >= park_q[1]:
        return 0
    
    # 클러스터 1: 의료 중심형 (병원 많음)
    elif row['hospital'] >= hospital_q[1]:
        return 1
    
    # 클러스터 2: 여가 중심형 (공원 많음)
    elif row['park'] >= park_q[1]:
        return 2
    
    # 클러스터 3: 카페 문화형 (카페 많음)
    elif row['cafe'] >= cafe_q[1]:
        return 3
    
    # 클러스터 4: 기본 인프라형 (모두 평균 이하)
    else:
        return 4

# 클러스터 할당
df['cluster'] = df.apply(assign_cluster, axis=1)

# 클러스터별 평균값 계산
cluster_means = df.groupby('cluster')[['hospital', 'cafe', 'park']].mean().reset_index()
cluster_means = cluster_means.round(1)  # 소수점 첫째 자리까지 반올림

# 각 클러스터의 동네 수 계산
cluster_counts = df.groupby('cluster').size().reset_index(name='동네_수')
cluster_df = pd.merge(cluster_means, cluster_counts, on='cluster')

# 클러스터 유형 이름 부여
cluster_names = {
    0: "종합 인프라형",
    1: "의료 중심형",
    2: "여가 중심형",
    3: "카페 문화형",
    4: "기본 인프라형"
}
cluster_df['유형'] = cluster_df['cluster'].map(cluster_names)

# 클러스터별 색상 지정
colors = ['#FF5733', '#33FF57', '#3357FF', '#FF33A8', '#FFD700']
cluster_df['색상'] = [colors[i] for i in range(len(cluster_df))]

print("\n클러스터별 특성:")
print(cluster_df)

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

# 행정동별 클러스터 정보를 JavaScript로 저장
district_clusters = df[['district', 'cluster']].to_dict('records')
with open('output/district_clusters.json', 'w', encoding='utf-8') as f:
    json.dump(district_clusters, f, ensure_ascii=False, indent=2)
print("행정동별 클러스터 정보가 output/district_clusters.json에 저장되었습니다.")

# 클러스터별 특성을 막대 그래프로 시각화
plt.figure(figsize=(15, 10))
for col in ['hospital', 'cafe', 'park']:
    plt.subplot(3, 1, ['hospital', 'cafe', 'park'].index(col) + 1)
    sns.barplot(x='cluster', y=col, data=cluster_df, palette=[colors[i] for i in cluster_df['cluster']])
    plt.title(f'클러스터별 {col} 평균')
    plt.xticks(range(len(cluster_df)), [f"{row['cluster']}: {row['유형']} ({row['동네_수']}개)" for _, row in cluster_df.iterrows()])
    plt.ylabel('평균 개수')

plt.tight_layout()
plt.savefig('output/cluster_bar_chart.png')
print("클러스터별 막대 그래프가 output/cluster_bar_chart.png에 저장되었습니다.")

# 행정동별 클러스터 정보를 JavaScript 배열로 저장 (직접 삽입 가능)
district_cluster_js = []
for _, row in df.iterrows():
    district_cluster_js.append(
        f"    {{ district: '{row['district']}', cluster: {row['cluster']}, type: '{cluster_names[row['cluster']]}', color: '{colors[row['cluster']]}'  }}"
    )

with open('output/district_clusters.js', 'w', encoding='utf-8') as f:
    f.write("// 행정동별 클러스터(유형) 정보\n")
    f.write("const districtClusters = [\n")
    f.write(",\n".join(district_cluster_js))
    f.write("\n];\n\n")
    
    f.write("// 클러스터 유형별 정보\n")
    f.write("const clusterInfo = [\n")
    for i, cluster in enumerate(cluster_info):
        f.write(f"    {{ id: {cluster['cluster']}, name: '{cluster['유형']}', color: '{cluster['색상']}', ")
        f.write(f"hospital: {cluster['hospital']}, cafe: {cluster['cafe']}, park: {cluster['park']}, ")
        f.write(f"count: {cluster['동네_수']} }}")
        if i < len(cluster_info) - 1:
            f.write(",\n")
        else:
            f.write("\n")
    f.write("];\n")
print("행정동별 클러스터 정보와 클러스터 유형별 정보가 output/district_clusters.js 파일에 저장되었습니다.")

print("\n클러스터링 분석이 완료되었습니다!")
