import os
import shutil

MAP_PATH = 'output/vet_hospitals_busan_map.html'
NEW_PATH = 'output/vet_hospitals_busan_map_custom.html'

# 원본 folium 지도는 그대로 두고 새 레이아웃만 만들기
# 원본 지도는 iframe으로 포함할 것임

# 새 HTML 템플릿
custom_html = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>부산에서 강아지 키우기 좋은 동네</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: 'Noto Sans KR', Arial, sans-serif;
            background: #f7f7fa;
            overflow-x: hidden;
        }
        .header {
            width: 100%;
            background: #3b82f6;
            color: #fff;
            font-size: 2rem;
            font-weight: bold;
            text-align: center;
            padding: 1.5rem 0 1.2rem 0;
            letter-spacing: -1px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }
        .container {
            display: flex;
            flex-direction: row;
            width: 100%;
            height: calc(100vh - 77px);
            min-height: 500px;
        }
        .left-map {
            width: 50%;
            min-width: 320px;
            height: 100%;
        }
        .map-iframe {
            width: 100%;
            height: 100%;
            border: none;
            display: block;
        }
        .right-panel {
            width: 50%;
            min-width: 320px;
            height: 100%;
            display: flex;
            flex-direction: column;
            background: #f7f7fa;
        }
        .right-top, .right-bottom {
            flex: 1;
            padding: 2rem;
            border-bottom: 1px solid #e5e7eb;
            background: #fff;
            overflow-y: auto;
        }
        .right-bottom {
            border-bottom: none;
            background: #f0f6ff;
        }
        @media (max-width: 900px) {
            .container { flex-direction: column; }
            .left-map, .right-panel { width: 100%; min-width: 0; }
            .left-map { height: 50%; }
            .right-panel { height: 50%; flex-direction: row; }
            .right-top, .right-bottom { flex: 1; padding: 1rem; border-bottom: none; border-right: 1px solid #e5e7eb; }
            .right-bottom { border-right: none; }
        }
    </style>
</head>
<body>
    <div class="header">부산에서 강아지 키우기 좋은 동네</div>
    <div class="container">
        <div class="left-map">
            <iframe class="map-iframe" src="./vet_hospitals_busan_map.html"></iframe>
        </div>
        <div class="right-panel">
            <div class="right-top">
                <!-- 상단 섹션: 자유롭게 내용 추가 -->
                <h3>추천 동네/행정동 정보</h3>
                <p>여기에 동물병원, 애견카페, 공원 등 동네별 요약 정보나 추천, 통계, 설명 등을 표시할 수 있습니다.</p>
            </div>
            <div class="right-bottom">
                <!-- 하단 섹션: 자유롭게 내용 추가 -->
                <h3>지도 사용법 및 안내</h3>
                <p>지도에서 원하는 레이어를 선택하거나, 마커를 클릭해 상세 정보를 확인하세요.</p>
            </div>
        </div>
    </div>
</body>
</html>
'''

with open(NEW_PATH, 'w', encoding='utf-8') as f:
    f.write(custom_html)

print(f"커스텀 레이아웃 HTML 생성 완료: {NEW_PATH}")
