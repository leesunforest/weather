"""
database_handler.py
SQLite 데이터베이스 생성 및 관리 모듈
"""

import sqlite3
import pandas as pd
from pathlib import Path


def create_sqlite_db(df: pd.DataFrame, start_date: str, end_date: str, 
                     db_dir: Path) -> Path:
    """
    SQLite 데이터베이스 생성
    
    Args:
        df: 저장할 DataFrame
        start_date: 시작 날짜 (YYYYMM)
        end_date: 종료 날짜 (YYYYMM)
        db_dir: 데이터베이스 디렉토리
    
    Returns:
        생성된 DB 파일 경로
    """
    db_filename = f"{start_date}_{end_date}.db"
    db_path = db_dir / db_filename
    
    # 기존 DB 삭제
    if db_path.exists():
        db_path.unlink()
    
    # SQLite 연결 및 테이블 생성
    conn = sqlite3.connect(db_path)
    
    # 테이블 생성
    df.to_sql('weather_data', conn, if_exists='replace', index=False)
    
    # 인덱스 생성 (영문 컬럼명으로 변경)
    cursor = conn.cursor()
    cursor.execute('CREATE INDEX idx_date_hour ON weather_data(date, hour)')
    
    conn.commit()
    conn.close()
    
    print(f"SQLite DB 생성: {db_path}")
    return db_path


def query_database(db_path: Path, query: str) -> list:
    """
    데이터베이스 쿼리 실행
    
    Args:
        db_path: 데이터베이스 파일 경로
        query: SQL 쿼리문
    
    Returns:
        쿼리 결과 리스트
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


def get_table_info(db_path: Path) -> list:
    """
    데이터베이스 테이블 정보 조회
    
    Args:
        db_path: 데이터베이스 파일 경로
    
    Returns:
        테이블 컬럼 정보
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(weather_data)")
    columns = cursor.fetchall()
    conn.close()
    return columns


if __name__ == "__main__":
    # 테스트 코드
    print("데이터베이스 핸들러 모듈")
