"""
data_saver.py
처리된 데이터를 다양한 형식으로 저장하는 모듈
"""

import pandas as pd
from pathlib import Path
from datetime import datetime


def save_processed_csv(data_type: str, df: pd.DataFrame, 
                       start_date: str, end_date: str, 
                       output_dir: Path) -> Path:
    """
    처리된 데이터를 원본 형식의 CSV로 저장
    
    Args:
        data_type: 데이터 타입 (기온, 강수, 강수형태)
        df: 저장할 DataFrame
        start_date: 시작 날짜 (YYYYMM)
        end_date: 종료 날짜 (YYYYMM)
        output_dir: 출력 디렉토리
    
    Returns:
        저장된 파일 경로
    """
    filename = f"{data_type}_{start_date}_{end_date}.csv"
    output_path = output_dir / filename
    
    # CSV 형식으로 저장 (원본 형식 유지)
    with open(output_path, 'w', encoding='utf-8') as f:
        # 헤더 작성
        f.write(f" format: day,hour,value location:60_127 Start : {start_date}01 \n")
        
        # 데이터 작성
        base_date = datetime(int(start_date[:4]), int(start_date[4:6]), 1)
        for _, row in df.iterrows():
            dt = row['datetime']
            day = (dt - base_date).days + 1
            hour = f"{dt.hour:04d}"
            value = row['value']
            f.write(f" {day}, {hour}, {value:.6f} \n")
    
    print(f"  Saved: {output_path}")
    return output_path


def save_integrated_csv(df: pd.DataFrame, start_date: str, end_date: str, 
                        output_dir: Path) -> Path:
    """
    통합 CSV 파일 저장 (date, hour, temperature, rain_prob, rain_type)
    
    Args:
        df: 통합 DataFrame
        start_date: 시작 날짜 (YYYYMM)
        end_date: 종료 날짜 (YYYYMM)
        output_dir: 출력 디렉토리
    
    Returns:
        저장된 파일 경로
    """
    filename = f"{start_date}_{end_date}.csv"
    output_path = output_dir / filename
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"\n통합 CSV 생성: {output_path}")
    return output_path


if __name__ == "__main__":
    # 테스트 코드
    print("데이터 저장 모듈")
