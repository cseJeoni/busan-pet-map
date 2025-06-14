"""
부산시 행정동 GeoJSON 파일의 좌표계 변환
- 입력: data/busan_emd.geojson (EPSG:5174)
- 출력: data/busan_emd_wgs84.geojson (EPSG:4326, 경위도)
"""
import os
import geopandas as gpd

def transform_geojson_crs(
    input_geojson_path='data/busan_emd.geojson', 
    output_geojson_path='data/busan_emd_wgs84.geojson',
    source_crs='EPSG:5174',
    target_crs='EPSG:4326'
):
    """
    GeoJSON 파일의 좌표계를 변환합니다.
    
    Args:
        input_geojson_path: 입력 GeoJSON 파일 경로
        output_geojson_path: 출력 GeoJSON 파일 경로
        source_crs: 원본 좌표계 (ex: 'EPSG:5174')
        target_crs: 목표 좌표계 (ex: 'EPSG:4326' - WGS84 경위도)
    """
    print(f"좌표계 변환 시작: {source_crs} -> {target_crs}")
    print(f"입력 파일: {input_geojson_path}")
    
    # GeoJSON 파일을 GeoDataFrame으로 읽기
    try:
        gdf = gpd.read_file(input_geojson_path)
        print(f"원본 데이터: {len(gdf)}개 피처")
        print(f"원본 좌표계: {gdf.crs}")
        
        # 원본 데이터에 좌표계가 없으면 원본 좌표계 지정
        if gdf.crs is None:
            print(f"좌표계 정보 없음, {source_crs}로 지정")
            gdf.set_crs(source_crs, inplace=True)
        
        # 좌표계 변환
        gdf_transformed = gdf.to_crs(target_crs)
        print(f"변환된 좌표계: {gdf_transformed.crs}")
        
        # 변환된 GeoJSON 저장
        os.makedirs(os.path.dirname(output_geojson_path), exist_ok=True)
        gdf_transformed.to_file(output_geojson_path, driver="GeoJSON")
        print(f"변환 완료! 결과 파일: {output_geojson_path}")
        
        return True
    except Exception as e:
        print(f"좌표계 변환 중 오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    transform_geojson_crs()
