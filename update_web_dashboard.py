import pandas as pd
import json
import os
import re
from pathlib import Path

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


def generate_custom_recommendation_dashboard():
    """맞춤형 추천 대시보드 HTML 및 JavaScript 생성"""
    # 행정동별 시설 개수 데이터 로드
    district_counts = pd.read_csv('output/district_facility_counts_all.csv')
    
    # 총 시설 개수 계산
    total_hospitals = district_counts['동물병원'].sum()
    total_cafes = district_counts['애견카페'].sum()
    total_parks = district_counts['공원'].sum()
    
    # 모든 행정동 데이터를 JavaScript에 전달하기 위한 JSON 생성
    all_districts = []
    for _, row in district_counts.iterrows():
        all_districts.append({
            '행정동': row['행정동'],
            '동물병원': int(row['동물병원']),
            '애견카페': int(row['애견카페']),
            '공원': int(row['공원'])
        })
    
    # JavaScript 데이터 변수 선언
    js_data = f"const allDistrictsData = {json.dumps(all_districts, ensure_ascii=False)};"
    
    # HTML 생성
    html = f"""
    <div class="custom-recommendation">
        <h3>🎯 맞춤형 동네 추천</h3>
        <p>각 시설의 중요도를 조절하여 나에게 맞는 동네를 찾아보세요.</p>
        
        <div class="weight-sliders">
            <div class="slider-container">
                <label>🏥 동물병원 중요도: <span id="hospital-weight-value">5</span></label>
                <input type="range" id="hospital-weight" min="0" max="10" value="5" step="0.5" class="weight-slider">
            </div>
            
            <div class="slider-container">
                <label>☕ 애견카페 중요도: <span id="cafe-weight-value">5</span></label>
                <input type="range" id="cafe-weight" min="0" max="10" value="5" step="0.5" class="weight-slider">
            </div>
            
            <div class="slider-container">
                <label>🌳 공원 중요도: <span id="park-weight-value">5</span></label>
                <input type="range" id="park-weight" min="0" max="10" value="5" step="0.5" class="weight-slider">
            </div>
        </div>
        
        <div class="chart-container">
            <canvas id="recommendation-chart"></canvas>
        </div>
        
        <div class="ranking-container">
            <h4>맞춤 추천 순위</h4>
            <ol id="ranking-list">
                <!-- 순위는 JavaScript로 동적 생성 -->
            </ol>
        </div>
        
        <div class="explanation">
            <small>※ 각 시설 점수는 (시설 수) × (중요도)로 계산되며, 점수가 높은 행정동이 우선적으로 추천됩니다.</small>
            <small>※ 부산 전체에는 동물병원 {total_hospitals}개, 애견카페 {total_cafes}개, 공원 {total_parks}개가 있습니다.</small>
        </div>
    </div>

    <style>
        .custom-recommendation {{
            background-color: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        
        .weight-sliders {{
            margin: 20px 0;
        }}
        
        .slider-container {{
            margin-bottom: 15px;
        }}
        
        .weight-slider {{
            width: 100%;
            height: 8px;
            -webkit-appearance: none;
            background: #f0f0f0;
            outline: none;
            border-radius: 5px;
        }}
        
        .weight-slider::-webkit-slider-thumb {{
            -webkit-appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #4285f4;
            cursor: pointer;
        }}
        
        .chart-container {{
            margin: 20px 0;
            height: 300px;
            position: relative;
        }}
        
        .ranking-container {{
            margin-top: 20px;
        }}
        
        #ranking-list li {{
            margin-bottom: 5px;
            padding: 8px;
            border-radius: 4px;
        }}
        
        #ranking-list li:nth-child(1) {{
            background-color: #fff6e6;
            font-weight: bold;
        }}
        
        #ranking-list li:nth-child(2), #ranking-list li:nth-child(3) {{
            background-color: #f9f9fb;
        }}
        
        .explanation {{
            margin-top: 15px;
            color: #666;
            font-size: 0.9em;
        }}
        
        .explanation small {{
            display: block;
            margin-bottom: 5px;
        }}
    </style>

    <script>
        // 모든 행정동 데이터
        {js_data}
        
        document.addEventListener('DOMContentLoaded', function() {{
            // 초기 차트 생성
            const ctx = document.getElementById('recommendation-chart').getContext('2d');
            let recommendationChart = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: [],
                    datasets: [
                        {{
                            label: '동물병원',
                            backgroundColor: 'rgba(255, 99, 132, 0.7)',
                            borderColor: 'rgba(255, 99, 132, 1)',
                            borderWidth: 1,
                            data: []
                        }},
                        {{
                            label: '애견카페',
                            backgroundColor: 'rgba(54, 162, 235, 0.7)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1,
                            data: []
                        }},
                        {{
                            label: '공원',
                            backgroundColor: 'rgba(75, 192, 192, 0.7)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1,
                            data: []
                        }}
                    ]
                }},
                options: {{
                    plugins: {{
                        title: {{
                            display: true,
                            text: '행정동별 시설 점수 (가중치 적용)',
                            font: {{
                                size: 16
                            }}
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const index = context.datasetIndex;
                                    const value = context.raw.toFixed(1);
                                    let label = context.dataset.label || '';
                                    
                                    if (label) {{
                                        label += ': ';
                                    }}
                                    
                                    if (index === 0) {{
                                        return `${{label}}${{value}}점 (${{rawData[context.dataIndex].hospital}}개)`;
                                    }} else if (index === 1) {{
                                        return `${{label}}${{value}}점 (${{rawData[context.dataIndex].cafe}}개)`;
                                    }} else if (index === 2) {{
                                        return `${{label}}${{value}}점 (${{rawData[context.dataIndex].park}}개)`;
                                    }}
                                    
                                    return `${{label}}${{value}}`;
                                }}
                            }}
                        }}
                    }},
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        x: {{
                            stacked: true,
                        }},
                        y: {{
                            stacked: true,
                            title: {{
                                display: true,
                                text: '가중치 적용 점수'
                            }}
                        }}
                    }}
                }}
            }});
            
            let rawData = []; // 차트에 표시된 데이터의 원본 정보 저장
            
            // 순위 리스트 업데이트 함수
            function updateRankingList(topDistricts) {{
                const rankingList = document.getElementById('ranking-list');
                rankingList.innerHTML = '';
                
                topDistricts.forEach((district, index) => {{
                    const listItem = document.createElement('li');
                    const totalScore = district.score.toFixed(1);
                    
                    listItem.innerHTML = `
                        <strong>${{district.name}}</strong>: ${{totalScore}}점
                        <div><small>동물병원: ${{district.hospital}}개, 애견카페: ${{district.cafe}}개, 공원: ${{district.park}}개</small></div>
                    `;
                    
                    rankingList.appendChild(listItem);
                }});
                
                // rawData 업데이트 (툴팁에서 사용)
                rawData = topDistricts;
            }}
            
            // 슬라이더 값 변경 시 차트 업데이트 함수
            function updateChart() {{
                // 현재 슬라이더 값 가져오기
                const hospitalWeight = parseFloat(document.getElementById('hospital-weight').value);
                const cafeWeight = parseFloat(document.getElementById('cafe-weight').value);
                const parkWeight = parseFloat(document.getElementById('park-weight').value);
                
                // 슬라이더 값 표시 업데이트
                document.getElementById('hospital-weight-value').textContent = hospitalWeight;
                document.getElementById('cafe-weight-value').textContent = cafeWeight;
                document.getElementById('park-weight-value').textContent = parkWeight;
                
                // 모든 행정동에 가중치 적용하여 점수 계산
                const scoredDistricts = allDistrictsData.map(district => {{
                    const hospitalScore = district['동물병원'] * hospitalWeight;
                    const cafeScore = district['애견카페'] * cafeWeight;
                    const parkScore = district['공원'] * parkWeight;
                    const totalScore = hospitalScore + cafeScore + parkScore;
                    
                    return {{
                        name: district['행정동'],
                        score: totalScore,
                        hospital: district['동물병원'],
                        cafe: district['애견카페'],
                        park: district['공원'],
                        hospitalScore: hospitalScore,
                        cafeScore: cafeScore,
                        parkScore: parkScore
                    }};
                }});
                
                // 점수 기준 상위 5개 행정동 선택
                const topDistricts = scoredDistricts
                    .sort((a, b) => b.score - a.score)
                    .slice(0, 5);
                
                // 차트 데이터 업데이트
                recommendationChart.data.labels = topDistricts.map(d => d.name);
                recommendationChart.data.datasets[0].data = topDistricts.map(d => d.hospitalScore);
                recommendationChart.data.datasets[1].data = topDistricts.map(d => d.cafeScore);
                recommendationChart.data.datasets[2].data = topDistricts.map(d => d.parkScore);
                recommendationChart.update();
                
                // 순위 리스트 업데이트
                updateRankingList(topDistricts);
            }}
            
            // 초기 차트 및 순위 리스트 생성
            updateChart();
            
            // 슬라이더 이벤트 리스너 추가
            document.getElementById('hospital-weight').addEventListener('input', updateChart);
            document.getElementById('cafe-weight').addEventListener('input', updateChart);
            document.getElementById('park-weight').addEventListener('input', updateChart);
        }});
    </script>
    """
    
    return html


def update_custom_html():
    """웹페이지 HTML 업데이트"""
    
    dashboard_html, usage_guide = generate_district_ranking_html()
    custom_recommendation_html = generate_custom_recommendation_dashboard()
    
    custom_html_path = 'output/vet_hospitals_busan_map_custom.html'
    
    with open(custom_html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Chart.js 라이브러리 추가
    chart_js_cdn = '<script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>'
    
    # HTML <head> 태그에 Chart.js 라이브러리 추가
    html_content = html_content.replace('</head>', f'{chart_js_cdn}\n</head>')
    
    # 오른쪽 상단 패널에 맞춤형 추천 대시보드 추가
    html_content = re.sub(
        r'<div class="right-top">.*?</div>',
        f'<div class="right-top">\n{custom_recommendation_html}\n</div>',
        html_content, 
        flags=re.DOTALL
    )
    
    # 오른쪽 하단 패널에 기존 대시보드 및 사용 가이드 추가
    html_content = re.sub(
        r'<div class="right-bottom">.*?</div>',
        f'<div class="right-bottom">\n{dashboard_html}\n{usage_guide}\n</div>',
        html_content,
        flags=re.DOTALL
    )
    
    with open(custom_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"웹 대시보드 업데이트 완료: {custom_html_path}")


if __name__ == "__main__":
    update_custom_html()
