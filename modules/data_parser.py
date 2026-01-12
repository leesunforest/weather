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
        start_date: 시작 날짜 (YYYYMM 형식)
    
    Returns:
        datetime과 value 컬럼을 가진 DataFrame
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 첫 줄은 헤더이므로 건너뛰기
    data_lines = lines[1:]
    
    # 데이터 파싱
    records = []
    for line in data_lines:
        parts = [x.strip() for x in line.split(',')]
        if len(parts) == 3:
            try:
                day = int(parts[0])
                hour = parts[1]  # '0000', '0100', etc.
                value = float(parts[2])
                records.append({'day': day, 'hour': hour, 'value': value})
            except ValueError:
                continue
    
    df = pd.DataFrame(records)
    
    # 날짜 생성 (start_date 기준)
    start_year = int(start_date[:4])
    start_month = int(start_date[4:6])
    base_date = datetime(start_year, start_month, 1)
    
    def make_datetime(row):
        try:
            dt = base_date + timedelta(days=row['day'] - 1)
            # hour 문자열을 HH 형식으로 파싱 (앞 2자리만)
            hour_val = int(row['hour'][:2])
            dt = dt.replace(hour=hour_val)
            return dt
        except:
            return None
    
    df['datetime'] = df.apply(make_datetime, axis=1)
    df = df.dropna(subset=['datetime'])
    
    return df[['datetime', 'value']]


if __name__ == "__main__":
    # 테스트 코드
    filename = "기온_202301_202312.csv"
    data_type, start, end = parse_filename(filename)
    print(f"파일명: {filename}")
    print(f"데이터 타입: {data_type}, 시작: {start}, 종료: {end}")
