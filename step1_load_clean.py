# -*- coding: utf-8 -*-
"""
M1-1 시계열 분석 | STEP 1 : 데이터 불러오기 · 정제
기상청 ASOS 일자료(연도별 CSV 11개) → 하나로 합치고 품질을 점검한다.

[데이터 개수 산출 근거 — 집계 과정 요약]
  원본 11개 CSV 합계            374,340행
  − 2026년 자료 제외(9개월치)    25,591행
  − 중복(지점+날짜)                   0건
  ────────────────────────────────────────
  = 분석 대상                   348,749행   ← asos_2016_2025_clean.csv

  이 348,749행을 groupby("날짜").mean() 으로 일 단위 집계하면
  = 메인 시계열                   3,653개   ← nation_daily.csv
  3,653 = 2016-01-01 ~ 2025-12-31 의 날짜 수 (윤년 2016·2020·2024 포함)
        = 365×10 + 3 = 3,653  → 누락된 날짜가 없음을 이 식으로 확인한다.

  전국 평균은 "지점 간 동등 가중"(지점값의 단순평균)이다. 면적 가중이 아니다.
  지점 밀도가 높은 수도권의 과대 대표를 막기 위한 선택이며, 면적 자료가 없어
  가중평균은 계산할 수 없다. 두 방식의 차이는 0.07℃ 이내(step6_robustness.py ②).
"""
import glob, os
import pandas as pd

RAW = "data/raw"
OUT = "data/processed"
os.makedirs(OUT, exist_ok=True)

# ---------- 1. 연도별 CSV 11개를 하나로 합치기 ----------
files = sorted(glob.glob(os.path.join(RAW, "OBS_ASOS_DD_*.csv")))
print(f"[1] 발견한 CSV 파일: {len(files)}개")
frames = []
for f in files:
    d = pd.read_csv(f, encoding="cp949")
    frames.append(d)
    print(f"    - {os.path.basename(f):28s} {len(d):>7,}행")
df = pd.concat(frames, ignore_index=True)
print(f"    → 합친 결과: {len(df):,}행 × {df.shape[1]}열\n")

# ---------- 2. 컬럼명 정리 ----------
df = df.rename(columns={
    "지점": "지점번호", "지점명": "지점명", "일시": "날짜",
    "평균기온(°C)": "평균기온", "최저기온(°C)": "최저기온", "최고기온(°C)": "최고기온",
})
df = df[["지점번호", "지점명", "날짜", "평균기온", "최저기온", "최고기온"]]
print(f"[2] 사용할 열: {list(df.columns)}\n")

# ---------- 3. 날짜형 변환 + 기간 확정 ----------
df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")
print(f"[3] 날짜 변환 실패(NaT): {df['날짜'].isna().sum()}건")
before = len(df)
df = df[(df["날짜"] >= "2016-01-01") & (df["날짜"] <= "2025-12-31")]
print(f"    2016~2025로 한정: {before:,}행 → {len(df):,}행  (2026년 {before-len(df):,}행 제외)\n")

# ---------- 4. 중복 제거 ----------
dup = df.duplicated(subset=["지점번호", "날짜"]).sum()
df = df.drop_duplicates(subset=["지점번호", "날짜"])
print(f"[4] 중복(같은 지점·같은 날): {dup}건 제거 → {len(df):,}행\n")

# ---------- 5. 결측치 점검 ----------
print("[5] 결측치 현황")
miss = pd.DataFrame({
    "결측개수": df.isnull().sum(),
    "결측비율(%)": (df.isnull().mean() * 100).round(3),
})
print(miss.to_string())
print()

# ---------- 6. 기본 정보 ----------
print("[6] 데이터 개요")
print(f"    기간        : {df['날짜'].min().date()} ~ {df['날짜'].max().date()}")
print(f"    관측지점 수 : {df['지점번호'].nunique()}개")
print(f"    전체 행 수  : {len(df):,}행")
print()
print("[7] 기온 기초통계")
print(df[["평균기온", "최저기온", "최고기온"]].describe().round(2).to_string())
print()

# ---------- 8. 이상치(IQR) 점검 ----------
print("[8] 이상치 점검 (IQR 1.5배 기준)")
for col in ["평균기온", "최저기온", "최고기온"]:
    q1, q3 = df[col].quantile([0.25, 0.75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    n = ((df[col] < lo) | (df[col] > hi)).sum()
    print(f"    {col}: 정상범위 {lo:6.1f} ~ {hi:5.1f}℃ | 벗어난 값 {n:,}건 ({n/len(df)*100:.2f}%)")
print()

# ---------- 9. 전국 일별 평균 (메인 시계열) ----------
# 집계 규칙: 같은 날짜의 모든 지점 값을 단순평균한다(지점 간 동등 가중).
#   - mean()은 결측을 자동 제외하므로 결측 행을 지우지 않아도 된다.
#   - 관측지점수 열을 함께 남겨, 날짜별로 몇 개 지점이 집계됐는지 추적할 수 있게 한다.
#   - 결과 행 수는 반드시 3,653이어야 한다(위 주석의 검산식 참고).
nation = df.groupby("날짜").agg(
    전국평균기온=("평균기온", "mean"),
    전국최저기온=("최저기온", "mean"),
    전국최고기온=("최고기온", "mean"),
    관측지점수=("지점번호", "nunique"),
).round(2)
print(f"[9] 메인 시계열(전국 일별 평균) 생성: {len(nation):,}일")
expected = (pd.Timestamp("2025-12-31") - pd.Timestamp("2016-01-01")).days + 1
print(f"    검산: 기대 날짜 수 {expected:,}일 / 실제 {len(nation):,}일 "
      f"→ {'일치 (누락 없음)' if expected == len(nation) else '불일치 — 확인 필요'}")
print(nation.head(3).to_string())
print("    ...")
print(nation.tail(2).to_string())

df.to_csv(f"{OUT}/asos_2016_2025_clean.csv", index=False, encoding="utf-8-sig")
nation.to_csv(f"{OUT}/nation_daily.csv", encoding="utf-8-sig")
print(f"\n[저장 완료] {OUT}/asos_2016_2025_clean.csv , {OUT}/nation_daily.csv")
