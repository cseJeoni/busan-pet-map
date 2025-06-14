#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTML 파일에 클러스터링 정보를 추가하는 스크립트
"""

import json
import os
from bs4 import BeautifulSoup

def load_clustering_data():
    """클러스터링 데이터 로드"""
    # 클러스터 정보 로드
    with open('./cluster_info.json', 'r', encoding='utf-8') as f:
        cluster_info = json.load(f)
    
    # 행정동별 클러스터 할당 로드
    with open('./district_clusters.json', 'r', encoding='utf-8') as f:
        district_clusters = json.load(f)
    
    return cluster_info, district_clusters

def generate_clustering_html(cluster_info, district_clusters):
    """클러스터링 HTML 섹션 생성"""
    
    # 클러스터별 행정동 그룹화
    cluster_districts = {}
    for district_data in district_clusters:
        cluster_id = district_data['cluster']
        district_name = district_data['district']
        
        if cluster_id not in cluster_districts:
            cluster_districts[cluster_id] = []
        cluster_districts[cluster_id].append(district_name)
    
    html_content = '''
    <!-- 클러스터링 분석 섹션 -->
    <h3>🔬 클러스터링 분석</h3>
    <div class="clustering-section">
        <div class="clustering-info">
            <p>부산시 행정동을 반려견 시설 특성에 따라 5개 클러스터로 분류했습니다.</p>
        </div>
        
        <div class="cluster-groups">
'''

    # 각 클러스터별 HTML 생성
    for cluster in cluster_info:
        cluster_id = cluster['cluster']
        cluster_type = cluster['유형']
        cluster_color = cluster['색상']
        hospital_count = cluster['hospital']
        cafe_count = cluster['cafe']
        park_count = cluster['park']
        district_count = cluster['동네_수']
        
        # 해당 클러스터의 행정동들
        districts = cluster_districts.get(cluster_id, [])
        
        # 아이콘 설정
        if '종합' in cluster_type:
            icon = '🏢'
        elif '의료' in cluster_type:
            icon = '🏥'
        elif '여가' in cluster_type:
            icon = '🌳'
        elif '카페' in cluster_type:
            icon = '☕'
        else:
            icon = '🏘️'
        
        html_content += f'''
            <div class="cluster-group" style="border-left: 4px solid {cluster_color};">
                <div class="cluster-header">
                    <h4 style="color: {cluster_color};">{icon} {cluster_type} ({district_count}개 동네)</h4>
                    <p class="cluster-desc">{get_cluster_description(cluster_type)}</p>
                </div>
                <div class="cluster-stats">
                    <span class="stat-item">🏥 동물병원: {hospital_count:.1f}개</span>
                    <span class="stat-item">☕ 애견카페: {cafe_count:.1f}개</span>
                    <span class="stat-item">🌳 공원: {park_count:.1f}개</span>
                </div>
                <div class="cluster-districts">
'''
        
        # 행정동 태그 추가 (최대 8개까지 표시)
        display_districts = districts[:8]
        for district in display_districts:
            html_content += f'                    <span class="district-tag">{district}</span>\n'
        
        # 나머지 행정동이 있으면 "외 N개 동네" 표시
        if len(districts) > 8:
            remaining = len(districts) - 8
            html_content += f'                    <span class="district-tag-more">외 {remaining}개 동네</span>\n'
        
        html_content += '''                </div>
            </div>
'''

    html_content += '''        </div>
    </div>

    <style>
        .clustering-section {
            margin: 2rem 0;
            padding: 1.5rem;
            background: #f8f9fa;
            border-radius: 10px;
        }
        
        .clustering-info {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .clustering-info p {
            font-size: 1.1rem;
            color: #495057;
            margin: 0;
        }
        
        .cluster-groups {
            display: grid;
            gap: 1.5rem;
        }
        
        .cluster-group {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s ease;
        }
        
        .cluster-group:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .cluster-header h4 {
            margin: 0 0 0.5rem 0;
            font-size: 1.2rem;
            font-weight: 600;
        }
        
        .cluster-desc {
            color: #6c757d;
            margin: 0 0 1rem 0;
            font-size: 0.9rem;
        }
        
        .cluster-stats {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }
        
        .stat-item {
            background: #e9ecef;
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-size: 0.85rem;
            font-weight: 500;
        }
        
        .cluster-districts {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        
        .district-tag {
            background: #f1f3f4;
            color: #495057;
            padding: 0.25rem 0.6rem;
            border-radius: 12px;
            font-size: 0.8rem;
            border: 1px solid #dee2e6;
        }
        
        .district-tag-more {
            background: #007bff;
            color: white;
            padding: 0.25rem 0.6rem;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        
        @media (max-width: 768px) {
            .cluster-stats {
                flex-direction: column;
                gap: 0.5rem;
            }
            
            .stat-item {
                text-align: center;
            }
        }
    </style>
'''
    
    return html_content

def get_cluster_description(cluster_type):
    """클러스터 유형별 설명 반환"""
    descriptions = {
        '종합 인프라형': '동물병원, 애견카페, 공원이 모두 잘 갖춰진 지역',
        '의료 중심형': '동물병원이 많이 집중된 지역',
        '여가 중심형': '공원이 많아 산책하기 좋은 지역',
        '카페 문화형': '애견카페가 발달한 문화적 지역',
        '기본 인프라형': '기본적인 시설만 갖춘 일반 주거지역'
    }
    return descriptions.get(cluster_type, '특별한 특성을 가진 지역')

def add_clustering_to_html():
    """HTML 파일에 클러스터링 정보 추가"""
    
    # 클러스터링 데이터 로드
    cluster_info, district_clusters = load_clustering_data()
    
    # HTML 파일 읽기
    html_file_path = './output/vet_hospitals_busan_map_custom.html'
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # BeautifulSoup로 HTML 파싱
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 시설별 상위 행정동 섹션 찾기
    facilities_section = soup.find('h3', string='📊 시설별 상위 행정동')
    
    if facilities_section:
        # 상위 행정동 섹션의 부모를 찾아서 그 다음에 클러스터링 섹션 추가
        parent = facilities_section.parent
        
        # 클러스터링 HTML 생성
        clustering_html = generate_clustering_html(cluster_info, district_clusters)
        
        # 클러스터링 섹션을 삽입할 위치 찾기 (facilities-tables div 다음)
        facilities_tables = soup.find('div', class_='facilities-tables')
        if facilities_tables:
            # 클러스터링 HTML을 BeautifulSoup 객체로 변환
            clustering_soup = BeautifulSoup(clustering_html, 'html.parser')
            
            # facilities-tables div 다음에 클러스터링 섹션 추가
            for element in clustering_soup.contents:
                if element.name:  # 텍스트 노드가 아닌 경우에만
                    facilities_tables.insert_after(element)
                    facilities_tables = element  # 다음 요소를 삽입할 위치 업데이트
    
    # 새로운 HTML 파일 저장
    output_file_path = './output/vet_hospitals_busan_map_with_clustering.html'
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    print(f"클러스터링 정보가 추가된 HTML 파일이 생성되었습니다: {output_file_path}")

if __name__ == "__main__":
    add_clustering_to_html()
