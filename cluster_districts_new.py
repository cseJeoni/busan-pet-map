#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
부산시 행정동별 반려견 시설 데이터 클러스터링 분석
- SOLID 원칙과 Clean Architecture 적용
- 행정동별 시설 데이터를 클러스터링하여 유사한 특성을 가진 그룹으로 분류
"""

import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import matplotlib.cm as cm
from matplotlib.colors import rgb2hex

# 도메인 계층 - 엔티티 및 도메인 모델
class District:
    """행정동 정보 모델"""
    def __init__(self, name):
        self.name = name
        self.facilities = {'동물병원': 0, '애견카페': 0, '공원': 0}
    
    def add_facility(self, facility_type):
        """시설 추가"""
        if facility_type in self.facilities:
            self.facilities[facility_type] += 1
    
    def get_features(self):
        """클러스터링에 사용할 특성 벡터 반환"""
        return [
            self.facilities['동물병원'], 
            self.facilities['애견카페'], 
            self.facilities['공원']
        ]

# 유스케이스 계층 - 클러스터링 서비스
class ClusteringService:
    """행정동 클러스터링 서비스"""
    def __init__(self):
        self.scaler = StandardScaler()
        
    def find_optimal_clusters(self, features, max_clusters=10):
        """최적의 클러스터 수 결정"""
        silhouette_scores = []
        
        # 최소 2개부터 max_clusters까지 실루엣 점수 계산
        for n_clusters in range(2, max_clusters + 1):
            # 클러스터링 수행
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(features)
            
            # 실루엣 점수 계산 (클러스터가 2개 이상일 때만 계산 가능)
            if len(np.unique(cluster_labels)) > 1:
                silhouette_avg = silhouette_score(features, cluster_labels)
                silhouette_scores.append((n_clusters, silhouette_avg))
                print(f"n_clusters={n_clusters}: 실루엣 점수={silhouette_avg:.3f}")
        
        # 실루엣 점수가 가장 높은 클러스터 수 선택
        if silhouette_scores:
            optimal_n_clusters = max(silhouette_scores, key=lambda x: x[1])[0]
            return optimal_n_clusters
        else:
            # 기본값으로 5개 클러스터 반환
            return 5
    
    def perform_clustering(self, district_features, district_names, n_clusters=5):
        """K-means 클러스터링 수행"""
        # 데이터 표준화
        scaled_features = self.scaler.fit_transform(district_features)
        
        # K-means 클러스터링
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(scaled_features)
        
        # 클러스터 중심 역변환하여 원래 스케일로 변환
        cluster_centers = self.scaler.inverse_transform(kmeans.cluster_centers_)
        
        # 클러스터별 행정동 그룹화
        clusters = {}
        for i, district in enumerate(district_names):
            cluster_id = int(cluster_labels[i])
            if cluster_id not in clusters:
                clusters[cluster_id] = []
            clusters[cluster_id].append(district)
        
        return {
            'cluster_labels': cluster_labels,
            'cluster_centers': cluster_centers,
            'clusters': clusters
        }
    
    def assign_cluster_types(self, cluster_centers):
        """클러스터 유형 부여"""
        cluster_types = []
        colors = ['#FF5733', '#33FF57', '#3357FF', '#FF33A8', '#FFD700', '#33CFFF', '#E533FF', '#FF5733']
        
        # 클러스터 특성에 따른 유형 부여
        for i, center in enumerate(cluster_centers):
            hospital, cafe, park = center
            
            # 클러스터 특성에 따른 유형 구분
            if hospital > 5 and park > 10:
                cluster_type = "종합 인프라형"
            elif hospital > 4:
                cluster_type = "의료 중심형"
            elif park > 7:
                cluster_type = "여가 중심형"
            elif cafe > 1:
                cluster_type = "카페 문화형"
            else:
                cluster_type = "기본 인프라형"
            
            # 색상은 인덱스 순서대로 지정
            color = colors[i % len(colors)]
            
            cluster_types.append({
                'cluster': i,
                '유형': cluster_type,
                '색상': color,
                'hospital': round(hospital, 1),
                'cafe': round(cafe, 1),
                'park': round(park, 1)
            })
        
        return cluster_types

# 인프라 계층 - 데이터 액세스 및 저장
class FacilityDataRepository:
    """시설 데이터 저장소"""
    def load_facility_data(self, filepath):
        """시설 데이터 로드"""
        try:
            df = pd.read_csv(filepath)
            return df
        except Exception as e:
            print(f"데이터 로드 오류: {e}")
            return None
    
    def save_cluster_results(self, cluster_types, district_clusters, output_dir):
        """클러스터링 결과 저장"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 클러스터 유형 정보 저장
        for cluster_type in cluster_types:
            # 행정동 수 계산
            cluster_id = cluster_type['cluster']
            count = sum(1 for item in district_clusters if item['cluster'] == cluster_id)
            cluster_type['동네_수'] = count
        
        # JSON 형식으로 저장
        with open(os.path.join(output_dir, 'cluster_info.json'), 'w', encoding='utf-8') as f:
            json.dump(cluster_types, f, ensure_ascii=False, indent=2)
        
        with open(os.path.join(output_dir, 'district_clusters.json'), 'w', encoding='utf-8') as f:
            json.dump(district_clusters, f, ensure_ascii=False, indent=2)
        
        print(f"클러스터링 결과가 {output_dir} 디렉토리에 저장되었습니다.")
        
        return cluster_types, district_clusters

# 유틸리티 함수
def visualize_clusters(cluster_types, district_clusters, output_dir):
    """클러스터 결과 시각화"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 클러스터별 행정동 수
    cluster_counts = {}
    for item in district_clusters:
        cluster = item['cluster']
        if cluster not in cluster_counts:
            cluster_counts[cluster] = 0
        cluster_counts[cluster] += 1
    
    # 클러스터별 색상 매핑
    cluster_colors = {}
    for cluster_type in cluster_types:
        cluster_id = cluster_type['cluster']
        cluster_colors[cluster_id] = cluster_type['색상']
    
    # 바 차트로 시각화
    plt.figure(figsize=(12, 6))
    
    # 클러스터별 특성 시각화
    clusters = sorted([c['cluster'] for c in cluster_types])
    
    # 각 특성별 바 그래프
    bar_width = 0.25
    hospital_data = [next((c['hospital'] for c in cluster_types if c['cluster'] == i), 0) for i in clusters]
    cafe_data = [next((c['cafe'] for c in cluster_types if c['cluster'] == i), 0) for i in clusters]
    park_data = [next((c['park'] for c in cluster_types if c['cluster'] == i), 0) for i in clusters]
    
    labels = [next((c['유형'] for c in cluster_types if c['cluster'] == i), f"클러스터 {i}") for i in clusters]
    x = np.arange(len(labels))
    
    fig, ax = plt.subplots(figsize=(14, 8))
    rects1 = ax.bar(x - bar_width, hospital_data, bar_width, label='동물병원')
    rects2 = ax.bar(x, cafe_data, bar_width, label='애견카페')
    rects3 = ax.bar(x + bar_width, park_data, bar_width, label='공원')
    
    # 행정동 수를 텍스트로 추가
    for i, cluster_id in enumerate(clusters):
        count = cluster_counts.get(cluster_id, 0)
        ax.text(i, 0.5, f"{count}개 동네", ha='center', color='black', fontweight='bold')
    
    ax.set_xlabel('클러스터 유형')
    ax.set_ylabel('평균 시설 수')
    ax.set_title('클러스터별 시설 특성')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'cluster_characteristics.png'))
    plt.close()
    
    print("클러스터 시각화가 완료되었습니다.")

def main():
    """메인 함수"""
    # 경로 설정
    input_filepath = './output/facilities_with_district.csv'
    output_dir = './output'
    
    # 저장소 및 서비스 인스턴스 생성
    repository = FacilityDataRepository()
    clustering_service = ClusteringService()
    
    # 데이터 로드
    df = repository.load_facility_data(input_filepath)
    if df is None:
        print("데이터 로드에 실패했습니다.")
        return

    print(f"총 {len(df)}개의 시설 데이터를 로드했습니다.")
    
    # 행정동별 시설 수 집계
    districts = {}
    for _, row in df.iterrows():
        district_name = row['district']
        facility_type = row['type']
        
        if district_name not in districts:
            districts[district_name] = District(district_name)
        
        districts[district_name].add_facility(facility_type)
    
    print(f"총 {len(districts)}개의 행정동 데이터를 처리했습니다.")
    
    # 클러스터링을 위한 특성 벡터 생성
    district_names = []
    district_features = []
    
    for name, district in districts.items():
        district_names.append(name)
        district_features.append(district.get_features())
    
    # 최적의 클러스터 수 결정
    print("최적의 클러스터 수 탐색 중...")
    n_clusters = clustering_service.find_optimal_clusters(district_features, max_clusters=8)
    print(f"최적의 클러스터 수: {n_clusters}")
    
    # 클러스터링 수행
    result = clustering_service.perform_clustering(district_features, district_names, n_clusters)
    
    # 클러스터 유형 부여
    cluster_types = clustering_service.assign_cluster_types(result['cluster_centers'])
    
    # 행정동별 클러스터 할당 결과 생성
    district_clusters = []
    for i, district in enumerate(district_names):
        district_clusters.append({
            'district': district,
            'cluster': int(result['cluster_labels'][i])
        })
    
    # 클러스터링 결과 저장
    cluster_types, district_clusters = repository.save_cluster_results(
        cluster_types,
        district_clusters,
        output_dir
    )
    
    # 클러스터 시각화
    visualize_clusters(cluster_types, district_clusters, output_dir)
    
    print("클러스터링 완료!")

if __name__ == "__main__":
    main()
