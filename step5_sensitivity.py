# -*- coding: utf-8 -*-
"""
M1-1 시계열 분석 | STEP 5 : 한계점 검증 — "10년은 짧다"를 수치로 확인
① 측정 방법(끝점 비교 vs 회귀)에 따라 상승폭이 얼마나 달라지는가
② 시작·끝 연도를 바꾸면 기울기가 얼마나 요동치는가
③ 기상청 113년 보고서와 동일한 6개 지점으로 맞춘 통제 비교
그래프는 만들지 않는다. REPORT.md 7-1 의 표를 그대로 출력한다.
"""
import pandas as pd
import numpy as np
from scipy import stats

KMA6 = ["서울", "인천", "대구", "부산", "목포", "강릉"]   # 기상청 113년 시계열 지점
KMA_RATE = 0.21          # 기상청 113년(1912~2024) 연평균기온 상승률 (℃/10년)
KMA_RECENT10 = 14.3      # 기상청 최근 10년(2015~2024) 연평균기온 (℃)


def slope_per_decade(series):
    """연 단위 시계열의 10년당 기울기와 p값"""
    r = stats.linregress(np.arange(len(series)), series.values)
    return r.slope * 10, r.pvalue, r.rvalue ** 2


df = pd.read_csv("data/processed/asos_2016_2025_clean.csv", parse_dates=["날짜"])
df["연"] = df["날짜"].dt.year
nat = pd.read_csv("data/processed/nation_daily.csv", parse_dates=["날짜"]).set_index("날짜")

# 지점 평균 → 연평균 (전 지점 / 6개 지점)
yr_all = df.groupby(["연", "지점번호"])["평균기온"].mean().groupby("연").mean()
yr_6 = (df[df["지점명"].isin(KMA6)]
        .groupby(["연", "지점명"])["평균기온"].mean().groupby("연").mean())

print("=" * 66)
print("① 측정 방법에 따른 10년 상승폭")
print("=" * 66)
ma365 = nat["전국평균기온"].rolling(365, min_periods=365).mean().dropna()
print(f"  365일 이동평균 끝점 비교 : {ma365.iloc[0]:.2f}℃ → {ma365.iloc[-1]:.2f}℃  "
      f"({ma365.iloc[-1] - ma365.iloc[0]:+.2f}℃)")
s, p, r2 = slope_per_decade(yr_all)
print(f"  연평균 단순선형회귀      : {s:+.2f}℃/10년  (p={p:.3f}, R²={r2:.3f})")
print("  → 같은 데이터인데 측정 방법만 바꿔도 약 3배 차이가 난다")

print()
print("=" * 66)
print("② 구간 민감도 — 시작·끝 연도를 바꾸면")
print("=" * 66)
print(f"  {'구간':<14}{'기울기':>14}{'p값':>10}   유의성")
rows = [(2016, e) for e in (2022, 2023, 2024, 2025)] + [(2020, 2025)]
for a, b in rows:
    sub = yr_all.loc[a:b]
    s, p, _ = slope_per_decade(sub)
    print(f"  {a}~{b} (n={len(sub):2d}) {s:+9.2f}℃/10년 {p:9.3f}   "
          f"{'유의' if p < 0.05 else '무의미'}")
lo = min(slope_per_decade(yr_all.loc[a:b])[0] for a, b in rows)
hi = max(slope_per_decade(yr_all.loc[a:b])[0] for a, b in rows)
print(f"  → 범위 {lo:+.2f} ~ {hi:+.2f}℃/10년")

print()
print("=" * 66)
print("③ 통제 비교 — 기상청과 동일한 6개 지점으로 맞추면")
print("=" * 66)
s6, p6, _ = slope_per_decade(yr_6)
sa, pa, _ = slope_per_decade(yr_all)
print(f"  기상청 113년(1912~2024, 6지점) : 최근10년 {KMA_RECENT10:.1f}℃ | {KMA_RATE:+.2f}℃/10년")
print(f"  본 분석(2016~2025, 동일 6지점) : 10년평균 {yr_6.mean():.2f}℃ | {s6:+.2f}℃/10년 (p={p6:.3f})")
print(f"  본 분석(2016~2025, 전체 98지점): 10년평균 {yr_all.mean():.2f}℃ | {sa:+.2f}℃/10년 (p={pa:.3f})")
print()
print(f"  평균기온 차이 : {abs(yr_6.mean() - KMA_RECENT10):.2f}℃  → 데이터 정합성 확인")
print(f"  기울기 배율   : {s6 / KMA_RATE:.1f}배  → 지점을 맞춰도 남는 차이 = 기간 길이 때문")
print()
print("  ※ 주의 : 시계열 회귀의 p값은 잔차 자기상관을 검정하지 않았으므로")
print("           실제 유의성은 표시된 값보다 낮을 수 있다.")

# =====================================================================
# ④ 인사이트 해석 검증 — 초안의 주장이 데이터로 성립하는지 확인
# =====================================================================
print()
print("=" * 66)
print("④ 인사이트 해석 검증")
print("=" * 66)

df["폭염"] = (df["최고기온"] >= 33).astype(int)
df["열대야"] = (df["최저기온"] >= 25).astype(int)
ext = df.groupby(["연", "지점번호"])[["폭염", "열대야"]].sum().groupby("연").mean()

print("  [인사이트 3] \"열대야가 폭염보다 빠르게 는다\" — 전국 기준 검증")
for c in ["폭염", "열대야"]:
    s = ext[c]
    r = stats.linregress(np.arange(len(s)), s.values)
    print(f"    {c:4s}: {s.iloc[0]:5.1f}일 → {s.iloc[-1]:5.1f}일 | "
          f"{r.slope*10:+.1f}일/10년 (p={r.pvalue:.3f}) "
          f"{'유의' if r.pvalue < 0.05 else '무의미'}")
cw = df[df["지점명"] == "창원"].groupby("연")[["폭염", "열대야"]].sum()
print("    창원  : 연도별 — 기준 연도에 따라 배율이 달라지므로 3개 연도를 함께 본다")
for yy in (2016, 2024, 2025):
    print(f"            {yy}년  폭염 {cw.loc[yy,'폭염']:>2.0f}일 · 열대야 {cw.loc[yy,'열대야']:>2.0f}일")
print(f"            2016→2024(최다해) 폭염 {cw.loc[2024,'폭염']/cw.loc[2016,'폭염']:.1f}배 · "
      f"열대야 {cw.loc[2024,'열대야']/cw.loc[2016,'열대야']:.1f}배")
print(f"            2016→2025        폭염 {cw.loc[2025,'폭염']/cw.loc[2016,'폭염']:.1f}배 · "
      f"열대야 {cw.loc[2025,'열대야']/cw.loc[2016,'열대야']:.1f}배")
print("    → 전국에서는 두 지표의 증가 속도가 비슷하다. 창원 한정 현상으로 범위를 좁혀야 하며,")
print("       '3배'는 최다 연도(2024)를 끝점으로 잡았을 때의 값이라는 점을 함께 밝혀야 한다.")

print()
print("  [인사이트 4] \"지역별 최대 4.7배 차이\" — 회귀로 재계산")
REGIONS = ["강릉", "서울", "창원", "제주", "대구", "부산"]
endpoint, slope = {}, {}
for rg in REGIONS:
    y = df[df["지점명"] == rg].groupby("연")["평균기온"].mean()
    lr = stats.linregress(np.arange(len(y)), y.values)
    endpoint[rg] = y.iloc[-1] - y.iloc[0]
    slope[rg] = lr.slope * 10
    print(f"    {rg:3s}: 끝점 {endpoint[rg]:+.2f}℃ | 회귀 {slope[rg]:+.2f}℃/10년 (p={lr.pvalue:.3f})")
print(f"    → 배율: 끝점 비교 {max(endpoint.values())/min(endpoint.values()):.1f}배 "
      f"vs 회귀 {max(slope.values())/min(slope.values()):.1f}배")
print("    → 배율은 측정 방법에 좌우된다. 순서(강릉 최고 · 부산 최저)만 유지된다.")
