"""
엑셀 파일을 CSV로 변환하는 간단한 스크립트
"""
import os
import sys

# 필요한 모듈들만 임포트 시도 (호환성 문제가 적은 것부터)
try:
    import pandas as pd
    USE_PANDAS = True
    print("pandas 사용 가능")
except ImportError:
    USE_PANDAS = False
    print("pandas 사용 불가")

def convert_excel_to_csv(excel_path, csv_path=None):
    """
    엑셀 파일을 CSV로 변환
    """
    if csv_path is None:
        csv_path = os.path.splitext(excel_path)[0] + '.csv'
    
    print(f"엑셀 파일: {excel_path}")
    print(f"CSV 파일: {csv_path}")
    
    if USE_PANDAS:
        try:
            # pandas로 변환 시도
            print("pandas를 사용하여 변환 중...")
            df = pd.read_excel(excel_path)
            df.to_csv(csv_path, index=False, encoding='utf-8')
            print(f"변환 성공! 행 수: {len(df)}")
            return True
        except Exception as e:
            print(f"pandas 변환 실패: {e}")
    
    # 다른 방법 시도
    try:
        # xlrd와 csv 모듈 사용 시도
        print("xlrd와 csv 모듈을 사용하여 변환 중...")
        import xlrd
        import csv
        
        wb = xlrd.open_workbook(excel_path)
        sh = wb.sheet_by_index(0)
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            c = csv.writer(f)
            for r in range(sh.nrows):
                c.writerow(sh.row_values(r))
        
        print("xlrd로 변환 성공!")
        return True
    except Exception as e:
        print(f"xlrd 변환 실패: {e}")
    
    # 또 다른 방법 시도
    try:
        # openpyxl 직접 사용 시도
        print("openpyxl을 직접 사용하여 변환 중...")
        from openpyxl import load_workbook
        
        wb = load_workbook(filename=excel_path, read_only=True)
        ws = wb.active
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            c = csv.writer(f)
            for row in ws.rows:
                c.writerow([cell.value for cell in row])
        
        print("openpyxl로 변환 성공!")
        return True
    except Exception as e:
        print(f"openpyxl 변환 실패: {e}")
    
    print("모든 변환 방법이 실패했습니다.")
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python convert_excel_to_csv.py [엑셀파일경로] [CSV파일경로(선택)]")
        sys.exit(1)
    
    excel_path = sys.argv[1]
    csv_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    convert_excel_to_csv(excel_path, csv_path)
