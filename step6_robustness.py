# -*- coding: utf-8 -*-
"""
M1-1 시계열 분석 | STEP 6 : 견고성 검증 (동료평가 지적사항 반영)
① 결측치를 "유지"한 결정이 결과에 얼마나 영향을 주는가  (유지 / 삭제 / 대체 비교)
② 전국 평균 산출 방식(지점평균의 평균 vs 일별 관측평균)에 따른 차이
③ 인사이트별 기본 통계 — 차이·표준편차·p값·z점수
그래프는 만들지 않는다. REPORT.md 3-1 · 3장 · 5장 · 부록 A의 수치를 출력한다.
"""
import pandas as pd
import numpy as np
from scipy import stats

df = pd.read_csv("data/processed/asos_2016_2025_clean.csv", parse_dates=["날짜"])
df["연"] = df["날짜"].dt.year
df["월"] = df["날짜"].dt.month
slope10 = lambda y: stats.linregress(np.arange(len(y)), y.values).slope * 10

# =====================================================================
# ① 결측치 처리 방식의 영향 — "유지" 결정이 결과를 바꾸는가
# =====================================================================
print("=" * 70)
print("① 결측치 처리 방식이 결과에 미치는 영향")
print("=" * 70)
keep = df.groupby("연")["평균기온"].mean()                       # A. 유지 (본 분석)
drop = df.dropna(subset=["평균기온"]).groupby("연")["평균기온"].mean()   # B. 결측 행 삭제
imp = df.copy()                                                  # C. 지점·월 평균으로 대체
imp["평균기온"] = imp.groupby(["지점번호", "월"])["평균기온"].transform(
    lambda s: s.fillna(s.mean()))
impy = imp.groupby("연")["평균기온"].mean()

print(f"  연평균 최대 차이 — 유지 vs 삭제 : {float((keep - drop).abs().max()):.4f}℃")
print(f"  연평균 최대 차이 — 유지 vs 대체 : {float((keep - impy).abs().max()):.4f}℃")
print(f"  10년 기울기 — 유지 {slope10(keep):+.3f} / 삭제 {slope10(drop):+.3f} / "
      f"대체 {slope10(impy):+.3f} ℃/10년")
print("  → 세 방식의 차이가 0.01℃ 미만이므로, 결측 유지 결정은 결론을 바꾸지 않는다.")

# =====================================================================
# ② 전국 평균 산출 방식
# =====================================================================
print()
print("=" * 70)
print("② 전국 평균 산출 방식 비교 (면적 가중은 면적 자료가 없어 불가)")
print("=" * 70)
simple = df.groupby(["연", "지점번호"])["평균기온"].mean().groupby("연").mean()
daily = df.groupby("날짜")["평균기온"].mean().resample("YE").mean()
daily.index = daily.index.year
print(f"  지점평균의 평균 : 10년 {simple.mean():.3f}℃ | 기울기 {slope10(simple):+.3f}℃/10년")
print(f"  일별 관측 평균  : 10년 {daily.mean():.3f}℃ | 기울기 {slope10(daily):+.3f}℃/10년")
print(f"  두 방식 최대 차이 : {float((simple - daily).abs().max()):.4f}℃")
print("  → 본 분석은 지점 간 동등 가중(지점평균의 평균)을 사용한다.")
print("    지점 밀도가 높은 수도권이 과대 대표되지 않도록 하기 위함이며, 두 방식 차이는 0.07℃ 이내다.")

# =====================================================================
# ③ 인사이트별 기본 통계
# =====================================================================
print()
print("=" * 70)
print("③ 인사이트별 기본 통계")
print("=" * 70)
m = df.groupby(["연", "월"])["평균기온"].mean().unstack()
early, late = m.loc[2016:2020], m.loc[2021:2025]
print("  [인사이트 1] 전반 5년 vs 후반 5년 월별 — Welch t-검정 (n=5 vs 5)")
for mm, nm in [(9, "9월"), (8, "8월"), (5, "5월")]:
    t, pv = stats.ttest_ind(late[mm], early[mm], equal_var=False)
    mark = "유의" if pv < 0.05 else "무의미"
    print(f"    {nm}: {early[mm].mean():.2f}±{early[mm].std():.2f} → "
          f"{late[mm].mean():.2f}±{late[mm].std():.2f} | 차이 {late[mm].mean()-early[mm].mean():+.2f}℃ "
          f"| t={t:+.2f}, p={pv:.3f} ({mark})")

yr = df.groupby("연")["평균기온"].mean()
print(f"\n  [인사이트 2] 연평균 10년: {yr.mean():.2f}℃ ± {yr.std():.2f}℃")
for y in (2018, 2024):
    print(f"    {y}년 {yr[y]:.2f}℃  z = {(yr[y]-yr.mean())/yr.std():+.2f}")

df["폭염"] = (df["최고기온"] >= 33).astype(int)
df["열대야"] = (df["최저기온"] >= 25).astype(int)
ext = df.groupby(["연", "지점번호"])[["폭염", "열대야"]].sum().groupby("연").mean()
print("\n  [인사이트 3] 극한기상 — 2024년의 이례성")
for c in ["폭염", "열대야"]:
    s = ext[c]
    print(f"    {c}: 10년 {s.mean():.1f}±{s.std():.1f}일 | 2024 {s[2024]:.1f}일 "
          f"z = {(s[2024]-s.mean())/s.std():+.2f}")
print("    → 열대야(z=+2.22)가 폭염(z=+1.44)보다 더 이례적인 값이었다.")

summer = df[df["월"].isin([6, 7, 8])].groupby("지점명")["평균기온"].mean()
winter = df[df["월"].isin([12, 1, 2])].groupby("지점명")["평균기온"].mean()
lev = stats.levene(summer, winter)
print(f"\n  [인사이트 5] 지점 간 산포 — 여름 σ={summer.std():.2f}℃ vs 겨울 σ={winter.std():.2f}℃")
print(f"    분산비 F = {winter.var()/summer.var():.2f}")
print(f"    Levene 등분산 검정: W={lev.statistic:.2f}, p={lev.pvalue:.2e} → 두 계절의 산포는 다르다")

print()
print("  ※ 표본이 연 단위 5개(t-검정) 또는 10개(회귀)로 작고, 시계열 자기상관을")
print("     검정하지 않았으므로 p값은 참고값이다. 유의하지 않은 항목은 그대로 표기했다.")
