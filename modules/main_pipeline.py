#!/usr/bin/env python3
"""
main_pipeline.py
기상 데이터 처리 메인 파이프라인
모든 모듈을 통합하여 실행
"""

from pathlib import Path
import pandas as pd
from data_parser import parse_filename
from data_merger import get_file_groups, merge_data_type, merge_all_types
from data_saver import save_processed_csv, save_integrated_csv
from database_handler import create_sqlite_db


class WeatherDataPipeline:
    """기상 데이터 처리 파이프라인"""
    
    def __init__(self, base_dir: str = "."):
        """
        파이프라인 초기화
        
        Args:
            base_dir: 기본 디렉토리 경로
        """
        self.base_dir = Path(base_dir)
        self.raw_dir = self.base_dir / "data" / "raw"
        self.processed_dir = self.base_dir / "data" / "processed"
        self.db_dir = self.base_dir / "data" / "db"
        
        # 디렉토리 생성
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.db_dir.mkdir(parents=True, exist_ok=True)
    
    def run(self):
        """전체 파이프라인 실행"""
        print("=" * 60)
        print("기상 데이터 처리 파이프라인 시작")
        print("=" * 60)
        
        # 1단계: 파일 그룹화
        print("\n[1단계] raw 폴더의 파일 스캔...")
        file_groups = get_file_groups(self.raw_dir)
        
        for data_type, files in file_groups.items():
            print(f"\n{data_type}: {len(files)}개 파일")
            for filepath, start, end in files:
                print(f"  - {filepath.name}")
        
        # 2단계: 각 데이터 타입별 병합
        print("\n[2단계] 데이터 타입별 병합 및 processed 폴더에 저장...")
        processed_data = {}
        date_ranges = {}
        
        for data_type, files in file_groups.items():
            if not files:
                continue
            
            print(f"\n{data_type} 병합 중...")
            merged_df = merge_data_type(data_type, files)
            
            if merged_df is not None and len(merged_df) > 0:
                # 전체 기간 계산
                start_date = files[0][1]
                end_date = files[-1][2]
                
                # processed 폴더에 저장
                save_processed_csv(data_type, merged_df, start_date, 
                                 end_date, self.processed_dir)
                
                processed_data[data_type] = merged_df
                date_ranges[data_type] = (start_date, end_date)
        
        # 3단계: 통합 CSV 생성
        print("\n[3단계] 통합 CSV 파일 생성...")
        if '기온' in processed_data:
            temp_df = processed_data['기온']
            precip_df = processed_data.get('강수')
            precip_type_df = processed_data.get('강수형태')
            
            # 전체 기간 계산
            all_dates = [date_ranges[dt] for dt in date_ranges]
            overall_start = min(d[0] for d in all_dates)
            overall_end = max(d[1] for d in all_dates)
            
            # 데이터 병합
            integrated_df = merge_all_types(temp_df, precip_df, precip_type_df)
            
            # CSV 저장
            csv_path = save_integrated_csv(integrated_df, overall_start, 
                                          overall_end, self.processed_dir)
            
            # 4단계: SQLite DB 생성
            print("\n[4단계] SQLite 데이터베이스 생성...")
            db_path = create_sqlite_db(integrated_df, overall_start, 
                                      overall_end, self.db_dir)
        
        print("\n" + "=" * 60)
        print("파이프라인 완료!")
        print("=" * 60)
        print(f"\n생성된 파일:")
        print(f"  - Processed: {self.processed_dir}")
        print(f"  - Database: {self.db_dir}")


if __name__ == "__main__":
    pipeline = WeatherDataPipeline()
    pipeline.run()
