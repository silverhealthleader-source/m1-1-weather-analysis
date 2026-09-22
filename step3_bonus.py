# -*- coding: utf-8 -*-
"""
M1-1 시계열 분석 | STEP 3 : 보너스 — 시계열 심화
(A) 시계열 분해 : 월평균 기온을 추세 · 계절성 · 잔차로 분리
(B) 간단 예측  : 베이스라인 2종으로 2025년 백테스트 후 2026년 예측
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose

# ---------- 한글 폰트 ----------
def set_korean_font():
    import glob
    names = {f.name for f in fm.fontManager.ttflist}
    for c in ["Malgun Gothic", "NanumGothic", "NanumBarunGothic", "AppleGothic",
              "Noto Sans CJK KR", "Noto Sans KR", "Noto Sans CJK JP"]:
        if c in names:
            plt.rc("font", family=c); return c
    for pat in [r"C:\Windows\Fonts\malgun.ttf",
                "/usr/share/fonts/**/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/**/*Nanum*.ttf"]:
        for p in glob.glob(pat, recursive=True):
            try:
                fm.fontManager.addfont(p)
                nm = fm.FontProperties(fname=p).get_name()
                plt.rc("font", family=nm); return nm
            except Exception:
                pass
    return None

print(f"[폰트] {set_korean_font()} 적용")
plt.rc("axes", unicode_minus=False)

INK, MUTED, GRID = "#1F2933", "#6B7785", "#DDE3E8"
BLUE, PINK, TEAL, AMBER = "#0072B2", "#C2185B", "#00897B", "#9A7D0A"
SURF = "#FCFCFB"
IMG = "images"; os.makedirs(IMG, exist_ok=True)

def style(ax):
    ax.set_facecolor(SURF)
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    for s in ("left", "bottom"): ax.spines[s].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=9.5)
    ax.title.set_color(INK)

def save(fig, name):
    fig.patch.set_facecolor(SURF); fig.tight_layout()
    fig.savefig(f"{IMG}/{name}", dpi=150, bbox_inches="tight", facecolor=SURF)
    plt.close(fig); print(f"[저장] {IMG}/{name}")

# ---------- 데이터 : 전국 월평균 기온 ----------
nat = pd.read_csv("data/processed/nation_daily.csv", parse_dates=["날짜"]).set_index("날짜")
월 = nat["전국평균기온"].resample("ME").mean().round(2)
월.index = 월.index.to_period("M").to_timestamp()      # 월초로 정렬
print(f"\n월평균 시계열: {len(월)}개월 ({월.index.min():%Y-%m} ~ {월.index.max():%Y-%m})")

# =====================================================================
# (A) 시계열 분해
# =====================================================================
res = seasonal_decompose(월, model="additive", period=12)

fig, axes = plt.subplots(4, 1, figsize=(12.5, 10), sharex=True)
parts = [
    (월,            "① 원본 (Observed) — 월평균 기온",                 BLUE),
    (res.trend,     "② 추세 (Trend) — 계절성을 걷어낸 장기 흐름",       PINK),
    (res.seasonal,  "③ 계절성 (Seasonal) — 매년 반복되는 성분",         TEAL),
    (res.resid,     "④ 잔차 (Residual) — 추세·계절성으로 설명 안 되는 부분", AMBER),
]
for ax, (s, t, c) in zip(axes, parts):
    style(ax)
    if t.startswith("④"):
        ax.axhline(0, color=GRID, lw=1, zorder=1)
        ax.scatter(s.index, s.values, s=9, color=c, zorder=3)
    else:
        ax.plot(s.index, s.values, color=c, lw=1.8, zorder=3)
    ax.set_title(t, fontsize=12.5, fontweight="bold", loc="left", pad=7)
    ax.set_ylabel("℃", color=MUTED, fontsize=10)

tr = res.trend.dropna()
axes[1].annotate(f"{tr.iloc[0]:.2f}℃ → {tr.iloc[-1]:.2f}℃  ({tr.iloc[-1]-tr.iloc[0]:+.2f}℃)",
                 xy=(0.99, 0.08), xycoords="axes fraction", ha="right",
                 fontsize=10.5, color=PINK, fontweight="bold")
fig.suptitle("전국 월평균 기온의 시계열 분해 (2016~2025, 가법 모형·주기 12개월)",
             fontsize=15, fontweight="bold", color=INK, y=1.005)
save(fig, "05_decomposition.png")

계절폭 = res.seasonal.max() - res.seasonal.min()
잔차표준편차 = res.resid.std()
설명력 = 1 - res.resid.var() / 월.var()

# =====================================================================
# (B) 간단 예측 — 베이스라인 2종
# =====================================================================
train = 월[월.index.year <= 2024]
test  = 월[월.index.year == 2025]

# 베이스라인 1 : 계절 나이브 — 작년 같은 달 값
naive = train[train.index.year == 2024].values

# 베이스라인 2 : 최근 5년 같은 달 평균 (2020~2024)
recent = train[train.index.year >= 2020]
clim = recent.groupby(recent.index.month).mean().values

mae = lambda a, b: float(np.mean(np.abs(np.asarray(a) - np.asarray(b))))
mae_naive, mae_clim = mae(test.values, naive), mae(test.values, clim)
best_name, best_vals = ("계절 나이브", naive) if mae_naive < mae_clim else ("최근 5년 평균", clim)

# 2026년 예측 : 검증에서 더 나았던 방식을 2025년까지 학습해 재적용
if best_name == "계절 나이브":
    pred26 = 월[월.index.year == 2025].values
else:
    r5 = 월[월.index.year >= 2021]
    pred26 = r5.groupby(r5.index.month).mean().values
idx26 = pd.date_range("2026-01-01", periods=12, freq="MS")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), gridspec_kw={"width_ratios": [1.15, 1]})

# 좌 : 2025 백테스트
style(ax1)
m = range(1, 13)
ax1.plot(m, test.values, color=INK, lw=2.6, marker="o", ms=6,
         markeredgecolor=SURF, markeredgewidth=1.2, zorder=4, label="실제 2025")
ax1.plot(m, naive, color=BLUE, lw=1.8, ls="--", marker="s", ms=4.5, zorder=3,
         label=f"계절 나이브 (MAE {mae_naive:.2f}℃)")
ax1.plot(m, clim, color=PINK, lw=1.8, ls=":", marker="^", ms=4.5, zorder=3,
         label=f"최근 5년 평균 (MAE {mae_clim:.2f}℃)")
ax1.set_xticks(list(m)); ax1.set_xticklabels([f"{i}월" for i in m], fontsize=9)
ax1.set_title("검증 — 2025년을 예측해 실제와 비교", fontsize=13.5, fontweight="bold", pad=10)
ax1.set_ylabel("월평균 기온 (℃)", color=MUTED, fontsize=10.5)
ax1.legend(frameon=False, fontsize=9.5, labelcolor=MUTED, loc="upper left")

# 우 : 2026 예측
style(ax2)
최근2년 = 월[월.index.year >= 2024]
ax2.plot(최근2년.index, 최근2년.values, color=INK, lw=2.0, marker="o", ms=4,
         markeredgecolor=SURF, markeredgewidth=1, zorder=3, label="실측 (2024~2025)")
ax2.plot(idx26, pred26, color=PINK, lw=2.4, ls="--", marker="D", ms=5,
         markeredgecolor=SURF, markeredgewidth=1, zorder=4, label=f"2026 예측 ({best_name})")
band = mae(test.values, best_vals)
ax2.fill_between(idx26, pred26 - band, pred26 + band, color=PINK, alpha=0.13, zorder=2,
                 label=f"검증 오차 범위 (±{band:.2f}℃)")
ax2.axvline(pd.Timestamp("2026-01-01"), color=GRID, lw=1.2, zorder=1)
ax2.set_title("예측 — 2026년 12개월", fontsize=13.5, fontweight="bold", pad=10)
ax2.set_ylabel("월평균 기온 (℃)", color=MUTED, fontsize=10.5)
ax2.set_ylim(top=ax2.get_ylim()[1] + 8)
ax2.legend(frameon=False, fontsize=9.5, labelcolor=MUTED, loc="upper left", ncol=1)

fig.suptitle("베이스라인 예측 — 검증과 2026년 전망 (정확도보다 가정·한계 확인이 목적)",
             fontsize=15, fontweight="bold", color=INK, y=1.02)
save(fig, "06_forecast_baseline.png")

# ---------- 리포트용 수치 ----------
print("\n" + "=" * 64)
print("보너스 과제 — 리포트에 쓸 수치")
print("=" * 64)
print(f"[A] 추세 성분: {tr.iloc[0]:.2f}℃ → {tr.iloc[-1]:.2f}℃ ({tr.iloc[-1]-tr.iloc[0]:+.2f}℃)")
print(f"[A] 계절성 진폭: {계절폭:.2f}℃ (최저 {res.seasonal.min():.2f} ~ 최고 {res.seasonal.max():.2f})")
print(f"[A] 잔차 표준편차: {잔차표준편차:.2f}℃ | 추세+계절성 설명력: {설명력*100:.1f}%")
resid_abs = res.resid.abs().dropna().sort_values(ascending=False)
print(f"[A] 잔차가 가장 큰 달 3개:")
for d, v in resid_abs.head(3).items():
    print(f"      {d:%Y-%m}  잔차 {res.resid[d]:+.2f}℃")
print(f"\n[B] 2025 검증 MAE — 계절 나이브 {mae_naive:.2f}℃ / 최근5년평균 {mae_clim:.2f}℃")
print(f"[B] 채택: {best_name}")
print(f"[B] 2026 예측 (℃): {[round(v,1) for v in pred26]}")
print(f"[B] 2026 연평균 예측: {np.mean(pred26):.2f}℃ (2025 실측 {test.mean():.2f}℃)")
err = np.abs(test.values - best_vals)
print(f"[B] 월별 오차 최대 {err.max():.2f}℃ ({list(m)[int(err.argmax())]}월) / 최소 {err.min():.2f}℃")
