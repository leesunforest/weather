# 기상 데이터 시각화 가이드

## 📊 개요

`analyze_weather.py` 스크립트를 사용하면 SQLite 데이터베이스의 기상 데이터를 분석하고 다양한 그래프로 시각화할 수 있습니다.

---

## 🚀 빠른 시작

### 1단계: 필수 라이브러리 설치

```bash
pip install pandas matplotlib
```

### 2단계: 스크립트 실행

```bash
cd weather/modules
python3 analyze_weather.py
```

기본적으로 `../data/db/202301_202512.db` 파일을 분석합니다.

또는 특정 DB 파일을 지정할 수 있습니다:

```bash
python3 analyze_weather.py /path/to/your/database.db
```

### 3단계: 결과 확인

실행이 완료되면 `graphs/` 폴더에 5개의 그래프가 생성됩니다.

---

## 📈 생성되는 그래프

### 1. `temperature_trend.png` - 기온 추세
- **설명**: 일별 평균 기온의 시계열 변화
- **용도**: 전체 기간 동안의 기온 추세 파악
- **특징**: 계절 변화, 이상 기온 확인

### 2. `temperature_distribution.png` - 기온 분포
- **설명**: 전체 기간 동안의 기온 분포 히스토그램
- **용도**: 기온의 분포 패턴 확인
- **특징**: 평균, 중앙값 표시

### 3. `hourly_pattern.png` - 시간대별 패턴
- **설명**: 하루 중 시간대별 평균 기온
- **용도**: 일일 기온 변화 패턴 확인
- **특징**: 최고/최저 기온 시간대 파악

### 4. `monthly_stats.png` - 월별 통계
- **설명**: 월별 최고/평균/최저 기온
- **용도**: 월별 기온 변화 추이 분석
- **특징**: 계절별 기온 범위 확인

### 5. `rain_analysis.png` - 강수 분석
- **설명**: 
  - 상단: 일별 총 강수량
  - 하단: 강수형태 분포 (비/진눈깨비/눈)
- **용도**: 강수 패턴 및 형태 분석

---

## 📊 통계 정보

스크립트 실행 시 콘솔에 다음 정보가 출력됩니다:

```
============================================================
기상 데이터 통계
============================================================

데이터 기간: 20230101 ~ 20250131
총 레코드 수: 2,232

[기온 통계]
  평균: -0.76°C
  최고: 12.30°C
  최저: -50.00°C
  표준편차: 5.04°C

[강수 통계]
  강수 일수: 26일
  총 강수량: 85.30mm
  평균 일강수량: 0.92mm

[강수형태 분포]
  비: 27회
  진눈깨비: 17회
  눈: 31회
```

---

## 🔧 커스터마이징

### Python 코드에서 직접 사용

```python
from analyze_weather import WeatherAnalyzer

# 분석 객체 생성
analyzer = WeatherAnalyzer("../data/db/202301_202512.db")

# 통계 출력
analyzer.get_statistics()

# 개별 그래프 생성
analyzer.plot_temperature_trend("my_temp_trend.png")
analyzer.plot_hourly_pattern("my_hourly.png")

# 모든 그래프 한번에 생성
analyzer.plot_all(output_dir="./my_graphs")
```

### 특정 그래프만 생성

```python
from analyze_weather import WeatherAnalyzer

analyzer = WeatherAnalyzer("../data/db/202301_202512.db")

# 기온 추세만 생성
analyzer.plot_temperature_trend("temperature_only.png")

# 강수 분석만 생성
analyzer.plot_rain_analysis("rain_only.png")
```

---

## 📁 출력 구조

```
weather/
├── modules/
│   ├── analyze_weather.py    # 분석 스크립트
│   └── graphs/               # 생성된 그래프
│       ├── temperature_trend.png
│       ├── temperature_distribution.png
│       ├── hourly_pattern.png
│       ├── monthly_stats.png
│       └── rain_analysis.png
└── data/
    └── db/
        └── 202301_202512.db  # 원본 데이터
```

---

## 🎨 그래프 해석 팁

### 기온 추세 (temperature_trend.png)
- **상승 추세**: 봄/여름으로 가는 시기
- **하강 추세**: 가을/겨울로 가는 시기
- **급격한 변화**: 이상 기온 또는 계절 전환기

### 시간대별 패턴 (hourly_pattern.png)
- **최저 기온 시간**: 보통 새벽 5~7시
- **최고 기온 시간**: 보통 오후 1~3시
- **일교차**: 최고-최저 온도 차이

### 월별 통계 (monthly_stats.png)
- **최고 기온 라인**: 해당 월의 가장 더운 날
- **평균 기온 라인**: 해당 월의 평균적인 날씨
- **최저 기온 라인**: 해당 월의 가장 추운 날

---

## ⚠️ 문제 해결

### 오류: "No module named 'matplotlib'"
```bash
pip install matplotlib
```

### 그래프가 생성되지 않음
- DB 파일 경로가 정확한지 확인
- graphs 폴더 생성 권한이 있는지 확인

### 한글 폰트가 깨짐
스크립트는 기본적으로 영문 그래프를 생성합니다. 한글이 필요한 경우 스크립트 상단의 폰트 설정을 수정하세요:

```python
# Windows
plt.rcParams['font.family'] = 'Malgun Gothic'

# Mac
plt.rcParams['font.family'] = 'AppleGothic'

# Linux
plt.rcParams['font.family'] = 'NanumGothic'
```

---

## 💡 활용 예시

### 1. 특정 기간 데이터만 분석
```python
from analyze_weather import WeatherAnalyzer
import pandas as pd

analyzer = WeatherAnalyzer("../data/db/202301_202512.db")

# 2023년 데이터만 필터링
analyzer.df = analyzer.df[analyzer.df['datetime'].dt.year == 2023]

# 그래프 생성
analyzer.plot_all(output_dir="./2023_graphs")
```

### 2. 추가 분석 수행
```python
from analyze_weather import WeatherAnalyzer
import pandas as pd

analyzer = WeatherAnalyzer("../data/db/202301_202512.db")

# 극한 기온 날짜 찾기
hottest = analyzer.df.loc[analyzer.df['temperature'].idxmax()]
coldest = analyzer.df.loc[analyzer.df['temperature'].idxmin()]

print(f"가장 더웠던 날: {hottest['date']} {hottest['hour']} - {hottest['temperature']}°C")
print(f"가장 추웠던 날: {coldest['date']} {coldest['hour']} - {coldest['temperature']}°C")
```

---

## 📚 관련 문서

- **README.md** - 전체 프로젝트 개요
- **README_MODULES.md** - 모듈별 상세 설명
- **QUICK_START.md** - 빠른 시작 가이드

---

**Happy Analyzing! 📊**
