// 맞춤형 동네 추천 기능을 위한 JavaScript 코드
document.addEventListener('DOMContentLoaded', function() {
    // 모든 행정동 데이터는 allDistrictsData 변수로 HTML에 삽입됨
    
    // 초기 차트 생성
    const ctx = document.getElementById('recommendation-chart').getContext('2d');
    let recommendationChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [], // 초기에는 빈 배열, 나중에 updateChart에서 채워짐
            datasets: [
                {
                    label: '동물병원',
                    backgroundColor: 'rgba(255, 99, 132, 0.7)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                },
                {
                    label: '애견카페',
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                },
                {
                    label: '공원',
                    backgroundColor: 'rgba(75, 192, 192, 0.7)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: '행정동별 시설 점수 (가중치 적용)',
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const index = context.datasetIndex;
                            const value = context.raw.toFixed(1);
                            let label = context.dataset.label || '';
                            
                            if (label) {
                                label += ': ';
                            }
                            
                            if (index === 0) {
                                return `${label}${value}점 (${rawData[context.dataIndex].hospital}개)`;
                            } else if (index === 1) {
                                return `${label}${value}점 (${rawData[context.dataIndex].cafe}개)`;
                            } else if (index === 2) {
                                return `${label}${value}점 (${rawData[context.dataIndex].park}개)`;
                            }
                            
                            return `${label}${value}`;
                        }
                    }
                }
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
    
    let rawData = []; // 차트에 표시된 데이터의 원본 정보 저장
    
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
        
        // rawData 업데이트 (툴팁에서 사용)
        rawData = topDistricts;
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
        const scoredDistricts = allDistrictsData.map(district => {
            const hospitalScore = district['동물병원'] * hospitalWeight;
            const cafeScore = district['애견카페'] * cafeWeight;
            const parkScore = district['공원'] * parkWeight;
            const totalScore = hospitalScore + cafeScore + parkScore;
            
            return {
                name: district['행정동'],
                score: totalScore,
                hospital: district['동물병원'],
                cafe: district['애견카페'],
                park: district['공원'],
                hospitalScore: hospitalScore,
                cafeScore: cafeScore,
                parkScore: parkScore
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
    
    // 초기 차트 및 순위 리스트 생성
    updateChart();
    
    // 슬라이더 이벤트 리스너 추가
    document.getElementById('hospital-weight').addEventListener('input', updateChart);
    document.getElementById('cafe-weight').addEventListener('input', updateChart);
    document.getElementById('park-weight').addEventListener('input', updateChart);
});
