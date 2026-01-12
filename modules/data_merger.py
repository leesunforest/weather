"""
data_merger.py
여러 CSV 파일을 병합하고 중복을 제거하는 모듈
"""

import pandas as pd
from pathlib import Path
from typing import List, Tuple, Dict
from data_parser import parse_filename, parse_csv_data


def get_file_groups(raw_dir: Path) -> Dict[str, List[Tuple[Path, str, str]]]:
    """
    raw 폴더의 파일들을 데이터 타입별로 그룹화
    
    Args:
        raw_dir: raw 데이터 폴더 경로
    
    Returns:
        데이터 타입별로 그룹화된 파일 정보
        {'기온': [(파일경로, 시작날짜, 종료날짜), ...], ...}
    """
    groups = {'기온': [], '강수': [], '강수형태': []}
    
    for filepath in raw_dir.glob('*.csv'):
        data_type, start_date, end_date = parse_filename(filepath.name)
        if data_type:
            groups[data_type].append((filepath, start_date, end_date))
    
    # 시작 날짜 기준으로 정렬
    for data_type in groups:
        groups[data_type].sort(key=lambda x: x[1])
    
    return groups


def merge_data_type(data_type: str, files: List[Tuple[Path, str, str]]) -> pd.DataFrame:
    """
    같은 데이터 타입의 파일들을 병합
    
    Args:
        data_type: 데이터 타입 (기온, 강수, 강수형태)
        files: (파일경로, 시작날짜, 종료날짜) 튜플 리스트
    
    Returns:
        병합된 DataFrame
    """
    all_data = []
    
    for filepath, start_date, end_date in files:
        print(f"  - Processing {filepath.name}...")
        df = parse_csv_data(filepath, start_date)
        all_data.append(df)
    
    if not all_data:
        return None
    
    # 모든 데이터 병합 및 중복 제거
    merged_df = pd.concat(all_data, ignore_index=True)
    merged_df = merged_df.drop_duplicates(subset=['datetime']).sort_values('datetime')
    
    return merged_df


def merge_all_types(temp_df: pd.DataFrame, 
                    precip_df: pd.DataFrame, 
                    precip_type_df: pd.DataFrame) -> pd.DataFrame:
    """
    기온, 강수, 강수형태 데이터를 하나로 병합
    
    Args:
        temp_df: 기온 DataFrame
        precip_df: 강수 DataFrame
        precip_type_df: 강수형태 DataFrame
    
    Returns:
        통합된 DataFrame (date, hour, temperature, rain_prob, rain_type)
    """
    # datetime을 기준으로 병합
    merged = temp_df.copy().rename(columns={'value': 'temperature'})
    
    if precip_df is not None:
        precip_df_copy = precip_df.copy().rename(columns={'value': 'rain_prob'})
        merged = merged.merge(precip_df_copy, on='datetime', how='outer')
    
    if precip_type_df is not None:
        precip_type_df_copy = precip_type_df.copy().rename(columns={'value': 'rain_type'})
        merged = merged.merge(precip_type_df_copy, on='datetime', how='outer')
    
    # 정렬
    merged = merged.sort_values('datetime').reset_index(drop=True)
    
    # 날짜/시간 분리 (hour를 정수로)
    merged['date'] = merged['datetime'].dt.strftime('%Y%m%d')
    merged['hour'] = merged['datetime'].dt.hour  # 0~23 정수
    
    # 컬럼 순서 조정 (datetime 제거)
    final_columns = ['date', 'hour', 'temperature', 'rain_prob', 'rain_type']
    merged = merged[final_columns]
    
    return merged


if __name__ == "__main__":
    # 테스트 코드
    from pathlib import Path
    
    raw_dir = Path("data/raw")
    if raw_dir.exists():
        groups = get_file_groups(raw_dir)
        for data_type, files in groups.items():
            print(f"\n{data_type}: {len(files)}개 파일")
            for filepath, start, end in files:
                print(f"  - {filepath.name}")
