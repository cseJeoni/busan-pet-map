import pandas as pd
import json
import os
import re

def generate_district_ranking_html():
    """행정동별 시설 개수 순위 및 요약 통계 HTML 생성"""
    
    # 행정동별 시설 개수 데이터 로드
    district_counts = pd.read_csv('output/district_facility_counts_all.csv')
    
    # 상위 15개 행정동만 선택
    top_districts = district_counts.sort_values('총합', ascending=False).head(15)
    
    # 강아지 키우기 좋은 동네 점수 계산 (가중치 적용)
    # 동물병원(3) + 애견카페(2) + 공원(1)
    district_counts['점수'] = (
        district_counts['동물병원'] * 3.0 + 
        district_counts['애견카페'] * 2.0 + 
        district_counts['공원'] * 1.0
    )
    
    # 점수 기준으로 상위 15개 행정동 선택
    top_districts = district_counts.sort_values('점수', ascending=False).head(15)
    
    # 시설별 상위 행정동 (각 시설별로 개수 기준 상위 5개)
    top_hospitals = district_counts.sort_values('동물병원', ascending=False).head(5)
    top_cafes = district_counts[district_counts['애견카페'] > 0].sort_values('애견카페', ascending=False).head(5)
    top_parks = district_counts[district_counts['공원'] > 0].sort_values('공원', ascending=False).head(5)
    
    # 순위 테이블 HTML 생성
    rank_table = '''
    <h3>🏆 강아지 키우기 좋은 동네 TOP 10</h3>
    <div class="info-text">
        <p><em>동물병원(2점), 애견카페(1.5점), 공원(1점) 가중치 적용</em></p>
    </div>
    <table class="rank-table">
        <thead>
            <tr>
                <th>순위</th>
                <th>행정동</th>
                <th>점수</th>
                <th>동물병원</th>
                <th>애견카페</th>
                <th>공원</th>
            </tr>
        </thead>
        <tbody>
    '''
    
    for i, (_, row) in enumerate(top_districts.iterrows(), 1):
        rank_table += f'''
            <tr class="{'first-rank' if i == 1 else 'top-rank' if i <= 3 else ''}">
                <td>{i}</td>
                <td>{row['행정동']}</td>
                <td>{row['점수']:.1f}</td>
                <td>{row['동물병원']}</td>
                <td>{row['애견카페']}</td>
                <td>{row['공원']}</td>
            </tr>
        '''
    
    rank_table += '''
        </tbody>
    </table>
    '''
    
    # 요약 통계
    total_hospitals = district_counts['동물병원'].sum()
    total_cafes = district_counts['애견카페'].sum()
    total_parks = district_counts['공원'].sum()
    total_districts = len(district_counts)
    districts_with_hospitals = len(district_counts[district_counts['동물병원'] > 0])
    districts_with_cafes = len(district_counts[district_counts['애견카페'] > 0])
    districts_with_parks = len(district_counts[district_counts['공원'] > 0])
    
    # 동물 인프라가 잘 갖춰진 동네 추천 문구
    recommendation = f'''
    <div class="recommendation">
        <h4>💡 강아지와 함께 하기 좋은 동네는?</h4>
        <p>
            부산 내 <b>{total_districts}</b>개 행정동 중, <b>{districts_with_hospitals}</b>개 동에 동물병원이 있으며,
            <b>{districts_with_cafes}</b>개 동에 애견카페, <b>{districts_with_parks}</b>개 동에 공원이 있습니다.
            부산 전체에는 총 <b>{total_hospitals}개</b>의 동물병원, <b>{total_cafes}개</b>의 애견카페, <b>{total_parks}개</b>의 공원이 있습니다.
        </p>
        <p>
            <b>{top_districts.iloc[0]['행정동']}</b>은(는) 종합 점수 <b>{top_districts.iloc[0]['점수']:.1f}점</b>으로
            부산에서 강아지 키우기 가장 좋은 동네로 평가되었습니다.
            <b>{top_hospitals.iloc[0]['행정동']}</b>은(는) 동물병원이 <b>{top_hospitals.iloc[0]['동물병원']}개</b>로 가장 많고,
            <b>{top_cafes.iloc[0]['행정동']}</b>은(는) 애견카페가 <b>{top_cafes.iloc[0]['애견카페']}개</b>로,
            <b>{top_parks.iloc[0]['행정동']}</b>은(는) 공원이 <b>{top_parks.iloc[0]['공원']}개</b>로 각 시설이 가장 많은 지역입니다.
        </p>
    </div>
    '''
    
    # 시설별 상위 행정동 테이블
    facilities_table = f'''
    <h3>📊 시설별 상위 행정동</h3>
    <div class="facilities-tables">
        <div class="facility-table">
            <h4>🏥 동물병원 TOP 5</h4>
            <table class="rank-table">
                <thead>
                    <tr>
                        <th>순위</th>
                        <th>행정동</th>
                        <th>개수</th>
                    </tr>
                </thead>
                <tbody>
'''

    for i, (_, row) in enumerate(top_hospitals.iterrows(), 1):
        facilities_table += f'''
                    <tr class="{'first-rank' if i == 1 else ''}">
                        <td>{i}</td>
                        <td>{row['행정동']}</td>
                        <td>{row['동물병원']}</td>
                    </tr>
        '''
    
    facilities_table += '''
                </tbody>
            </table>
        </div>
        <div class="facility-table">
            <h4>☕ 애견카페 TOP 5</h4>
            <table class="rank-table">
                <thead>
                    <tr>
                        <th>순위</th>
                        <th>행정동</th>
                        <th>개수</th>
                    </tr>
                </thead>
                <tbody>
'''

    for i, (_, row) in enumerate(top_cafes.iterrows(), 1):
        facilities_table += f'''
                    <tr class="{'first-rank' if i == 1 else ''}">
                        <td>{i}</td>
                        <td>{row['행정동']}</td>
                        <td>{row['애견카페']}</td>
                    </tr>
        '''
    
    facilities_table += '''
                </tbody>
            </table>
        </div>
        <div class="facility-table">
            <h4>🌳 공원 TOP 5</h4>
            <table class="rank-table">
                <thead>
                    <tr>
                        <th>순위</th>
                        <th>행정동</th>
                        <th>개수</th>
                    </tr>
                </thead>
                <tbody>
'''

    for i, (_, row) in enumerate(top_parks.iterrows(), 1):
        facilities_table += f'''
                    <tr class="{'first-rank' if i == 1 else ''}">
                        <td>{i}</td>
                        <td>{row['행정동']}</td>
                        <td>{row['공원']}</td>
                    </tr>
        '''
    
    facilities_table += '''
                </tbody>
            </table>
        </div>
    </div>
    '''
    
    # 사용 가이드 HTML
    usage_guide = '''
    <h3>🗺 지도 사용법</h3>
    <ul class="guide-list">
        <li>
            <b>레이어 선택:</b> 왼쪽 상단의 레이어 컨트롤에서 원하는 정보 레이어를 켜고 끌 수 있습니다.
        </li>
        <li>
            <b>행정동 확인:</b> 행정동 경계에 마우스를 올리면 행정동 이름이 표시됩니다. 
        </li>
        <li>
            <b>시설 정보:</b> 각 마커를 클릭하면 시설명, 주소, 연락처 등 상세 정보가 표시됩니다.
        </li>
        <li>
            <b>지도 확대/축소:</b> 스크롤이나 +/- 버튼으로 확대/축소가 가능합니다.
        </li>
    </ul>
    <div class="legend">
        <h4>범례</h4>
        <div class="legend-item"><span class="marker red"></span> 동물병원</div>
        <div class="legend-item"><span class="marker blue"></span> 애견카페</div>
        <div class="legend-item"><span class="marker green"></span> 공원</div>
    </div>
    '''
    
    # CSS 스타일
    styles = '''
    <style>
        .rank-table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            font-size: 0.9rem;
        }
        .rank-table th, .rank-table td {
            padding: 8px 12px;
            text-align: center;
            border: 1px solid #e0e0e0;
        }
        .rank-table th {
            background-color: #f0f6ff;
            font-weight: bold;
        }
        .rank-table tr:nth-child(even) {
            background-color: #f9f9fb;
        }
        .first-rank {
            background-color: #fff6e6 !important;
            font-weight: bold;
        }
        .top-rank {
            background-color: #f9f9fb;
            font-weight: bold;
        }
        .facilities-tables {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 20px;
        }
        .facility-table {
            flex: 1;
            min-width: 200px;
        }
        .facility-table h4 {
            margin-top: 0;
            color: #334155;
            font-size: 1rem;
        }
        .data-methodology {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            border-left: 4px solid #10b981;
        }
        .data-methodology h3 {
            margin-top: 0;
            color: #10b981;
        }
        .recommendation {
            background-color: #f0f8ff;
            padding: 1rem;
            border-radius: 8px;
            margin-top: 1.5rem;
            border-left: 4px solid #3b82f6;
        }
        .recommendation h4 {
            margin-top: 0;
            color: #2563eb;
        }
        .info-text {
            font-size: 0.8rem;
            color: #666;
            margin: -0.8rem 0 1rem 0;
        }
        .guide-list {
            padding-left: 1.5rem;
        }
        .guide-list li {
            margin-bottom: 0.8rem;
        }
        .legend {
            margin-top: 1.5rem;
            padding: 0.8rem;
            background: #f9f9fb;
            border-radius: 6px;
        }
        .legend h4 {
            margin-top: 0;
            margin-bottom: 0.5rem;
            font-size: 1rem;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin-bottom: 0.4rem;
        }
        .marker {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .red { background-color: red; }
        .blue { background-color: blue; }
        .green { background-color: green; }
        h3 {
            color: #1f2937;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 0.5rem;
            margin-top: 0;
        }
    </style>
    '''
    
    # 데이터 수집 방법 설명
    data_methodology = '''
    <div class="data-methodology">
        <h3>📝 데이터 수집 방법</h3>
        <p>
            본 지도는 카카오맵 API를 활용하여 부산 전체 지역의 동물병원, 애견카페, 공원 데이터를 수집했습니다.
            카카오맵 API는 검색당 최대 45개의 결과만 반환하는 제한이 있어, 이를 극복하기 위해 부산 지역을 
            작은 지역으로 분할하는 재귀적 검색 기법을 적용했습니다.
        </p>
        <p>
            <b>데이터 수집 개선 결과:</b>
            <ul>
                <li>공원: <b>{total_parks}개</b> (기존 45개에서 대폭 증가)</li>
                <li>애견카페: <b>{total_cafes}개</b> (기존 45개에서 증가)</li>
                <li>동물병원: <b>{total_hospitals}개</b> (기존 데이터 활용)</li>
            </ul>
        </p>
    </div>
    '''
    
    return styles + rank_table + recommendation + facilities_table + data_methodology, usage_guide


def update_custom_html():
    """웹페이지 HTML 업데이트"""
    
    dashboard_html, usage_guide = generate_district_ranking_html()
    
    custom_html_path = 'output/vet_hospitals_busan_map_custom.html'
    
    with open(custom_html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 오른쪽 상단 패널 업데이트
    html_content = re.sub(
        r'<div class="right-top">\s*<!-- 상단 섹션: 자유롭게 내용 추가 -->\s*<h3>.*?</h3>\s*<p>.*?</p>\s*</div>',
        f'<div class="right-top">\n{dashboard_html}\n</div>',
        html_content, 
        flags=re.DOTALL
    )
    
    # 오른쪽 하단 패널 업데이트
    html_content = re.sub(
        r'<div class="right-bottom">\s*<!-- 하단 섹션: 자유롭게 내용 추가 -->\s*<h3>.*?</h3>\s*<p>.*?</p>\s*</div>',
        f'<div class="right-bottom">\n{usage_guide}\n</div>',
        html_content,
        flags=re.DOTALL
    )
    
    with open(custom_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"웹 대시보드 업데이트 완료: {custom_html_path}")


if __name__ == "__main__":
    update_custom_html()
