"""
엑셀 파일에서 동물병원 데이터를 로드하는 레포지토리
"""
import os
import pandas as pd
except ImportError:
    print("pandas 모듈을 가져올 수 없습니다. 기본 CSV 처리 방식을 사용합니다.")
    import csv
    pd = None
import subprocess
from typing import List, Dict, Any, Optional

from src.domain.entity import VetHospital


class ExcelRepository:
    """
    엑셀 파일에서 동물병원 데이터를 로드하는 레포지토리
    """
    
    def __init__(self, file_path: str):
        """
        데이터 파일 레포지토리 초기화
        
        Args:
            file_path: 엑셀 또는 CSV 파일 경로
        """
        self.file_path = file_path
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"파일이 존재하지 않습니다: {file_path}")
            
        # 파일 확장자 확인
        self.is_csv = file_path.lower().endswith('.csv')
        
        # CSV 파일이 있는지 확인하고 없으면 .xlsx 파일에서 변환된 CSV 파일 찾기
        if not self.is_csv:
            csv_path = os.path.splitext(file_path)[0] + '.csv'
            if os.path.exists(csv_path):
                print(f"CSV 파일이 존재합니다: {csv_path}. CSV 파일을 사용합니다.")
                self.file_path = csv_path
                self.is_csv = True
    
    def load_hospitals(self, city: str = "부산") -> List[VetHospital]:
        """
        파일에서 특정 도시의 동물병원 데이터 로드
        
        Args:
            city: 필터링할 도시 이름 (기본값: "부산")
        
        Returns:
            도시에 해당하는 동물병원 리스트
        """
        try:
            if self.is_csv:
                # CSV 파일에서 직접 로드
                hospitals = self._load_from_csv(self.file_path, city)
            elif pd is not None:
                # pandas로 엑셀 파일 로드 시도
                hospitals = self._load_with_pandas(city)
            else:
                # pandas가 없으면 CSV 변환 후 로드 시도
                print("pandas를 사용할 수 없어 CSV 변환이 필요합니다.")
                hospitals = self._convert_and_load(city)
        except Exception as e:
            print(f"데이터 로드 중 오류 발생: {e}")
            print("CSV 처리 방식으로 전환합니다.")
            hospitals = self._load_from_csv_basic(self.file_path, city)
            
        print(f"{len(hospitals)}개 동물병원 데이터 로드됨 (도시: {city})")
        return hospitals
    
    def _load_with_pandas(self, city: str) -> List[VetHospital]:
        """pandas를 사용해 엑셀 파일에서 데이터 로드"""
        df = pd.read_excel(self.file_path)
        
        # 주소(도로명 또는 지번) 필드가 있다고 가정하고 city로 필터링
        filtered_df = df[df.apply(lambda row: self._is_in_city(row, city), axis=1)]
        
        hospitals = []
        for _, row in filtered_df.iterrows():
            hospital = self._row_to_hospital(row)
            if hospital:
                hospitals.append(hospital)
                
        return hospitals
    
    def _convert_and_load(self, city: str) -> List[VetHospital]:
        """엑셀 파일을 CSV로 변환 후 로드 (pandas 호환성 문제 해결용)"""
        csv_path = f"{os.path.splitext(self.file_path)[0]}.csv"
        
        # 다른 방법으로 엑셀을 CSV로 변환 (예: ssconvert, Excel 앱 등)
        # 이 예제에서는 변환이 이미 되었다고 가정
        if not os.path.exists(csv_path):
            print(f"CSV 파일이 존재하지 않습니다: {csv_path}")
            print("엑셀을 CSV로 변환 중...")
            
            try:
                # 파이썬을 사용하여 엑셀을 CSV로 변환 (openpyxl 없이)
                self._excel_to_csv_with_subprocess(self.file_path, csv_path)
            except Exception as e:
                print(f"변환 중 오류 발생: {e}")
                # 빈 리스트 반환
                return []
        
        # CSV 파일 로드
        return self._load_from_csv(csv_path, city)
    
    def _excel_to_csv_with_subprocess(self, excel_path: str, csv_path: str):
        """외부 명령어를 사용해 엑셀을 CSV로 변환"""
        cmd = [
            "python", "-c", 
            f"import pandas as pd
except ImportError:
    print("pandas 모듈을 가져올 수 없습니다. 기본 CSV 처리 방식을 사용합니다.")
    import csv
    pd = None; pd.read_excel('{excel_path}').to_csv('{csv_path}', index=False, encoding='utf-8')"
        ]
        
        # 서브프로세스로 실행
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("변환 성공!")
        except subprocess.CalledProcessError as e:
            print(f"변환 실패: {e.stderr}")
            # 다른 방법으로 시도
            self._try_alternative_conversion(excel_path, csv_path)
    
    def _try_alternative_conversion(self, excel_path: str, csv_path: str):
        """다른 방법으로 엑셀을 CSV로 변환 시도"""
        print("대체 변환 방법 시도 중...")
        # 시스템에 따라 다른 방법 사용 (예: Mac에서는 numbers, Windows에서는 excel.exe)
        if os.name == 'posix':  # macOS, Linux
            try:
                cmd = ["ssconvert", excel_path, csv_path]
                subprocess.run(cmd, check=True)
                print("gnumeric ssconvert로 변환 성공!")
            except:
                print("ssconvert 실패, 수동 변환이 필요합니다.")
        else:
            print("자동 변환이 지원되지 않습니다. 수동으로 CSV로 변환해주세요.")
    
    def _load_from_csv(self, csv_path: str, city: str) -> List[VetHospital]:
        """pandas를 사용하여 CSV 파일에서 데이터 로드"""
        if pd is None:
            return self._load_from_csv_basic(csv_path, city)
            
        try:
            df = pd.read_csv(csv_path, encoding='utf-8')
            print(f"CSV 파일에서 총 {len(df)}개 행 로드됨")
            print(f"컬럼 목록: {', '.join(df.columns.tolist())}")
            
            # 샘플 데이터 출력
            print("\n=== 처음 3개 행 미리보기 ===")
            print(df.head(3))
            
            # city로 필터링
            filtered_df = df[df.apply(lambda row: self._is_in_city(row, city), axis=1)]
            print(f"'{city}' 필터링 후 {len(filtered_df)}개 행 남음")
            
            hospitals = []
            for _, row in filtered_df.iterrows():
                hospital = self._row_to_hospital(row)
                if hospital:
                    hospitals.append(hospital)
                    
            return hospitals
        except Exception as e:
            print(f"pandas로 CSV 로드 중 오류 발생: {e}")
            return self._load_from_csv_basic(csv_path, city)
    
    def _load_from_csv_basic(self, csv_path: str, city: str) -> List[VetHospital]:
        """기본 csv 모듈을 사용하여 CSV 파일에서 데이터 로드 (pandas 없을 때)"""
        print("기본 CSV 모듈 사용")
        hospitals = []
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                print(f"CSV 헤더: {headers}")
                
                # 주소 필드 찾기
                address_fields = [h for h in headers if '주소' in h or '소재지' in h]
                print(f"주소 관련 필드: {address_fields}")
                
                for row_num, row in enumerate(reader):
                    # 도시 필터링
                    is_in_city = False
                    for field in address_fields:
                        if field in row and row[field] and city in row[field]:
                            is_in_city = True
                            break
                    
                    if not is_in_city:
                        continue
                        
                    # 병원 객체 생성
                    hospital_dict = {}
                    for field in row:
                        hospital_dict[field] = row[field]
                    
                    # 메타데이터 출력 (처음 몇 개만)
                    if row_num < 3:
                        print(f"\n데이터 행 {row_num+1}: {hospital_dict}")
                    
                    # 병원 객체 생성
                    hospital = self._dict_to_hospital(hospital_dict)
                    if hospital:
                        hospitals.append(hospital)
                        
                print(f"총 {len(hospitals)}개 병원 로드됨")
                return hospitals
        except Exception as e:
            print(f"기본 CSV 로드 중 오류: {e}")
            return []
    
    def _is_in_city(self, row: pd.Series, city: str) -> bool:
        """행이 특정 도시에 속하는지 확인 (주소 필드에 도시명 포함 여부)"""
        # 데이터셋의 열 이름이 확실하지 않으므로 가능한 주소 필드 후보들을 확인
        address_fields = ['주소', '소재지도로명주소', '소재지지번주소', '도로명주소', '지번주소', '주소(도로명)', '주소(지번)']
        
        for field in address_fields:
            if field in row and isinstance(row[field], str) and city in row[field]:
                return True
        
        # 시도 및 시군구 필드가 따로 있는 경우
        if '시도' in row and row['시도'] == city:
            return True
        if '시군구' in row and city in row['시군구']:
            return True
            
        return False
    
    def _row_to_hospital(self, row: pd.Series) -> Optional[VetHospital]:
        """pandas Series 행을 VetHospital 객체로 변환"""
        try:
            # 필드명이 데이터셋마다 다를 수 있으므로 가능한 필드명 후보들을 확인
            name = self._get_value_from_candidates(row, ['사업장명', '병원명', '이름', '업체명', '상호', '사업자명'])
            address = self._get_value_from_candidates(row, [
                '주소', '소재지도로명주소', '소재지지번주소', '도로명주소', '지번주소', 
                '주소(도로명)', '주소(지번)', '소재지(도로명)', '소재지(지번)'
            ])
            
            # 위도 경도 추출
            latitude = self._get_value_from_candidates(row, ['위도', 'latitude', 'lat', 'Y', '좌표정보(Y)', 'Y좌표'])
            longitude = self._get_value_from_candidates(row, ['경도', 'longitude', 'lon', 'lng', 'X', '좌표정보(X)', 'X좌표'])
            
            # 전화번호 추출
            phone = self._get_value_from_candidates(row, ['전화번호', '연락처', 'tel', '전화', '대표전화', '소재지전화'])
            
            # ID 생성: 없으면 이름+주소 조합으로 (중복 방지)
            id_value = self._get_value_from_candidates(row, ['id', 'ID', '식별자', '관리번호', '번호'])
            if not id_value:
                id_value = str(hash(f"{name}_{address}"))
                
            # 필수 필드 확인
            if not name or not address:
                return None
                
            # 좌표가 없거나 숫자가 아니면 None으로 설정
            try:
                lat_float = float(latitude) if latitude else None
                lng_float = float(longitude) if longitude else None
            except:
                lat_float = None
                lng_float = None
                
            return VetHospital(
                id=id_value,
                name=name,
                address=address,
                latitude=lat_float,
                longitude=lng_float,
                phone=phone or "",
                place_url="",  # 엑셀/CSV에는 없는 필드
                dong_code=None,
                dong_name=None
            )
        except Exception as e:
            print(f"병원 객체 생성 중 오류: {e}")
            return None
    
    def _dict_to_hospital(self, row_dict: Dict[str, str]) -> Optional[VetHospital]:
        """딕셔너리를 VetHospital 객체로 변환 (기본 CSV 처리용)"""
        try:
            # 필드명 후보에서 값 추출
            name_fields = ['사업장명', '병원명', '이름', '업체명', '상호', '사업자명', '기관명']
            name = None
            for field in name_fields:
                if field in row_dict and row_dict[field]:
                    name = row_dict[field]
                    break
                    
            # 주소 추출
            address_fields = [
                '주소', '소재지도로명주소', '소재지지번주소', '도로명주소', '지번주소', 
                '주소(도로명)', '주소(지번)', '소재지(도로명)', '소재지(지번)', '소재지'
            ]
            address = None
            for field in address_fields:
                if field in row_dict and row_dict[field]:
                    address = row_dict[field]
                    break
            
            # 필수 필드 확인
            if not name or not address:
                return None
                
            # 위도 경도 추출
            lat_fields = ['위도', 'latitude', 'lat', 'Y', '좌표정보(Y)', 'Y좌표']
            lng_fields = ['경도', 'longitude', 'lon', 'lng', 'X', '좌표정보(X)', 'X좌표']
            
            latitude = None
            longitude = None
            
            for field in lat_fields:
                if field in row_dict and row_dict[field]:
                    latitude = row_dict[field]
                    break
                    
            for field in lng_fields:
                if field in row_dict and row_dict[field]:
                    longitude = row_dict[field]
                    break
            
            # 전화번호 추출
            phone_fields = ['전화번호', '연락처', 'tel', '전화', '대표전화', '소재지전화']
            phone = ""
            for field in phone_fields:
                if field in row_dict and row_dict[field]:
                    phone = row_dict[field]
                    break
            
            # ID 생성: 없으면 이름+주소 조합으로 (중복 방지)
            id_fields = ['id', 'ID', '식별자', '관리번호', '번호']
            id_value = None
            for field in id_fields:
                if field in row_dict and row_dict[field]:
                    id_value = row_dict[field]
                    break
                    
            if not id_value:
                id_value = str(hash(f"{name}_{address}"))
            
            # 좌표가 없거나 숫자가 아니면 None으로 설정
            try:
                lat_float = float(latitude) if latitude else None
                lng_float = float(longitude) if longitude else None
            except:
                lat_float = None
                lng_float = None
                
            return VetHospital(
                id=id_value,
                name=name,
                address=address,
                latitude=lat_float,
                longitude=lng_float,
                phone=phone,
                place_url="",
                dong_code=None,
                dong_name=None
            )
        except Exception as e:
            print(f"딕셔너리 변환 중 오류: {e}")
            return None
    
    def _get_value_from_candidates(self, row: pd.Series, candidates: List[str]):
        """여러 후보 필드명 중 존재하는 첫 번째 필드의 값 반환"""
        for field in candidates:
            if field in row and row[field] is not None and row[field] != "":
                return row[field]
        return None
