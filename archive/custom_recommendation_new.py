"""
맞춤형 동네 추천 대시보드 생성 스크립트
- 사용자 우선순위 기반 점수 계산 및 시각화
- 가중치 조절 슬라이더 UI 제공
- Chart.js를 사용한 누적 막대그래프 시각화
"""
import pandas as pd
import json
import os
from pathlib import Path

def generate_custom_recommendation_dashboard():
    """
    맞춤형 추천 대시보드 HTML 및 JavaScript 생성
    - 슬라이더로 가중치 조절 가능
    - 실시간 점수 계산 및 차트 업데이트
    - 상위 5개 행정동 순위 표시
    """
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

def update_dashboard_with_recommendation():
    """기존 HTML 파일에 맞춤형 추천 대시보드 추가"""
    try:
        # HTML 파일 경로
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        html_path = output_dir / 'vet_hospitals_busan_map_custom.html'
        
        # 맞춤형 추천 대시보드 HTML 생성
        custom_recommendation_html = generate_custom_recommendation_dashboard()
        
        # 기존 HTML 파일 읽기
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Chart.js 라이브러리 추가 및 맞춤형 추천 대시보드 삽입
        dashboard_div = '<div class="dashboard">'
        chart_js_cdn = '<script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>'
        
        # HTML <head> 태그에 Chart.js 라이브러리 추가
        html_content = html_content.replace('</head>', f'{chart_js_cdn}\n</head>')
        
        # 대시보드 영역에 맞춤형 추천 대시보드 추가
        if dashboard_div in html_content:
            html_content = html_content.replace(
                dashboard_div,
                f'{dashboard_div}\n{custom_recommendation_html}'
            )
        
        # 수정된 HTML 파일 저장
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"맞춤형 추천 대시보드가 추가되었습니다: {html_path}")
        return True
    
    except Exception as e:
        print(f"맞춤형 추천 대시보드 추가 중 오류 발생: {e}")
        return False

if __name__ == "__main__":
    update_dashboard_with_recommendation()
