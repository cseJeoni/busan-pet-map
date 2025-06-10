"""
동물병원 데이터 시각화 유즈케이스
"""
import os
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple, List
import matplotlib.cm as cm
from matplotlib.colors import Normalize

from src.domain.repository import VetHospitalRepository, AdministrativeDongRepository


class VisualizeVetHospitalsUseCase:
    """동물병원 데이터 시각화 유즈케이스"""
    
    def __init__(
        self,
        vet_hospital_repository: VetHospitalRepository,
        dong_repository: AdministrativeDongRepository,
        output_dir: str = "output"
    ):
        """
        동물병원 데이터 시각화 유즈케이스 초기화
        
        Args:
            vet_hospital_repository: 동물병원 레포지토리
            dong_repository: 행정동 레포지토리
            output_dir: 출력 디렉토리
        """
        self.vet_hospital_repository = vet_hospital_repository
        self.dong_repository = dong_repository
        self.output_dir = output_dir
        
        # 출력 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)
        
        # 한글 폰트 설정
        plt.rcParams['font.family'] = 'AppleGothic'  # Mac OS용
        plt.rcParams['axes.unicode_minus'] = False
    
    def create_choropleth_map(self, 
                             title: str = "부산시 행정동별 동물병원 분포",
                             figsize: Tuple[int, int] = (12, 10),
                             save_path: Optional[str] = None) -> None:
        """
        행정동별 동물병원 개수 choropleth 지도 생성
        
        Args:
            title: 지도 제목
            figsize: 그림 크기
            save_path: 저장 경로 (없으면 기본 경로에 저장)
        """
        # 행정동 GeoDataFrame 가져오기
        dongs_gdf = self.dong_repository.get_dongs_geodataframe()
        
        # 행정동별 동물병원 개수 가져오기
        hospital_counts = self.vet_hospital_repository.get_hospitals_count_by_dong()
        
        # 행정동 GeoDataFrame에 동물병원 개수 추가
        dongs_gdf['vet_count'] = dongs_gdf['ADM_CD'].map(hospital_counts).fillna(0)
        
        # 그림 생성
        fig, ax = plt.subplots(figsize=figsize)
        
        # Choropleth 맵 그리기
        dongs_gdf.plot(
            column='vet_count',
            ax=ax,
            legend=True,
            cmap='YlOrRd',
            edgecolor='black',
            linewidth=0.3,
            legend_kwds={'label': '동물병원 수'}
        )
        
        # 제목 설정
        ax.set_title(title, fontsize=16)
        
        # 축 제거
        ax.set_axis_off()
        
        # 파일 저장
        if save_path is None:
            save_path = os.path.join(self.output_dir, "vet_hospitals_choropleth.png")
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_point_map(self, 
                        title: str = "부산시 동물병원 위치",
                        figsize: Tuple[int, int] = (12, 10),
                        save_path: Optional[str] = None) -> None:
        """
        동물병원 위치 점 지도 생성
        
        Args:
            title: 지도 제목
            figsize: 그림 크기
            save_path: 저장 경로 (없으면 기본 경로에 저장)
        """
        # 행정동 GeoDataFrame 가져오기
        dongs_gdf = self.dong_repository.get_dongs_geodataframe()
        
        # 동물병원 목록 가져오기
        hospitals = self.vet_hospital_repository.get_hospitals()
        
        # 동물병원 GeoDataFrame 생성
        hospitals_df = pd.DataFrame([{
            'name': h.name,
            'address': h.address,
            'latitude': h.latitude,
            'longitude': h.longitude,
            'dong_code': h.dong_code,
            'dong_name': h.dong_name
        } for h in hospitals])
        
        hospitals_gdf = gpd.GeoDataFrame(
            hospitals_df,
            geometry=gpd.points_from_xy(hospitals_df.longitude, hospitals_df.latitude),
            crs=dongs_gdf.crs
        )
        
        # 그림 생성
        fig, ax = plt.subplots(figsize=figsize)
        
        # 행정동 경계 그리기
        dongs_gdf.plot(
            ax=ax,
            color='lightgray',
            edgecolor='black',
            linewidth=0.3,
            alpha=0.5
        )
        
        # 동물병원 위치 점 그리기
        hospitals_gdf.plot(
            ax=ax,
            color='red',
            markersize=20,
            marker='o',
            alpha=0.7
        )
        
        # 제목 설정
        ax.set_title(title, fontsize=16)
        
        # 축 제거
        ax.set_axis_off()
        
        # 파일 저장
        if save_path is None:
            save_path = os.path.join(self.output_dir, "vet_hospitals_points.png")
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_top_dongs_bar_chart(self, 
                                  top_n: int = 5,
                                  title: str = "동물병원 수 상위 행정동",
                                  figsize: Tuple[int, int] = (10, 6),
                                  save_path: Optional[str] = None) -> None:
        """
        동물병원 수 상위 행정동 막대 그래프 생성
        
        Args:
            top_n: 상위 개수
            title: 그래프 제목
            figsize: 그림 크기
            save_path: 저장 경로 (없으면 기본 경로에 저장)
        """
        # 행정동별 동물병원 개수 가져오기
        hospital_counts = self.vet_hospital_repository.get_hospitals_count_by_dong()
        
        # 행정동 정보 가져오기
        dongs = {dong.code: dong.name for dong in self.dong_repository.get_all_dongs()}
        
        # 데이터프레임 생성
        df = pd.DataFrame([
            {'dong_code': code, 'dong_name': dongs.get(code, code), 'count': count}
            for code, count in hospital_counts.items()
        ])
        
        # 동물병원 수 기준 정렬 및 상위 N개 선택
        top_dongs = df.sort_values('count', ascending=False).head(top_n)
        
        # 그림 생성
        fig, ax = plt.subplots(figsize=figsize)
        
        # 막대 그래프 그리기
        bars = ax.bar(top_dongs['dong_name'], top_dongs['count'], color='skyblue')
        
        # 막대 위에 값 표시
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.,
                height + 0.1,
                f'{int(height)}',
                ha='center',
                va='bottom',
                fontsize=12
            )
        
        # 제목 및 레이블 설정
        ax.set_title(title, fontsize=16)
        ax.set_xlabel('행정동', fontsize=12)
        ax.set_ylabel('동물병원 수', fontsize=12)
        
        # 격자 추가
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # 여백 조정
        plt.tight_layout()
        
        # 파일 저장
        if save_path is None:
            save_path = os.path.join(self.output_dir, "top_dongs_bar_chart.png")
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        # SVG 형식으로도 저장 (웹 표시용)
        svg_path = os.path.splitext(save_path)[0] + ".svg"
        plt.figure(figsize=figsize)
        bars = plt.bar(top_dongs['dong_name'], top_dongs['count'], color='skyblue')
        
        # 막대 위에 값 표시
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.,
                height + 0.1,
                f'{int(height)}',
                ha='center',
                va='bottom',
                fontsize=12
            )
        
        plt.title(title, fontsize=16)
        plt.xlabel('행정동', fontsize=12)
        plt.ylabel('동물병원 수', fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(svg_path, format='svg')
        plt.close()
    
    def create_all_visualizations(self) -> List[str]:
        """
        모든 시각화 생성
        
        Returns:
            생성된 파일 경로 목록
        """
        output_files = []
        
        # Choropleth 지도
        choropleth_path = os.path.join(self.output_dir, "vet_hospitals_choropleth.png")
        self.create_choropleth_map(save_path=choropleth_path)
        output_files.append(choropleth_path)
        
        # 점 지도
        point_map_path = os.path.join(self.output_dir, "vet_hospitals_points.png")
        self.create_point_map(save_path=point_map_path)
        output_files.append(point_map_path)
        
        # 상위 행정동 막대 그래프
        bar_chart_path = os.path.join(self.output_dir, "top_dongs_bar_chart.png")
        self.create_top_dongs_bar_chart(save_path=bar_chart_path)
        output_files.append(bar_chart_path)
        output_files.append(os.path.splitext(bar_chart_path)[0] + ".svg")
        
        return output_files
