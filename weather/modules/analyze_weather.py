#!/usr/bin/env python3
"""
analyze_weather.py
기상 데이터 분석 및 시각화 스크립트
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from pathlib import Path

# 한글 폰트 설정 (선택사항)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False


class WeatherAnalyzer:
    """기상 데이터 분석 클래스"""
    
    def __init__(self, db_path: str):
        """
        초기화
        
        Args:
            db_path: SQLite DB 파일 경로
        """
        self.db_path = Path(db_path)
        self.df = None
        self.load_data()
    
    def load_data(self):
        """데이터베이스에서 데이터 로드"""
        conn = sqlite3.connect(self.db_path)
        self.df = pd.read_sql("SELECT * FROM weather_data", conn)
        conn.close()
        
        # datetime 컬럼 생성
        self.df['datetime'] = pd.to_datetime(
            self.df['date'].astype(str) + self.df['hour'].astype(str).str.zfill(4),
            format='%Y%m%d%H%M'
        )
        
        print(f"데이터 로드 완료: {len(self.df)} 레코드")
        print(f"기간: {self.df['date'].min()} ~ {self.df['date'].max()}")
    
    def plot_temperature_trend(self, output_path: str = "temperature_trend.png"):
        """
        기온 추세 그래프
        
        Args:
            output_path: 저장할 파일 경로
        """
        plt.figure(figsize=(15, 6))
        
        # 일별 평균 기온 계산
        daily_temp = self.df.groupby('date')['temperature'].mean().reset_index()
        daily_temp['date'] = pd.to_datetime(daily_temp['date'], format='%Y%m%d')
        
        plt.plot(daily_temp['date'], daily_temp['temperature'], 
                linewidth=1, alpha=0.7)
        plt.title('Daily Average Temperature Trend', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Temperature (°C)', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # x축 날짜 포맷
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ 기온 추세 그래프 저장: {output_path}")
        plt.close()
    
    def plot_temperature_distribution(self, output_path: str = "temperature_distribution.png"):
        """
        기온 분포 히스토그램
        
        Args:
            output_path: 저장할 파일 경로
        """
        plt.figure(figsize=(10, 6))
        
        plt.hist(self.df['temperature'], bins=50, edgecolor='black', alpha=0.7)
        plt.title('Temperature Distribution', fontsize=16, fontweight='bold')
        plt.xlabel('Temperature (°C)', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.grid(True, alpha=0.3, axis='y')
        
        # 평균, 중앙값 표시
        mean_temp = self.df['temperature'].mean()
        median_temp = self.df['temperature'].median()
        plt.axvline(mean_temp, color='red', linestyle='--', 
                   label=f'Mean: {mean_temp:.1f}°C')
        plt.axvline(median_temp, color='green', linestyle='--', 
                   label=f'Median: {median_temp:.1f}°C')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ 기온 분포 그래프 저장: {output_path}")
        plt.close()
    
    def plot_hourly_pattern(self, output_path: str = "hourly_pattern.png"):
        """
        시간대별 평균 기온 패턴
        
        Args:
            output_path: 저장할 파일 경로
        """
        plt.figure(figsize=(12, 6))
        
        # 시간대별 평균 기온
        hourly_temp = self.df.copy()
        hourly_temp['hour_num'] = hourly_temp['hour'].astype(int) // 100
        hourly_avg = hourly_temp.groupby('hour_num')['temperature'].mean()
        
        plt.plot(hourly_avg.index, hourly_avg.values, marker='o', linewidth=2)
        plt.title('Average Temperature by Hour of Day', fontsize=16, fontweight='bold')
        plt.xlabel('Hour', fontsize=12)
        plt.ylabel('Temperature (°C)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(range(0, 24))
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ 시간대별 패턴 그래프 저장: {output_path}")
        plt.close()
    
    def plot_monthly_stats(self, output_path: str = "monthly_stats.png"):
        """
        월별 기온 통계 (최고/최저/평균)
        
        Args:
            output_path: 저장할 파일 경로
        """
        plt.figure(figsize=(14, 6))
        
        # 월별 통계 계산
        monthly_df = self.df.copy()
        monthly_df['month'] = monthly_df['datetime'].dt.to_period('M')
        monthly_stats = monthly_df.groupby('month')['temperature'].agg(['max', 'min', 'mean'])
        
        x = range(len(monthly_stats))
        plt.plot(x, monthly_stats['max'], marker='o', label='Max', linewidth=2)
        plt.plot(x, monthly_stats['mean'], marker='s', label='Average', linewidth=2)
        plt.plot(x, monthly_stats['min'], marker='^', label='Min', linewidth=2)
        
        plt.title('Monthly Temperature Statistics', fontsize=16, fontweight='bold')
        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Temperature (°C)', fontsize=12)
        plt.xticks(x, [str(m) for m in monthly_stats.index], rotation=45)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ 월별 통계 그래프 저장: {output_path}")
        plt.close()
    
    def plot_rain_analysis(self, output_path: str = "rain_analysis.png"):
        """
        강수 분석 그래프
        
        Args:
            output_path: 저장할 파일 경로
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # 1. 일별 총 강수량
        daily_rain = self.df.groupby('date')['rain_prob'].sum().reset_index()
        daily_rain['date'] = pd.to_datetime(daily_rain['date'], format='%Y%m%d')
        
        ax1.bar(daily_rain['date'], daily_rain['rain_prob'], alpha=0.7, width=1)
        ax1.set_title('Daily Total Precipitation', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Date', fontsize=11)
        ax1.set_ylabel('Precipitation (mm)', fontsize=11)
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # 2. 강수형태 분포
        rain_type_counts = self.df[self.df['rain_type'] > 0]['rain_type'].value_counts().sort_index()
        rain_type_labels = {0: 'None', 1: 'Rain', 2: 'Sleet', 3: 'Snow'}
        
        if len(rain_type_counts) > 0:
            labels = [rain_type_labels.get(int(x), f'Type {x}') for x in rain_type_counts.index]
            ax2.bar(labels, rain_type_counts.values, alpha=0.7)
            ax2.set_title('Precipitation Type Distribution', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Type', fontsize=11)
            ax2.set_ylabel('Count', fontsize=11)
            ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ 강수 분석 그래프 저장: {output_path}")
        plt.close()
    
    def plot_all(self, output_dir: str = "."):
        """
        모든 그래프 생성
        
        Args:
            output_dir: 출력 디렉토리
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print("\n" + "="*60)
        print("기상 데이터 시각화 시작")
        print("="*60)
        
        self.plot_temperature_trend(output_path / "temperature_trend.png")
        self.plot_temperature_distribution(output_path / "temperature_distribution.png")
        self.plot_hourly_pattern(output_path / "hourly_pattern.png")
        self.plot_monthly_stats(output_path / "monthly_stats.png")
        self.plot_rain_analysis(output_path / "rain_analysis.png")
        
        print("\n" + "="*60)
        print(f"모든 그래프 저장 완료! 위치: {output_path}")
        print("="*60)
    
    def get_statistics(self):
        """기본 통계 정보 출력"""
        print("\n" + "="*60)
        print("기상 데이터 통계")
        print("="*60)
        
        print(f"\n데이터 기간: {self.df['date'].min()} ~ {self.df['date'].max()}")
        print(f"총 레코드 수: {len(self.df):,}")
        
        print("\n[기온 통계]")
        print(f"  평균: {self.df['temperature'].mean():.2f}°C")
        print(f"  최고: {self.df['temperature'].max():.2f}°C")
        print(f"  최저: {self.df['temperature'].min():.2f}°C")
        print(f"  표준편차: {self.df['temperature'].std():.2f}°C")
        
        print("\n[강수 통계]")
        rainy_days = (self.df.groupby('date')['rain_prob'].sum() > 0).sum()
        total_rain = self.df['rain_prob'].sum()
        print(f"  강수 일수: {rainy_days}일")
        print(f"  총 강수량: {total_rain:.2f}mm")
        print(f"  평균 일강수량: {total_rain / len(self.df['date'].unique()):.2f}mm")
        
        print("\n[강수형태 분포]")
        rain_types = self.df[self.df['rain_type'] > 0]['rain_type'].value_counts().sort_index()
        rain_type_names = {1: '비', 2: '진눈깨비', 3: '눈'}
        for rt, count in rain_types.items():
            print(f"  {rain_type_names.get(rt, f'타입{rt}')}: {count}회")


if __name__ == "__main__":
    import sys
    
    # DB 경로 설정
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = "../data/db/202301_202512.db"
    
    # 분석 실행
    analyzer = WeatherAnalyzer(db_path)
    
    # 통계 출력
    analyzer.get_statistics()
    
    # 그래프 생성
    analyzer.plot_all(output_dir="./graphs")
    
    print("\n사용법:")
    print("  python3 analyze_weather.py [DB파일경로]")
    print("  예: python3 analyze_weather.py ../data/db/202301_202512.db")
