# Database Schema Documentation

## 📊 데이터베이스 개요

이 프로젝트는 두 개의 SQLite 데이터베이스 파일을 생성합니다:
1. **시간별 기상 데이터** (`202301_202512.db`)
2. **일별 최저/최고 온도** (`daily_temp_202301_202512.db`)

---

## 🗄️ Database 1: 시간별 기상 데이터

**파일명:** `202301_202512.db`  
**위치:** `data/db/202301_202512.db`

### 테이블: `weather_data`

시간별 기온, 강수량, 강수형태 데이터를 저장합니다.

#### 스키마

| 컬럼명 | 데이터 타입 | 설명 | 예시 |
|--------|------------|------|------|
| `date` | TEXT | 날짜 (YYYYMMDD 형식) | 20230101 |
| `hour` | TEXT | 시간 (HHMM 형식, 24시간제) | 0000, 1300, 2300 |
| `temperature` | REAL | 기온 (섭씨, °C) | -5.2, 15.3, 28.7 |
| `rain_prob` | REAL | 강수량 (mm) | 0.0, 2.5, 15.3 |
| `rain_type` | REAL | 강수형태 코드 | 0.0, 1.0, 3.0 |

#### 강수형태 코드

| 코드 | 의미 |
|------|------|
| 0 | 없음 |
| 1 | 비 |
| 2 | 진눈깨비 |
| 3 | 눈 |

#### 인덱스

- **`idx_date_hour`**: (date, hour) 복합 인덱스
  - 특정 날짜/시간 조회 최적화
  
#### 데이터 범위

- **기간:** 2023-01-01 00:00 ~ 2025-12-31 23:00
- **총 레코드:** 약 26,304개 (1,096일 × 24시간)
- **파일 크기:** 약 128KB

#### 샘플 쿼리

```sql
-- 특정 날짜의 모든 시간별 데이터
SELECT * FROM weather_data 
WHERE date = '20230101' 
ORDER BY hour;

-- 특정 시간대의 평균 기온
SELECT hour, AVG(temperature) as avg_temp
FROM weather_data
GROUP BY hour
ORDER BY hour;

-- 강수가 있었던 모든 기록
SELECT date, hour, temperature, rain_prob, rain_type
FROM weather_data
WHERE rain_prob > 0
ORDER BY date, hour;

-- 날짜별 최고/최저 기온
SELECT date, 
       MAX(temperature) as max_temp,
       MIN(temperature) as min_temp
FROM weather_data
GROUP BY date
ORDER BY date;

-- 특정 기간의 평균 기온
SELECT AVG(temperature) as avg_temp
FROM weather_data
WHERE date BETWEEN '20230101' AND '20230131';

-- 기온이 영하인 시간대
SELECT date, hour, temperature
FROM weather_data
WHERE temperature < 0
ORDER BY temperature ASC;
```

---

## 🗄️ Database 2: 일별 최저/최고 온도

**파일명:** `daily_temp_202301_202512.db`  
**위치:** `data/db/daily_temp_202301_202512.db`

### 테이블: `daily_temperature`

일별 최저 기온과 최고 기온을 저장합니다.

#### 스키마

| 컬럼명 | 데이터 타입 | 설명 | 예시 |
|--------|------------|------|------|
| `date` | INTEGER | 날짜 (YYYYMMDD 형식) | 20230101 |
| `min_temp` | REAL | 해당 일의 최저 기온 (°C, 소숫점 1자리) | -6.9, 0.5, 15.3 |
| `max_temp` | REAL | 해당 일의 최고 기온 (°C, 소숫점 1자리) | 3.2, 12.5, 28.7 |

#### 인덱스

- **`idx_date`**: date 단일 인덱스
  - 날짜 기반 조회 최적화

#### 데이터 범위

- **기간:** 2023-01-01 ~ 2025-12-31
- **총 레코드:** 1,096개 (3년간의 일별 데이터)
  - 2023년: 365일
  - 2024년: 366일 (윤년)
  - 2025년: 365일
- **파일 크기:** 약 12KB

#### 샘플 쿼리

```sql
-- 특정 날짜의 최저/최고 기온
SELECT * FROM daily_temperature 
WHERE date = 20230101;

-- 일교차가 큰 날 Top 10
SELECT date, min_temp, max_temp,
       (max_temp - min_temp) as temp_range
FROM daily_temperature
ORDER BY temp_range DESC
LIMIT 10;

-- 최저 기온이 영하인 날
SELECT date, min_temp, max_temp
FROM daily_temperature
WHERE min_temp < 0
ORDER BY min_temp ASC;

-- 월별 평균 최저/최고 기온
SELECT 
    SUBSTR(CAST(date AS TEXT), 1, 6) as month,
    AVG(min_temp) as avg_min_temp,
    AVG(max_temp) as avg_max_temp
FROM daily_temperature
GROUP BY month
ORDER BY month;

-- 연도별 평균 기온
SELECT 
    SUBSTR(CAST(date AS TEXT), 1, 4) as year,
    AVG(min_temp) as avg_min_temp,
    AVG(max_temp) as avg_max_temp,
    AVG((min_temp + max_temp) / 2) as avg_temp
FROM daily_temperature
GROUP BY year;

-- 특정 기간의 통계
SELECT 
    COUNT(*) as days,
    MIN(min_temp) as lowest_temp,
    MAX(max_temp) as highest_temp,
    AVG(min_temp) as avg_min,
    AVG(max_temp) as avg_max
FROM daily_temperature
WHERE date BETWEEN 20230101 AND 20231231;

-- 폭염일 찾기 (최고기온 33도 이상)
SELECT date, min_temp, max_temp
FROM daily_temperature
WHERE max_temp >= 33.0
ORDER BY max_temp DESC;

-- 한파일 찾기 (최저기온 -15도 이하)
SELECT date, min_temp, max_temp
FROM daily_temperature
WHERE min_temp <= -15.0
ORDER BY min_temp ASC;
```

---

## 🔗 두 데이터베이스 간 관계

### 데이터 흐름

```
시간별 데이터 (weather_data)
         ↓
    일별 집계 (GROUP BY date)
         ↓
일별 최저/최고 (daily_temperature)
```

### 조인 예시

두 데이터베이스를 동시에 사용하려면 ATTACH 명령을 사용:

```sql
-- daily_temp DB에서 시작
ATTACH DATABASE 'data/db/202301_202512.db' AS hourly;

-- 일교차가 큰 날의 시간별 온도 변화 조회
SELECT h.date, h.hour, h.temperature, 
       d.min_temp, d.max_temp,
       (d.max_temp - d.min_temp) as temp_range
FROM hourly.weather_data h
JOIN daily_temperature d ON h.date = CAST(d.date AS TEXT)
WHERE (d.max_temp - d.min_temp) >= 15.0
ORDER BY h.date, h.hour;
```

---

## 💡 Python 사용 예시

### 시간별 데이터 조회

```python
import sqlite3
import pandas as pd

# 연결
conn = sqlite3.connect('data/db/202301_202512.db')

# 특정 날짜 조회
df = pd.read_sql("""
    SELECT * FROM weather_data 
    WHERE date = '20230101'
    ORDER BY hour
""", conn)

# 날짜별 평균 기온
daily_avg = pd.read_sql("""
    SELECT date, AVG(temperature) as avg_temp
    FROM weather_data
    GROUP BY date
""", conn)

conn.close()
```

### 일별 데이터 조회

```python
import sqlite3
import pandas as pd

# 연결
conn = sqlite3.connect('data/db/daily_temp_202301_202512.db')

# 전체 데이터 로드
df = pd.read_sql("SELECT * FROM daily_temperature", conn)

# 일교차 계산
df['temp_range'] = df['max_temp'] - df['min_temp']

# 월별 평균
df['month'] = df['date'].astype(str).str[:6]
monthly = df.groupby('month').agg({
    'min_temp': 'mean',
    'max_temp': 'mean',
    'temp_range': 'mean'
})

conn.close()
```

---

## 📈 데이터 품질

### 데이터 특성

- **완전성**: 모든 날짜/시간에 대한 데이터 포함
- **정확도**: 소숫점 1자리까지 반올림 (일별 데이터)
- **일관성**: 시간별 데이터에서 일별 통계가 자동 계산됨

### 이상치

데이터에 다음과 같은 이상치가 포함될 수 있습니다:
- 극단적인 저온 (예: -50°C)
- 결측값 표시 (-1.0 등)

분석 시 이러한 값들을 필터링해야 할 수 있습니다:

```sql
-- 정상 범위 데이터만 조회 (-30°C ~ 40°C)
SELECT * FROM weather_data
WHERE temperature BETWEEN -30 AND 40;
```

---

## 🛠️ 데이터베이스 유지보수

### 백업

```bash
# SQLite DB 백업
cp data/db/202301_202512.db data/db/backup_202301_202512.db
```

### 최적화

```sql
-- 데이터베이스 최적화 (VACUUM)
VACUUM;

-- 통계 업데이트
ANALYZE;
```

### 무결성 검사

```sql
-- 무결성 체크
PRAGMA integrity_check;
```

---

## 📝 참고사항

1. **날짜 형식**: 
   - `weather_data`: TEXT 타입 (문자열 비교)
   - `daily_temperature`: INTEGER 타입 (숫자 비교)

2. **시간대**: 모든 시간은 24시간 형식 (0000~2300)

3. **NULL 값**: 이 데이터셋에는 NULL 값이 없으며, 결측은 -1.0 등의 특수 값으로 표시

4. **인코딩**: UTF-8 인코딩 사용

---

**문서 버전**: 1.0  
**최종 업데이트**: 2026-01-12
