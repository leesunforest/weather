# Weather Data Pipeline - Quick Start Guide

## 📦 폴더 구조

```
weather/
├── QUICK_START.md         # 이 파일 - 빠른 시작 가이드
├── README.md              # 기본 사용법
├── README_MODULES.md      # 모듈별 상세 설명서
├── modules/              # Python 소스 코드
│   ├── main_pipeline.py       # 메인 실행 파일
│   ├── data_parser.py         # CSV 파싱 모듈
│   ├── data_merger.py         # 데이터 병합 모듈
│   ├── data_saver.py          # 파일 저장 모듈
│   └── database_handler.py    # SQLite DB 관리 모듈
└── data/                 # 데이터 폴더
    ├── raw/              # 원본 CSV 파일 (입력)
    ├── processed/        # 처리된 CSV 파일 (출력)
    └── db/               # SQLite 데이터베이스 (출력)
```

---

## 🚀 빠른 시작

### 1단계: 필수 라이브러리 확인 및 설치

이 프로그램은 **pandas**만 필요합니다.

```bash
# pandas 설치 여부 확인
python3 -c "import pandas; print('pandas', pandas.__version__, 'installed')"

# pandas가 없다면 설치
pip install pandas
```

**참고:** `sqlite3`는 Python 기본 내장 라이브러리이므로 별도 설치가 필요없습니다.

### 2단계: 데이터 준비
`data/raw/` 폴더에 다음 형식의 CSV 파일을 넣으세요:
- `기온_YYYYMM_YYYYMM.csv`
- `강수_YYYYMM_YYYYMM.csv`
- `강수형태_YYYYMM_YYYYMM.csv`

예시:
```
data/raw/
├── 기온_202301_202312.csv
├── 기온_202401_202412.csv
├── 강수_202301_202312.csv
├── 강수_202401_202412.csv
├── 강수형태_202301_202312.csv
└── 강수형태_202401_202412.csv
```

### 3단계: 파이프라인 실행
```bash
cd modules
python3 main_pipeline.py
```

### 4단계: 결과 확인
실행이 완료되면 다음 파일들이 생성됩니다:

**data/processed/**
- `기온_202301_202512.csv` - 병합된 기온 데이터
- `강수_202301_202512.csv` - 병합된 강수 데이터
- `강수형태_202301_202512.csv` - 병합된 강수형태 데이터
- `202301_202512.csv` - **통합 CSV 파일 (시간별)** ⭐
- `daily_temp_202301_202512.csv` - **일별 최저/최고 온도** ⭐

**data/db/**
- `202301_202512.db` - **시간별 데이터 SQLite DB** ⭐
- `daily_temp_202301_202512.db` - **일별 최저/최고 온도 SQLite DB** ⭐

---

## 📊 출력 데이터 형식

### 통합 CSV (`202301_202512.csv`) - 시간별 데이터
```csv
date,hour,temperature,rain_prob,rain_type
20230101,0000,-0.2,0.0,0.0
20230101,0100,0.6,0.0,0.0
20230101,0200,2.2,0.0,0.0
...
```

**컬럼 설명:**
- `date`: 날짜 (YYYYMMDD 형식)
- `hour`: 시간 (HHMM 형식, 0000~2300)
- `temperature`: 기온 (°C)
- `rain_prob`: 강수량 (mm)
- `rain_type`: 강수형태 (0=없음, 1=비, 2=진눈깨비, 3=눈 등)

### 일별 최저/최고 온도 (`daily_temp_202301_202512.csv`)
```csv
date,min_temp,max_temp
20230101,-6.9,3.2
20230102,-8.8,-0.5
20230103,-5.5,0.0
...
```

**컬럼 설명:**
- `date`: 날짜 (YYYYMMDD 형식)
- `min_temp`: 해당 일의 최저 기온 (°C, 소숫점 1자리)
- `max_temp`: 해당 일의 최고 기온 (°C, 소숫점 1자리)

---

## 💾 SQLite 데이터베이스 사용

> 📘 **상세 스키마 정보**: 전체 테이블 구조, 컬럼 설명, 샘플 쿼리는 [`DATABASE_SCHEMA.md`](DATABASE_SCHEMA.md)를 참조하세요.

### Python에서 사용

#### 시간별 데이터 조회
```python
import sqlite3
import pandas as pd

# 시간별 데이터베이스 연결
conn = sqlite3.connect('data/db/202301_202512.db')

# 전체 데이터 조회
df = pd.read_sql("SELECT * FROM weather_data", conn)

# 특정 날짜 조회
df = pd.read_sql("SELECT * FROM weather_data WHERE date = '20230101'", conn)

# 날짜별 평균 기온
df = pd.read_sql("""
    SELECT date, AVG(temperature) as avg_temp 
    FROM weather_data 
    GROUP BY date
""", conn)

conn.close()
```

#### 일별 최저/최고 온도 조회
```python
import sqlite3
import pandas as pd

# 일별 온도 데이터베이스 연결
conn = sqlite3.connect('data/db/daily_temp_202301_202512.db')

# 전체 일별 데이터 조회
df = pd.read_sql("SELECT * FROM daily_temperature", conn)

# 최저 온도가 영하인 날 조회
df = pd.read_sql("""
    SELECT * FROM daily_temperature 
    WHERE min_temp < 0
""", conn)

# 일교차가 큰 날 조회 (10도 이상)
df = pd.read_sql("""
    SELECT date, min_temp, max_temp, 
           (max_temp - min_temp) as temp_range
    FROM daily_temperature 
    WHERE (max_temp - min_temp) >= 10
    ORDER BY temp_range DESC
""", conn)

conn.close()
```

### SQL 쿼리 예시

#### 시간별 데이터 (weather_data 테이블)
```sql
-- 강수가 있었던 시간 조회
SELECT * FROM weather_data WHERE rain_prob > 0;

-- 특정 기간의 최고/최저 기온
SELECT date, MAX(temperature), MIN(temperature)
FROM weather_data
WHERE date BETWEEN '20230101' AND '20230131'
GROUP BY date;

-- 시간대별 평균 기온
SELECT hour, AVG(temperature) as avg_temp
FROM weather_data
GROUP BY hour
ORDER BY hour;
```

#### 일별 최저/최고 온도 (daily_temperature 테이블)
```sql
-- 전체 일별 데이터
SELECT * FROM daily_temperature;

-- 일교차가 가장 큰 날 Top 10
SELECT date, min_temp, max_temp, 
       (max_temp - min_temp) as temp_range
FROM daily_temperature
ORDER BY temp_range DESC
LIMIT 10;

-- 월별 평균 최저/최고 온도
SELECT 
    SUBSTR(date, 1, 6) as month,
    AVG(min_temp) as avg_min,
    AVG(max_temp) as avg_max
FROM daily_temperature
GROUP BY month;
```

---

## 🔄 재실행하기

새로운 데이터 파일을 추가하거나 업데이트한 경우:

1. `data/raw/` 폴더에 새 CSV 파일 추가
2. 파이프라인 재실행
```bash
cd modules
python3 main_pipeline.py
```

**주의:** 기존 출력 파일들은 자동으로 덮어쓰기됩니다.

---

## 📝 처리 과정

파이프라인은 다음 단계로 작동합니다:

1. **파일 스캔**: `data/raw/` 폴더의 모든 CSV 파일 검색
2. **데이터 타입별 그룹화**: 기온, 강수, 강수형태로 분류
3. **병합**: 같은 타입의 여러 기간 파일을 하나로 병합
4. **중복 제거**: 동일한 날짜/시간 데이터 제거
5. **통합 CSV 생성**: 모든 데이터를 하나의 파일로 통합 (시간별)
6. **SQLite DB 생성**: 시간별 데이터를 쿼리 가능한 데이터베이스로 저장
7. **일별 통계 생성**: 최저/최고 온도 CSV 및 DB 파일 생성

---

## 🛠️ 개별 모듈 사용

전체 파이프라인이 아닌 특정 기능만 사용하고 싶다면:

```python
# 특정 파일만 파싱
from data_parser import parse_csv_data
from pathlib import Path

df = parse_csv_data(Path("data/raw/기온_202301_202312.csv"), "202301")
print(df.head())

# 데이터베이스 쿼리만 실행
from database_handler import query_database
from pathlib import Path

results = query_database(
    Path("data/db/202301_202512.db"),
    "SELECT * FROM weather_data LIMIT 10"
)
```

---

## ❓ 문제 해결

### 오류: "No module named 'pandas'"
```bash
pip install pandas
```

### 오류: "파일을 찾을 수 없습니다"
- `data/raw/` 폴더에 CSV 파일이 있는지 확인
- 파일명이 `기온_YYYYMM_YYYYMM.csv` 형식인지 확인

### 데이터가 비어있음
- 원본 CSV 파일의 첫 줄이 헤더 형식인지 확인
- 데이터 형식이 `day, hour, value`인지 확인

---

## 📚 더 자세한 정보

각 모듈의 상세한 설명과 고급 사용법은 `README_MODULES.md`를 참조하세요.

---

## 📄 라이선스

MIT License

---

## 🎯 주요 특징

✅ 자동 날짜 범위 감지  
✅ 여러 파일 자동 병합  
✅ 중복 데이터 자동 제거  
✅ 시간순 정렬  
✅ SQLite 인덱스 자동 생성  
✅ UTF-8 인코딩 지원  
✅ 영문 컬럼명 (인코딩 문제 없음)  
✅ 일별 최저/최고 온도 자동 생성  

---

**Happy Data Processing! 🌤️**
