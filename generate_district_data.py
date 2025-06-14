import pandas as pd
import json

# 필터링된 시설 데이터 읽기
df = pd.read_csv('output/facilities_with_district_filtered.csv')

# 행정동 단위 데이터만 필터링 (부산, 경남, 경계 외 등 제외)
districts = df[df['district'].str.contains('동|읍|면', na=False) & ~df['district'].str.contains('부산|경남|경계', na=False)]

# 행정동별로 시설 유형 카운트
counts = districts.groupby(['district', 'type']).size().unstack(fill_value=0)
counts = counts.reset_index()
counts.columns.name = None

# 필요한 열 확인 및 추가
for col in ['동물병원', '애견카페', '공원']:
    if col not in counts.columns:
        counts[col] = 0

# 필요한 열만 선택
counts = counts[['district', '동물병원', '애견카페', '공원']]

# 총합 계산하여 정렬
counts['총합'] = counts['동물병원'] + counts['애견카페'] + counts['공원']
counts = counts.sort_values('총합', ascending=False)

# 상위 15개 출력
print(counts.head(15).to_string())

# JavaScript 코드로 변환하여 저장
district_data = counts[['district', '동물병원', '애견카페', '공원']].to_dict(orient='records')

# JSON 형태로 저장
with open('output/district_data.json', 'w', encoding='utf-8') as f:
    json.dump(district_data, f, ensure_ascii=False, indent=2)

# JavaScript 배열 형태로 출력
js_array = []
for row in district_data:
    js_array.append(f"    {{ district: '{row['district']}', hospital: {row['동물병원']}, cafe: {row['애견카페']}, park: {row['공원']} }}")

with open('output/district_data.js', 'w', encoding='utf-8') as f:
    f.write("// 행정동별 시설 데이터 (필터링된 데이터 기준)\n")
    f.write("const districtData = [\n")
    f.write(",\n".join(js_array))
    f.write("\n];")

print(f"\n총 {len(district_data)}개 행정동의 데이터가 생성되었습니다.")
