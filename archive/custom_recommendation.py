"""맞춤형 동네 추천 대시보드 생성 스크립트
- 사용자 우선순위 기반 점수 계산
- Chart.js를 활용한 누적 막대그래프 시각화
- 슬라이더 기반 사용자 인터페이스
- 사용자 우선순위 기반 점수 계산
- 누적 막대그래프 시각화 (Chart.js 활용)
"""
import pandas as pd
import json
import os
from pathlib import Path

def generate_custom_recommendation_dashboard():
    """
    맞춤형 추천 대시보드 HTML 생성
    - 사용자 가중치 조절 슬라이더
    - Chart.js 기반 누적 막대그래프
    - 실시간 순위 업데이트
    """
    # 행정동별 시설 개수 데이터 로드
    district_counts = pd.read_csv('output/district_facility_counts_all.csv')
    
    # Chart.js 라이브러리를 위한 데이터 준비
    # 초기 가중치: 동물병원 5, 애견카페 5, 공원 5로 설정
    initial_weights = {
        '동물병원': 5,
        '애견카페': 5,
        '공원': 5
    }
    
    # 초기 가중치로 점수 계산
    district_counts['점수'] = (
        district_counts['동물병원'] * initial_weights['동물병원'] +
        district_counts['애견카페'] * initial_weights['애견카페'] +
        district_counts['공원'] * initial_weights['공원']
    )
    
    # 상위 5개 행정동 선택
    top_districts = district_counts.sort_values('점수', ascending=False).head(5)
    
    # Chart.js 데이터 포맷 생성
    chart_labels = top_districts['행정동'].tolist()
    hospital_data = top_districts['동물병원'].tolist()
    cafe_data = top_districts['애견카페'].tolist()
    park_data = top_districts['공원'].tolist()
    
    # 모든 행정동 데이터를 JavaScript에 전달하기 위한 JSON 생성
    all_districts = []
    for _, row in district_counts.iterrows():
        all_districts.append({
            '행정동': row['행정동'],
            '동물병원': int(row['동물병원']),
            '애견카페': int(row['애견카페']),
            '공원': int(row['공원'])
        })
    
    # 외부 JavaScript 파일 읽기
    try:
        with open('custom_recommendation.js', 'r', encoding='utf-8') as js_file:
            custom_js_code = js_file.read()
    except Exception as e:
        print(f"JavaScript 파일 로드 오류: {e}")
        custom_js_code = '// JavaScript 파일을 로드하는 데 실패했습니다.'
        
    # HTML 템플릿 생성
    html = f"""
    <div class="custom-recommendation">
        <h3>🎯 맞춤형 동네 추천</h3>
        <p>각 시설의 중요도를 조절하여 나만의 맞춤 추천을 받아보세요.</p>
        
        <div class="weight-sliders">
            <div class="slider-container">
                <label>🏥 동물병원 중요도: <span id="hospital-weight-value">5</span></label>
                <input type="range" id="hospital-weight" min="0" max="10" value="5" class="weight-slider">
            </div>
            
            <div class="slider-container">
                <label>☕ 애견카페 중요도: <span id="cafe-weight-value">5</span></label>
                <input type="range" id="cafe-weight" min="0" max="10" value="5" class="weight-slider">
            </div>
            
            <div class="slider-container">
                <label>🌳 공원 중요도: <span id="park-weight-value">5</span></label>
                <input type="range" id="park-weight" min="0" max="10" value="5" class="weight-slider">
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
    </div>

    <style>
        .custom-recommendation {
            background-color: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .weight-sliders {
            margin: 20px 0;
        }
        
        .slider-container {
            margin-bottom: 15px;
        }
        
        .weight-slider {
            width: 100%;
            height: 8px;
            -webkit-appearance: none;
            background: #f0f0f0;
            outline: none;
            border-radius: 5px;
        }
        
        .weight-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #4285f4;
            cursor: pointer;
        }
        
        .chart-container {
            margin: 20px 0;
            height: 300px;
        }
        
        .ranking-container {
            margin-top: 20px;
        }
        
        #ranking-list li {
            margin-bottom: 5px;
            padding: 8px;
            border-radius: 4px;
        }
        
        #ranking-list li:nth-child(1) {
            background-color: #fff6e6;
            font-weight: bold;
        }
        
        #ranking-list li:nth-child(2), #ranking-list li:nth-child(3) {
            background-color: #f9f9fb;
        }
    </style>

    <script>
        // Chart.js 로드 (CDN으로 페이지에 이미 포함되어 있다고 가정)
        document.addEventListener('DOMContentLoaded', function() {
            // 모든 행정동 데이터
            const allDistricts = {json.dumps(all_districts)};
            
            // 초기 차트 생성
            const ctx = document.getElementById('recommendation-chart').getContext('2d');
            let recommendationChart = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(chart_labels)},
                    datasets: [
                        {{
                            label: '동물병원',
                            data: {json.dumps(hospital_data)}.map(v => v * 5), // 초기 가중치 5 적용
                            backgroundColor: 'rgba(255, 99, 132, 0.7)',
                            borderColor: 'rgba(255, 99, 132, 1)',
                            borderWidth: 1
                        }},
                        {{
                            label: '애견카페',
                            data: {json.dumps(cafe_data)}.map(v => v * 5), // 초기 가중치 5 적용
                            backgroundColor: 'rgba(54, 162, 235, 0.7)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1
                        }},
                        {{
                            label: '공원',
                            data: {json.dumps(park_data)}.map(v => v * 5), // 초기 가중치 5 적용
                            backgroundColor: 'rgba(75, 192, 192, 0.7)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1
                        }}
                    ]
                }},
                options: {
                    plugins: {
                        title: {
                            display: true,
                            text: '행정동별 시설 점수 (가중치 적용)'
                        },
                    },
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            stacked: true,
                        },
                        y: {
                            stacked: true,
                            title: {
                                display: true,
                                text: '가중치 적용 점수'
                            }
                        }
                    }
                }
            });
            
            // 순위 리스트 업데이트 함수
            function updateRankingList(topDistricts) {
                const rankingList = document.getElementById('ranking-list');
                rankingList.innerHTML = '';
                
                topDistricts.forEach((district, index) => {
                    const listItem = document.createElement('li');
                    const totalScore = district.score.toFixed(1);
                    
                    listItem.innerHTML = `
                        <strong>${district.name}</strong>: ${totalScore}점
                        <div><small>동물병원: ${district.hospital}개, 애견카페: ${district.cafe}개, 공원: ${district.park}개</small></div>
                    `;
                    
                    rankingList.appendChild(listItem);
                });
            }
            
            // 슬라이더 값 변경 시 차트 업데이트 함수
            function updateChart() {
                // 현재 슬라이더 값 가져오기
                const hospitalWeight = parseFloat(document.getElementById('hospital-weight').value);
                const cafeWeight = parseFloat(document.getElementById('cafe-weight').value);
                const parkWeight = parseFloat(document.getElementById('park-weight').value);
                
                // 슬라이더 값 표시 업데이트
                document.getElementById('hospital-weight-value').textContent = hospitalWeight;
                document.getElementById('cafe-weight-value').textContent = cafeWeight;
                document.getElementById('park-weight-value').textContent = parkWeight;
                
                // 모든 행정동에 가중치 적용하여 점수 계산
                const scoredDistricts = allDistricts.map(district => {
                    const score = 
                        district['동물병원'] * hospitalWeight +
                        district['애견카페'] * cafeWeight +
                        district['공원'] * parkWeight;
                    
                    return {
                        name: district['행정동'],
                        score: score,
                        hospital: district['동물병원'],
                        cafe: district['애견카페'],
                        park: district['공원'],
                        hospitalScore: district['동물병원'] * hospitalWeight,
                        cafeScore: district['애견카페'] * cafeWeight,
                        parkScore: district['공원'] * parkWeight
                    };
                });
                
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
            }
            
            // 초기 순위 리스트 생성
            updateChart();
            
            // 슬라이더 이벤트 리스너 추가
            document.getElementById('hospital-weight').addEventListener('input', updateChart);
            document.getElementById('cafe-weight').addEventListener('input', updateChart);
            document.getElementById('park-weight').addEventListener('input', updateChart);
        });
    </script>
    """
    
    return html

def update_dashboard_with_recommendation():
    """기존 HTML 파일에 맞춤형 추천 대시보드 추가"""
    try:
        # HTML 파일 경로
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        html = f"""output_dir / 'vet_hospitals_busan_map_custom.html'
        
        # 맞춤형 추천 대시보드 HTML 생성
        custom_recommendation_html = generate_custom_recommendation_dashboard()
        
        # 기존 HTML 파일 읽기
        with open(html, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Chart.js 라이브러리 추가 및 맞춤형 추천 대시보드 삽입
        # 기존 대시보드 영역을 찾아서 맨 앞에 맞춤형 추천 추가
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
