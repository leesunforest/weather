"""
data_parser.py
CSV 파일을 파싱하여 DataFrame으로 변환하는 모듈
"""

import re
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Tuple


def parse_filename(filename: str) -> Tuple[str, str, str]:
    """
    파일명에서 데이터 타입과 기간 추출
    
    Args:
        filename: 파일명 (예: 기온_202301_202312.csv)
    
    Returns:
        (데이터타입, 시작날짜, 종료날짜) 튜플
        예: ('기온', '202301', '202312')
    """
    pattern = r'(기온|강수|강수형태)_(\d{6})_(\d{6})\.csv'
    match = re.match(pattern, filename)
    if match:
        return match.groups()
    return None, None, None


def parse_csv_data(filepath: Path, start_date: str) -> pd.DataFrame:
    """
    CSV 파일을 파싱하여 DataFrame으로 변환
    
    Args:
        filepath: CSV 파일 경로
        start_date: 시작 날짜 (YYYYMM 형식) - 참고용, 실제로는 파일 내 Start 헤더 사용
    
    Returns:
        datetime과 value 컬럼을 가진 DataFrame
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 데이터 파싱
    records = []
    current_base_date = None
    
    for line in lines:
        line = line.strip()
        
        # Start 헤더 찾기 (예: "Start : 20230101")
        if 'Start :' in line or 'Start:' in line:
            # 날짜 추출
            date_str = line.split(':')[-1].strip()
            if len(date_str) == 8:  # YYYYMMDD 형식
                year = int(date_str[:4])
                month = int(date_str[4:6])
                current_base_date = datetime(year, month, 1)
                continue
        
        # 데이터 라인 파싱
        parts = [x.strip() for x in line.split(',')]
        if len(parts) == 3 and current_base_date:
            try:
                day = int(parts[0])
                hour = parts[1]  # '0000', '0100', etc.
                value = float(parts[2])
                
                # datetime 생성
                dt = current_base_date + timedelta(days=day - 1)
                hour_val = int(hour[:2])
                dt = dt.replace(hour=hour_val)
                
                records.append({'datetime': dt, 'value': value})
            except (ValueError, TypeError):
                continue
    
    df = pd.DataFrame(records)
    
    return df


if __name__ == "__main__":
    # 테스트 코드
    filename = "기온_202301_202312.csv"
    data_type, start, end = parse_filename(filename)
    print(f"파일명: {filename}")
    print(f"데이터 타입: {data_type}, 시작: {start}, 종료: {end}")
