# 기상 데이터 처리 파이프라인 - 모듈 설명서

## 📁 프로젝트 구조

```
weather_data_pipeline/
├── main_pipeline.py          # 메인 실행 파일
├── data_parser.py            # 데이터 파싱 모듈
├── data_merger.py            # 데이터 병합 모듈
├── data_saver.py             # 데이터 저장 모듈
├── database_handler.py       # 데이터베이스 관리 모듈
├── README_MODULES.md         # 이 문서
└── data/
    ├── raw/                  # 원본 데이터 (입력)
    ├── processed/            # 처리된 데이터 (출력)
    └── db/                   # SQLite DB (출력)
```

---

## 🔧 각 모듈 설명

### 1. `data_parser.py` - 데이터 파싱 모듈

**역할**: CSV 파일을 읽어서 pandas DataFrame으로 변환

**주요 함수**:

#### `parse_filename(filename: str) -> Tuple[str, str, str]`
파일명에서 정보를 추출합니다.

```python
from data_parser import parse_filename

filename = "기온_202301_202312.csv"
data_type, start, end = parse_filename(filename)
# 결과: ('기온', '202301', '202312')
```

#### `parse_csv_data(filepath: Path, start_date: str) -> pd.DataFrame`
CSV 파일을 DataFrame으로 변환합니다.

```python
from data_parser import parse_csv_data
from pathlib import Path

filepath = Path("data/raw/기온_202301_202312.csv")
df = parse_csv_data(filepath, "202301")
# 결과: datetime과 value 컬럼을 가진 DataFrame
```

**특징**:
- 파일 첫 줄(헤더) 자동 스킵
- day, hour, value를 datetime으로 변환
- 잘못된 데이터 자동 필터링

---

### 2. `data_merger.py` - 데이터 병합 모듈

**역할**: 여러 파일을 병합하고 중복 제거

**주요 함수**:

#### `get_file_groups(raw_dir: Path) -> Dict[str, List]`
raw 폴더의 파일들을 데이터 타입별로 그룹화합니다.

```python
from data_merger import get_file_groups
from pathlib import Path

raw_dir = Path("data/raw")
groups = get_file_groups(raw_dir)
# 결과: {'기온': [...], '강수': [...], '강수형태': [...]}
```

#### `merge_data_type(data_type: str, files: List) -> pd.DataFrame`
같은 타입의 파일들을 병합합니다.

```python
from data_merger import merge_data_type

files = [
    (Path("기온_202301_202312.csv"), "202301", "202312"),
    (Path("기온_202401_202412.csv"), "202401", "202412")
]
merged_df = merge_data_type("기온", files)
```

#### `merge_all_types(temp_df, precip_df, precip_type_df) -> pd.DataFrame`
기온, 강수, 강수형태를 하나로 통합합니다.

```python
from data_merger import merge_all_types

integrated_df = merge_all_types(temp_df, precip_df, precip_type_df)
# 결과: date, hour, temperature, rain_prob, rain_type 컬럼
```

**특징**:
- 시간순 자동 정렬
- 중복 데이터 자동 제거
- 여러 파일 자동 병합

---

### 3. `data_saver.py` - 데이터 저장 모듈

**역할**: 처리된 데이터를 CSV 파일로 저장

**주요 함수**:

#### `save_processed_csv(data_type, df, start_date, end_date, output_dir) -> Path`
원본 형식을 유지하여 CSV 저장합니다.

```python
from data_saver import save_processed_csv
from pathlib import Path

output_path = save_processed_csv(
    "기온", 
    df, 
    "202301", 
    "202512", 
    Path("data/processed")
)
# 저장: data/processed/기온_202301_202512.csv
```

#### `save_integrated_csv(df, start_date, end_date, output_dir) -> Path`
통합 CSV 파일을 저장합니다.

```python
from data_saver import save_integrated_csv

output_path = save_integrated_csv(
    integrated_df,
    "202301",
    "202512",
    Path("data/processed")
)
# 저장: data/processed/202301_202512.csv
```

**특징**:
- 원본 형식 유지 (day, hour, value)
- UTF-8 인코딩
- 자동 헤더 생성

---

### 4. `database_handler.py` - 데이터베이스 관리 모듈

**역할**: SQLite 데이터베이스 생성 및 관리

**주요 함수**:

#### `create_sqlite_db(df, start_date, end_date, db_dir) -> Path`
SQLite 데이터베이스를 생성합니다.

```python
from database_handler import create_sqlite_db
from pathlib import Path

db_path = create_sqlite_db(
    integrated_df,
    "202301",
    "202512",
    Path("data/db")
)
# 생성: data/db/202301_202512.db
```

#### `query_database(db_path, query) -> list`
데이터베이스에 쿼리를 실행합니다.

```python
from database_handler import query_database

results = query_database(
    db_path,
    "SELECT * FROM weather_data WHERE date = '20230101'"
)
```

#### `get_table_info(db_path) -> list`
테이블 구조 정보를 조회합니다.

```python
from database_handler import get_table_info

columns = get_table_info(db_path)
for col in columns:
    print(f"{col[1]} ({col[2]})")
```

**특징**:
- 자동 인덱스 생성 (date, hour)
- 기존 DB 자동 덮어쓰기
- weather_data 테이블 자동 생성

---

### 5. `main_pipeline.py` - 메인 파이프라인

**역할**: 모든 모듈을 통합하여 실행

**사용 방법**:

```bash
python3 main_pipeline.py
```

**클래스**:

#### `WeatherDataPipeline`
파이프라인 전체를 관리하는 메인 클래스

```python
from main_pipeline import WeatherDataPipeline

# 기본 경로로 초기화
pipeline = WeatherDataPipeline()

# 또는 커스텀 경로로 초기화
pipeline = WeatherDataPipeline(base_dir="/custom/path")

# 실행
pipeline.run()
```

**처리 단계**:
1. raw 폴더 파일 스캔
2. 데이터 타입별 병합
3. 통합 CSV 생성
4. SQLite DB 생성

---

## 🚀 사용 예시

### 기본 사용법

```bash
# 1. raw 폴더에 CSV 파일 넣기
cp *.csv data/raw/

# 2. 파이프라인 실행
python3 main_pipeline.py

# 3. 결과 확인
ls data/processed/  # CSV 파일들
ls data/db/         # SQLite DB
```

### 개별 모듈 사용

```python
# 특정 파일만 파싱하기
from data_parser import parse_csv_data
from pathlib import Path

df = parse_csv_data(Path("data/raw/기온_202301_202312.csv"), "202301")
print(df.head())
```

```python
# 데이터베이스 쿼리하기
from database_handler import query_database
from pathlib import Path

db_path = Path("data/db/202301_202512.db")
results = query_database(
    db_path,
    "SELECT date, AVG(temperature) as avg_temp FROM weather_data GROUP BY date LIMIT 10"
)
for row in results:
    print(row)
```

---

## 📊 데이터 흐름

```
[Raw CSV Files]
      ↓
[data_parser.py] ← 파일 파싱
      ↓
[data_merger.py] ← 데이터 병합
      ↓
   ┌──┴──┐
   ↓     ↓
[data_saver.py]  [database_handler.py]
   ↓                    ↓
[Processed CSV]    [SQLite DB]
```

---

## 🔍 커스터마이징

### 새로운 데이터 타입 추가

`data_merger.py`의 `get_file_groups()` 함수 수정:

```python
def get_file_groups(raw_dir: Path) -> Dict[str, List]:
    groups = {
        '기온': [], 
        '강수': [], 
        '강수형태': [],
        '습도': []  # 새로운 타입 추가
    }
    # ... 나머지 코드
```

### 다른 파일 형식 지원

`data_parser.py`의 `parse_filename()` 함수 수정:

```python
def parse_filename(filename: str) -> Tuple[str, str, str]:
    pattern = r'(기온|강수|강수형태|습도)_(\d{6})_(\d{6})\.csv'
    # ... 나머지 코드
```

---

## ⚠️ 주의사항

1. **파일명 형식**: 반드시 `데이터타입_YYYYMM_YYYYMM.csv` 형식 사용
2. **데이터 형식**: 첫 줄은 헤더, 이후 `day, hour, value` 형식
3. **인코딩**: UTF-8 인코딩 사용
4. **중복 데이터**: 같은 datetime의 데이터는 자동으로 제거됨

---

## 🐛 문제 해결

### ModuleNotFoundError
```bash
# 같은 디렉토리에서 실행하세요
cd /path/to/project
python3 main_pipeline.py
```

### pandas 설치 오류
```bash
pip install pandas
```

### 파일을 찾을 수 없음
```bash
# 디렉토리 구조 확인
ls -la data/raw/
```

---

## 📝 라이선스

MIT License

---

## 👨‍💻 개발자 정보

각 모듈은 독립적으로 사용할 수 있도록 설계되었습니다.
필요에 따라 개별 모듈만 import하여 사용 가능합니다.
