# M1-1 시계열 데이터 분석 — 전국 기온 변화 (2016~2025)

Codyssey AI 네이티브 과정 · M1-1 개인과제

## 분석 개요

- **주제**: 전국 98개 관측지점의 일별 기온 10년 추이 — 추세 · 계절성 · 폭염/열대야 · 지역 비교 · 지역별 연교차
- **보너스**: 시계열 분해(추세/계절성/잔차) + 베이스라인 예측
- **한계점 검증**: 기간 민감도 분석 · 기상청 113년 관측과의 동일 지점 통제 비교
- **데이터**: 기상청 기상자료개방포털 종관기상관측(ASOS) 일자료
- **기간**: 2016-01-01 ~ 2025-12-31 (3,653일 · 완전한 10개 연도)
- **분석 행 수**: 348,749행 / 메인 시계열 3,653개

👉 **분석 결과는 [REPORT.md](REPORT.md) 를 보세요.**

## 폴더 구조

```
m1-1-weather-analysis/
├── data/
│   ├── raw/          기상청 원본 CSV 11개 (연도별)
│   └── processed/    정제 결과 — git 제외, 아래 실행으로 재생성
├── images/           분석 결과 그래프 7장 (png)
├── step1_load_clean.py   병합 · 정제
├── step2_visualize.py    그래프 4장 생성
├── step3_bonus.py        보너스 — 시계열 분해 · 베이스라인 예측
├── step4_regional_range.py  지역별 연교차 분석
├── step5_sensitivity.py  한계점 검증 — 기간 민감도 · 기상청 통제비교
├── requirements.txt
├── REPORT.md         분석 리포트
└── README.md         이 파일
```

> `data/processed/` 는 원본에서 자동 생성되는 중간 산출물(약 13MB)이라 저장소에 포함하지 않았습니다.
> `step1_load_clean.py` 를 실행하면 동일하게 재생성됩니다.

## 실행 방법

```bash
pip install -r requirements.txt
python step1_load_clean.py      # data/raw → data/processed 생성
python step2_visualize.py       # images/ 에 그래프 4장 생성
python step3_bonus.py           # 보너스 그래프 2장 생성 (statsmodels 필요)
python step4_regional_range.py  # 지역별 연교차 그래프 1장 생성
python step5_sensitivity.py     # 한계점 검증 수치 출력 (scipy 필요)
```

### 실행 환경
```
Python 3.10.12
pandas==2.3.3 · numpy==2.2.6 · matplotlib==3.10.9
statsmodels>=0.14 (step3_bonus.py) · scipy>=1.11 (step5_sensitivity.py)
```

## 데이터 출처 및 라이선스

- 출처: 기상청 기상자료개방포털 <https://data.kma.go.kr>
- 수집 경로: 데이터 › 기상관측 › 지상 › 종관기상관측(ASOS) › 일 자료
- 이용 허락: **공공저작물 출처표시 (제1유형)** — 무료, 출처 명시 조건
- ※ 일 자료는 1회 조회 최대 10년 제한이 있어 연도별로 나누어 내려받았습니다.

---
📘 CandyAflex AI·Digital Instructor | 손애희
silverhealthleader@gmail.com · blog.naver.com/wholebodyegoodballro
