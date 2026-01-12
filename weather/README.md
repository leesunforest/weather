# 기상 데이터 처리 파이프라인

## 빠른 시작

### 1. 필수 라이브러리 설치
이 프로그램은 **pandas**만 필요합니다.

```bash
# pandas 설치
pip install pandas
```

**참고:** `sqlite3`는 Python 기본 라이브러리이므로 별도 설치 불필요

### 2. 데이터 준비
`data/raw/` 폴더에 CSV 파일을 넣으세요:
- `기온_YYYYMM_YYYYMM.csv`
- `강수_YYYYMM_YYYYMM.csv`
- `강수형태_YYYYMM_YYYYMM.csv`

### 3. 실행
```bash
cd modules
python3 main_pipeline.py
```

### 4. 결과 확인
- `data/processed/` - 병합된 CSV 파일들
- `data/db/` - SQLite 데이터베이스

## 📁 프로젝트 구조

```
.
├── QUICK_START.md            # 빠른 시작 가이드
├── README.md                 # 이 파일
├── README_MODULES.md         # 상세한 모듈 설명서
├── modules/                  # Python 모듈들
│   ├── main_pipeline.py      # 메인 실행 파일
│   ├── data_parser.py        # 파싱 모듈
│   ├── data_merger.py        # 병합 모듈
│   ├── data_saver.py         # 저장 모듈
│   ├── database_handler.py   # DB 관리 모듈
│   └── daily_stats.py        # 일별 통계 모듈
└── data/
    ├── raw/                  # 원본 데이터 (입력)
    ├── processed/            # 처리된 데이터 (출력)
    └── db/                   # SQLite DB (출력)
```

## 🔧 모듈 설명

### `data_parser.py`
- CSV 파일을 DataFrame으로 변환
- 파일명에서 정보 추출

### `data_merger.py`
- 여러 파일을 병합
- 중복 데이터 제거
- 데이터 타입별 그룹화

### `data_saver.py`
- 처리된 데이터를 CSV로 저장
- 원본 형식 유지

### `database_handler.py`
- SQLite 데이터베이스 생성
- 쿼리 실행 지원

### `daily_stats.py`
- 일별 최저/최고 온도 생성
- 시간별 데이터에서 통계 추출

### `main_pipeline.py`
- 모든 모듈을 통합
- 전체 파이프라인 실행

## 📊 출력 예시

### 통합 CSV (`202301_202512.csv`) - 시간별
| date | hour | temperature | rain_prob | rain_type |
|------|------|-------------|-----------|-----------|
| 20230101 | 0000 | -0.2 | 0.0 | 0.0 |
| 20230101 | 0100 | 0.6 | 0.0 | 0.0 |

### 일별 통계 (`daily_temp_202301_202512.csv`)
| date | min_temp | max_temp |
|------|----------|----------|
| 20230101 | -6.9 | 3.2 |
| 20230102 | -8.8 | -0.5 |

### SQLite DB 쿼리 예시
```python
import sqlite3

conn = sqlite3.connect('data/db/202301_202512.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM weather_data WHERE date = '20230101'")
results = cursor.fetchall()
```

## 📖 더 자세한 정보

모듈별 상세 설명은 `README_MODULES.md`를 참조하세요.

## 🛠️ 개별 모듈 사용

```python
# 특정 파일만 파싱
from data_parser import parse_csv_data
df = parse_csv_data("data/raw/기온_202301_202312.csv", "202301")

# 데이터베이스 쿼리
from database_handler import query_database
results = query_database(db_path, "SELECT * FROM weather_data LIMIT 10")
```

## ⚙️ 커스터마이징

필요에 따라 개별 모듈을 수정하여 사용할 수 있습니다.
각 모듈은 독립적으로 작동하도록 설계되었습니다.

## 라이선스

MIT License
