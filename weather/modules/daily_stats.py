"""
daily_stats.py
시간별 데이터에서 일별 통계(최저/최고 온도)를 생성하는 모듈
"""

import pandas as pd
import sqlite3
from pathlib import Path


def create_daily_temperature_stats(integrated_csv_path: Path, 
                                   output_dir: Path,
                                   db_dir: Path,
                                   start_date: str,
                                   end_date: str) -> tuple:
    """
    시간별 통합 CSV에서 일별 최저/최고 온도 파일 생성 (CSV & DB)
    
    Args:
        integrated_csv_path: 통합 CSV 파일 경로 (시간별 데이터)
        output_dir: CSV 출력 디렉토리
        db_dir: DB 출력 디렉토리
        start_date: 시작 날짜 (YYYYMM)
        end_date: 종료 날짜 (YYYYMM)
    
    Returns:
        (CSV 파일 경로, DB 파일 경로) 튜플
    """
    # 통합 CSV 읽기
    df = pd.read_csv(integrated_csv_path)
    
    # date별로 그룹화하여 최저/최고 온도 계산
    daily_stats = df.groupby('date').agg({
        'temperature': ['min', 'max']
    }).reset_index()
    
    # 컬럼명 정리
    daily_stats.columns = ['date', 'min_temp', 'max_temp']
    
    # 소숫점 1자리로 반올림
    daily_stats['min_temp'] = daily_stats['min_temp'].round(1)
    daily_stats['max_temp'] = daily_stats['max_temp'].round(1)
    
    # CSV 파일 저장
    csv_filename = f"daily_temp_{start_date}_{end_date}.csv"
    csv_path = output_dir / csv_filename
    daily_stats.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    print(f"\n일별 최저/최고 온도 CSV 생성: {csv_path}")
    print(f"  - 총 {len(daily_stats)}일 데이터")
    
    # SQLite DB 저장
    db_filename = f"daily_temp_{start_date}_{end_date}.db"
    db_path = db_dir / db_filename
    
    # 기존 DB 삭제
    if db_path.exists():
        db_path.unlink()
    
    # SQLite 연결 및 테이블 생성
    conn = sqlite3.connect(db_path)
    daily_stats.to_sql('daily_temperature', conn, if_exists='replace', index=False)
    
    # 인덱스 생성
    cursor = conn.cursor()
    cursor.execute('CREATE INDEX idx_date ON daily_temperature(date)')
    
    conn.commit()
    conn.close()
    
    print(f"일별 최저/최고 온도 DB 생성: {db_path}")
    
    return csv_path, db_path


if __name__ == "__main__":
    # 테스트 코드
    from pathlib import Path
    
    integrated_csv = Path("data/processed/202301_202512.csv")
    output_dir = Path("data/processed")
    db_dir = Path("data/db")
    
    if integrated_csv.exists():
        csv_path, db_path = create_daily_temperature_stats(
            integrated_csv, 
            output_dir,
            db_dir,
            "202301",
            "202512"
        )
        
        # 결과 확인
        df = pd.read_csv(csv_path)
        print(f"\n생성된 CSV 파일 샘플:")
        print(df.head(10))
        
        # DB 확인
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM daily_temperature LIMIT 5")
        print(f"\n생성된 DB 파일 샘플:")
        for row in cursor.fetchall():
            print(f"  {row}")
        conn.close()
