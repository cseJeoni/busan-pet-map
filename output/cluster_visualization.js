// 클러스터 시각화 및 토글 기능을 위한 스크립트
let districtClusters = []; // 행정동별 클러스터 정보
let clusterInfo = [];      // 클러스터 유형 정보
let showClusters = false;  // 클러스터 표시 여부
let geoJsonLayer = null;   // 지도에 표시되는 GeoJSON 레이어
let legend = null;         // 범례 컨트롤

// 클러스터 데이터 로드
function loadClusterData() {
    // 클러스터 설정 로드
    fetch('./district_clusters.json')
        .then(response => response.json())
        .then(data => {
            districtClusters = data;
            console.log('행정동별 클러스터 정보 로드 완료:', districtClusters.length);
            
            // 클러스터 정보 로드
            fetch('./cluster_info.json')
                .then(response => response.json())
                .then(data => {
                    clusterInfo = data;
                    console.log('클러스터 정보 로드 완료:', clusterInfo);
                    
                    // 컨트롤 추가
                    addClusterControls();
                })
                .catch(error => console.error('클러스터 정보 로드 실패:', error));
        })
        .catch(error => console.error('행정동별 클러스터 정보 로드 실패:', error));
}

// 클러스터 토글 컨트롤 추가
function addClusterControls() {
    // 이미 맵이 초기화되어 있는지 확인 
    if (!map_718005d04db2f7b490d1b6e073270da7) {
        console.error('지도가 초기화되지 않았습니다.');
        return;
    }
    
    // 토글 컨트롤 생성
    const ClusterToggleControl = L.Control.extend({
        options: {
            position: 'topright'
        },
        
        onAdd: function() {
            const container = L.DomUtil.create('div', 'custom-control cluster-toggle');
            container.style.backgroundColor = 'white';
            container.style.padding = '6px 10px';
            container.style.border = '2px solid rgba(0,0,0,0.2)';
            container.style.borderRadius = '4px';
            container.style.cursor = 'pointer';
            container.innerHTML = '클러스터 시각화 토글';
            
            // 클릭 이벤트
            L.DomEvent.on(container, 'click', function(e) {
                L.DomEvent.stopPropagation(e);
                
                showClusters = !showClusters;
                if (showClusters) {
                    container.style.backgroundColor = '#f4f4f4';
                    container.style.fontWeight = 'bold';
                    applyClusterColors();
                    showLegend();
                } else {
                    container.style.backgroundColor = 'white';
                    container.style.fontWeight = 'normal';
                    resetColors();
                    hideLegend();
                }
            });
            
            return container;
        }
    });
    
    // 토글 컨트롤 추가
    map_718005d04db2f7b490d1b6e073270da7.addControl(new ClusterToggleControl());
    
    // 범례 생성
    createLegend();
}

// 범례 생성
function createLegend() {
    legend = L.control({position: 'bottomright'});
    
    legend.onAdd = function() {
        const div = L.DomUtil.create('div', 'info legend');
        div.style.backgroundColor = 'white';
        div.style.padding = '6px 8px';
        div.style.border = '1px solid #aaa';
        div.style.borderRadius = '5px';
        div.style.display = 'none'; // 기본적으로 숨김
        return div;
    };
    
    legend.addTo(map_718005d04db2f7b490d1b6e073270da7);
    updateLegendContent();
}

// 범례 콘텐츠 업데이트
function updateLegendContent() {
    const legendDiv = document.querySelector('.legend');
    if (!legendDiv || clusterInfo.length === 0) return;
    
    let html = '<h4 style="margin:0 0 5px;color:#777">클러스터 유형</h4>';
    clusterInfo.forEach(cluster => {
        html += `
            <div style="margin-bottom:3px">
                <i style="width:18px;height:18px;float:left;margin-right:8px;opacity:0.7;background:${cluster.색상}"></i>
                <span>${cluster.유형}</span>
            </div>
        `;
    });
    
    legendDiv.innerHTML = html;
}

// 범례 표시
function showLegend() {
    const legendDiv = document.querySelector('.legend');
    if (legendDiv) {
        legendDiv.style.display = 'block';
    }
}

// 범례 숨기기
function hideLegend() {
    const legendDiv = document.querySelector('.legend');
    if (legendDiv) {
        legendDiv.style.display = 'none';
    }
}

// 클러스터 색상 적용
function applyClusterColors() {
    // GeoJSON 레이어 접근 
    if (!geo_json_f53b76cc8e581e006d61501b949050d0) {
        console.error('GeoJSON 레이어를 찾을 수 없습니다.');
        return;
    }
    
    geo_json_f53b76cc8e581e006d61501b949050d0.eachLayer(function(layer) {
        const districtName = layer.feature.properties.EMD_KOR_NM;
        const clusterData = districtClusters.find(d => d.district === districtName);
        
        if (clusterData) {
            const clusterDetail = clusterInfo.find(c => c.cluster === clusterData.cluster);
            
            if (clusterDetail) {
                layer.setStyle({
                    fillColor: clusterDetail.색상,
                    weight: 1,
                    opacity: 1,
                    color: 'white',
                    dashArray: '3',
                    fillOpacity: 0.7
                });
            }
        }
    });
}

// 원래 색상으로 복원
function resetColors() {
    if (!geo_json_f53b76cc8e581e006d61501b949050d0) return;
    
    geo_json_f53b76cc8e581e006d61501b949050d0.eachLayer(function(layer) {
        layer.setStyle({
            fillColor: '#3388ff',
            weight: 1,
            opacity: 1,
            color: 'white',
            dashArray: '3',
            fillOpacity: 0.7
        });
    });
}

// 팝업 내용 강화 - 클러스터 정보 포함
function enhancePopupContent(feature) {
    const districtName = feature.properties.EMD_KOR_NM;
    const clusterData = districtClusters.find(d => d.district === districtName);
    
    let content = `<div><strong>행정동:</strong> ${districtName}</div>`;
    
    if (clusterData) {
        const clusterDetail = clusterInfo.find(c => c.cluster === clusterData.cluster);
        if (clusterDetail) {
            content += `<div><strong>클러스터 유형:</strong> ${clusterDetail.유형}</div>`;
            content += `<div>
                <strong>시설 현황:</strong> 
                동물병원 ${clusterDetail.hospital}개, 
                애견카페 ${clusterDetail.cafe}개, 
                공원 ${clusterDetail.park}개
            </div>`;
        }
    }
    
    return content;
}

// 레이어에 이벤트 추가
function addLayerEvents() {
    if (!geo_json_f53b76cc8e581e006d61501b949050d0) return;
    
    geo_json_f53b76cc8e581e006d61501b949050d0.eachLayer(function(layer) {
        // 마우스오버 이벤트
        layer.on('mouseover', function(e) {
            this.setStyle({
                weight: 3,
                dashArray: '',
                fillOpacity: 0.9
            });
            
            if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
                this.bringToFront();
            }
        });
        
        // 마우스아웃 이벤트
        layer.on('mouseout', function(e) {
            if (showClusters) {
                const districtName = this.feature.properties.EMD_KOR_NM;
                const clusterData = districtClusters.find(d => d.district === districtName);
                
                if (clusterData) {
                    const clusterDetail = clusterInfo.find(c => c.cluster === clusterData.cluster);
                    if (clusterDetail) {
                        this.setStyle({
                            fillColor: clusterDetail.색상,
                            weight: 1,
                            opacity: 1,
                            color: 'white',
                            dashArray: '3',
                            fillOpacity: 0.7
                        });
                    } else {
                        geo_json_f53b76cc8e581e006d61501b949050d0.resetStyle(this);
                    }
                } else {
                    geo_json_f53b76cc8e581e006d61501b949050d0.resetStyle(this);
                }
            } else {
                geo_json_f53b76cc8e581e006d61501b949050d0.resetStyle(this);
            }
        });
        
        // 클릭 이벤트 - 팝업 내용 강화
        layer.on('click', function(e) {
            const content = enhancePopupContent(this.feature);
            this.bindPopup(content).openPopup();
        });
    });
}

// 지도가 로드된 후 초기화
document.addEventListener('DOMContentLoaded', () => {
    // 지도가 완전히 로드될 때까지 대기
    const checkMapInterval = setInterval(() => {
        if (window.map_718005d04db2f7b490d1b6e073270da7 && window.geo_json_f53b76cc8e581e006d61501b949050d0) {
            clearInterval(checkMapInterval);
            console.log('지도가 로드되었습니다. 클러스터 시각화 초기화 중...');
            loadClusterData();
            
            // GeoJSON이 로드된 후 이벤트 추가
            setTimeout(() => {
                addLayerEvents();
            }, 2000);
        }
    }, 500);
});
