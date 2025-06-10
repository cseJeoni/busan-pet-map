"""
동물병원 데이터 저장소 구현
"""
import os
import json
import pandas as pd
import geopandas as gpd
from typing import List, Dict, Any, Optional
from shapely.geometry import Point

from src.domain.entity import VetHospital
from src.domain.repository import VetHospitalRepository


class InMemoryVetHospitalRepository(VetHospitalRepository):
    """메모리 기반 동물병원 레포지토리 구현"""
    
    def __init__(self):
        self.hospitals: List[VetHospital] = []
    
    def save_hospitals(self, hospitals: List[VetHospital]) -> None:
        """동물병원 목록 저장"""
        self.hospitals = hospitals
    
    def get_hospitals(self) -> List[VetHospital]:
        """저장된 동물병원 목록 조회"""
        return self.hospitals
    
    def get_hospitals_by_dong(self, dong_code: str) -> List[VetHospital]:
        """특정 행정동의 동물병원 목록 조회"""
        return [h for h in self.hospitals if h.dong_code == dong_code]
    
    def get_hospitals_count_by_dong(self) -> Dict[str, int]:
        """행정동별 동물병원 개수 조회"""
        counts = {}
        for hospital in self.hospitals:
            if hospital.dong_code:
                counts[hospital.dong_code] = counts.get(hospital.dong_code, 0) + 1
        return counts


class FileVetHospitalRepository(VetHospitalRepository):
    """파일 기반 동물병원 레포지토리 구현"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.hospitals: List[VetHospital] = []
        
        # 데이터 디렉토리 생성
        os.makedirs(data_dir, exist_ok=True)
    
    def save_hospitals(self, hospitals: List[VetHospital]) -> None:
        """
        동물병원 목록 저장
        - JSON 파일로 저장
        - CSV 파일로 저장
        - GeoJSON 파일로 저장
        """
        self.hospitals = hospitals
        
        # JSON 파일로 저장
        hospitals_dict = [self._hospital_to_dict(h) for h in hospitals]
        with open(os.path.join(self.data_dir, "vet_hospitals.json"), "w", encoding="utf-8") as f:
            json.dump(hospitals_dict, f, ensure_ascii=False, indent=2)
        
        # CSV 파일로 저장
        df = pd.DataFrame([self._hospital_to_dict(h) for h in hospitals])
        df.to_csv(os.path.join(self.data_dir, "vet_hospitals.csv"), index=False, encoding="utf-8")
        
        # GeoJSON 파일로 저장
        gdf = gpd.GeoDataFrame(
            [self._hospital_to_dict(h) for h in hospitals],
            geometry=[Point(h.longitude, h.latitude) for h in hospitals],
            crs="EPSG:4326"
        )
        gdf.to_file(os.path.join(self.data_dir, "vet_hospitals.geojson"), driver="GeoJSON")
    
    def get_hospitals(self) -> List[VetHospital]:
        """저장된 동물병원 목록 조회"""
        if not self.hospitals:
            self._load_hospitals()
        return self.hospitals
    
    def get_hospitals_by_dong(self, dong_code: str) -> List[VetHospital]:
        """특정 행정동의 동물병원 목록 조회"""
        if not self.hospitals:
            self._load_hospitals()
        return [h for h in self.hospitals if h.dong_code == dong_code]
    
    def get_hospitals_count_by_dong(self) -> Dict[str, int]:
        """행정동별 동물병원 개수 조회"""
        if not self.hospitals:
            self._load_hospitals()
        
        counts = {}
        for hospital in self.hospitals:
            if hospital.dong_code:
                counts[hospital.dong_code] = counts.get(hospital.dong_code, 0) + 1
        return counts
    
    def _load_hospitals(self) -> None:
        """저장된 동물병원 데이터 로드"""
        json_path = os.path.join(self.data_dir, "vet_hospitals.json")
        
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                hospitals_dict = json.load(f)
            
            self.hospitals = [self._dict_to_hospital(h) for h in hospitals_dict]
    
    def _hospital_to_dict(self, hospital: VetHospital) -> Dict[str, Any]:
        """VetHospital 객체를 딕셔너리로 변환"""
        return {
            "id": hospital.id,
            "name": hospital.name,
            "address": hospital.address,
            "latitude": hospital.latitude,
            "longitude": hospital.longitude,
            "phone": hospital.phone,
            "place_url": hospital.place_url,
            "dong_code": hospital.dong_code,
            "dong_name": hospital.dong_name
        }
    
    def _dict_to_hospital(self, data: Dict[str, Any]) -> VetHospital:
        """딕셔너리를 VetHospital 객체로 변환"""
        return VetHospital(
            id=data["id"],
            name=data["name"],
            address=data["address"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            phone=data.get("phone"),
            place_url=data.get("place_url"),
            dong_code=data.get("dong_code"),
            dong_name=data.get("dong_name")
        )
