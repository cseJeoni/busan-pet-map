"""
NumPy 버전 문제를 해결하고 엑셀 파일을 CSV로 변환하는 스크립트
"""
import subprocess
import sys
import os

def fix_numpy_and_convert():
    """NumPy 버전 다운그레이드 및 엑셀 파일 변환 시도"""
    
    print("=== NumPy 호환성 문제 해결 및 엑셀 파일 변환 ===")
    
    # 1. 현재 환경 확인
    print("현재 NumPy 버전 확인 중...")
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import numpy; print(numpy.__version__)"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"현재 NumPy 버전: {result.stdout.strip()}")
        else:
            print(f"NumPy 버전 확인 실패: {result.stderr.strip()}")
    except Exception as e:
        print(f"NumPy 버전 확인 중 오류: {e}")
    
    # 2. NumPy 다운그레이드 시도
    print("\n=== NumPy 다운그레이드 시도 ===")
    print("NumPy 1.x 버전 설치 중... (pandas와 호환)")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "numpy<2.0.0", "--force-reinstall"],
            check=True
        )
        print("NumPy 다운그레이드 성공!")
    except subprocess.CalledProcessError as e:
        print(f"NumPy 다운그레이드 실패: {e}")
    
    # 3. openpyxl 업그레이드 시도
    print("\n=== openpyxl 업그레이드 시도 ===")
    print("openpyxl 3.1.0 이상 버전 설치 중...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "openpyxl>=3.1.0", "--force-reinstall"],
            check=True
        )
        print("openpyxl 업그레이드 성공!")
    except subprocess.CalledProcessError as e:
        print(f"openpyxl 업그레이드 실패: {e}")
    
    # 4. 엑셀 파일 변환 스크립트 재실행 시도
    print("\n=== 엑셀 변환 재시도 ===")
    excel_path = "data/fulldata_02_03_01_P_동물병원.xlsx"
    csv_path = "data/fulldata_02_03_01_P_동물병원.csv"
    
    if os.path.exists(excel_path):
        print(f"엑셀 파일 변환 시도: {excel_path} -> {csv_path}")
        conversion_script = """
import pandas as pd
df = pd.read_excel('{0}')
print(f'엑셀 파일 읽기 성공: {{len(df)}}행')
df.to_csv('{1}', encoding='utf-8', index=False)
print(f'CSV 파일 저장 성공: {1}')
print(f'데이터 미리보기:\\n{{df.head(3)}}')
""".format(excel_path, csv_path)
        
        try:
            subprocess.run([sys.executable, "-c", conversion_script], check=True)
            print("엑셀 변환 성공!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"엑셀 변환 실패: {e}")
    else:
        print(f"엑셀 파일이 존재하지 않습니다: {excel_path}")
    
    # 5. 대안 방법
    print("\n=== 대안 방법: Mac Numbers 사용 안내 ===")
    print("1. Mac의 Numbers로 엑셀 파일을 열고 CSV로 내보내기하세요.")
    print("   File > Export To > CSV...")
    print(f"2. CSV 파일을 {csv_path}에 저장하세요.")
    print("3. 그런 다음 프로그램을 다시 실행하세요.")
    
    print("\n또는 다음 명령어로 LibreOffice를 설치하여 변환할 수 있습니다:")
    print("brew install libreoffice")
    print("libreoffice --headless --convert-to csv data/fulldata_02_03_01_P_동물병원.xlsx")
    
    return False

if __name__ == "__main__":
    fix_numpy_and_convert()
