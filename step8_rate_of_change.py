# -*- coding: utf-8 -*-
"""
M1-1 시계열 분석 | STEP 8 : 변화율(rate of change) — 어디에 쓰고 어디에 쓰지 않았는가

과제 목표 2-② "이동평균, 변화율 등 기본 시계열 분석 기법을 왜/어떻게 적용했는지
설명할 수 있다" 에 대응한다.

(a) 연평균기온의 전년 대비 **변화량(℃)** — 연간 변동이 평균 추세보다 훨씬 크다
(b) 같은 변화를 **변화율(%)** 로 바꾸면 섭씨/켈빈에 따라 값이 20배 달라진다
    → 기온(간격척도)에 백분율 변화율을 쓰면 안 되는 이유
(c) 폭염·열대야 **일수**는 비율척도이므로 변화율(%)이 성립한다 — 여기에만 적용했다
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd


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
os.makedirs("images", exist_ok=True)

UP, DOWN = "#C2185B", "#0072B2"      # 상승 / 하락 (validate_palette.js 통과 팔레트)
INK, GRID, GRAY = "#1F2933", "#DDE3E8", "#6B7785"

df = pd.read_csv("data/processed/asos_2016_2025_clean.csv", parse_dates=["날짜"])
df["연"] = df["날짜"].dt.year
df["폭염"] = (df["최고기온"] >= 33).astype(int)
df["열대야"] = (df["최저기온"] >= 25).astype(int)

# 전국 연평균 : 지점평균의 평균 (step6 ②에서 채택한 방식과 동일)
yr = df.groupby(["연", "지점번호"])["평균기온"].mean().groupby("연").mean()
ext = df.groupby(["연", "지점번호"])[["폭염", "열대야"]].sum().groupby("연").mean()

delta = yr.diff()                              # 변화량 (℃)
pct_c = yr.pct_change() * 100                  # 변화율 (섭씨 기준, %)
pct_k = (yr + 273.15).pct_change() * 100       # 변화율 (켈빈 기준, %)
pct_hw = ext["폭염"].pct_change() * 100
pct_tn = ext["열대야"].pct_change() * 100

tbl = pd.DataFrame({
    "연평균기온": yr.round(2), "변화량(℃)": delta.round(2),
    "변화율_섭씨(%)": pct_c.round(2), "변화율_켈빈(%)": pct_k.round(3),
    "폭염일수": ext["폭염"].round(1), "폭염_변화율(%)": pct_hw.round(1),
    "열대야일수": ext["열대야"].round(1), "열대야_변화율(%)": pct_tn.round(1),
})
print("\n[표] 전년 대비 변화량 · 변화율")
print(tbl.to_string())

print(f"\n  변화량 평균 : {delta.mean():+.3f}℃/년   표준편차 : {delta.std():.3f}℃")
print(f"  → 연간 변동(σ {delta.std():.2f}℃)이 평균 추세({delta.mean():+.3f}℃)의 "
      f"{delta.std()/abs(delta.mean()):.0f}배다. 전년 대비 변화만으로는 추세를 읽을 수 없다.")
print(f"\n  2024년 같은 변화(+{delta[2024]:.2f}℃)를 백분율로 바꾸면")
print(f"    섭씨 기준 {pct_c[2024]:+.2f}%   /   켈빈 기준 {pct_k[2024]:+.3f}%   "
      f"→ {pct_c[2024]/pct_k[2024]:.1f}배 차이")
print("    영점(0℃)을 어디에 두느냐에 따라 값이 달라지므로, 기온에 백분율 변화율은 성립하지 않는다.")

# =====================================================================
# 그림 10
# =====================================================================
fig, axes = plt.subplots(1, 3, figsize=(15.2, 5.0))
fig.patch.set_facecolor("white")
yrs = delta.dropna().index.astype(int)

# (a) 변화량 (℃)
ax = axes[0]
v = delta.dropna().values
ax.bar(yrs, v, 0.62, color=[UP if x > 0 else DOWN for x in v])
for x, y in zip(yrs, v):
    ax.text(x, y + (0.035 if y > 0 else -0.045), f"{y:+.2f}", ha="center",
            va="bottom" if y > 0 else "top", fontsize=9.5, fontweight="bold", color=INK)
ax.axhline(delta.mean(), color="#7A4B00", linestyle="--", linewidth=1.5)
ax.text(yrs[-1] + 0.15, delta.mean(), f" 평균 {delta.mean():+.3f}℃/년",
        va="center", fontsize=9.5, color="#7A4B00", fontweight="bold")
ax.axhline(0, color=INK, linewidth=1)
ax.set_title("(a) 변화량 — 전년 대비 몇 ℃ 올랐나", fontsize=12.5,
             fontweight="bold", color=INK, pad=10)
ax.set_ylabel("전년 대비 변화량 (℃)", fontsize=10.5)
ax.set_ylim(-1.0, 1.05)
ax.set_xticks(yrs); ax.set_xticklabels(yrs, fontsize=9, rotation=45)
ax.grid(axis="y", color=GRID, linewidth=0.8); ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.text(0.5, 0.02, f"연간 변동 σ={delta.std():.2f}℃ 는 평균 추세의 약 "
                   f"{delta.std()/abs(delta.mean()):.0f}배\n→ 전년 대비만으로는 추세를 읽을 수 없다",
        transform=ax.transAxes, ha="center", fontsize=9.5, color="#7A4B00",
        fontweight="bold", linespacing=1.3)

# (b) 같은 변화를 % 로 — 섭씨 vs 켈빈
ax = axes[1]
x = np.arange(len(yrs)); w = 0.38
ax.bar(x - w/2, pct_c.dropna().values, w, color=UP, label="섭씨(℃) 기준 변화율")
ax.bar(x + w/2, pct_k.dropna().values, w, color=DOWN, label="켈빈(K) 기준 변화율")
ax.axhline(0, color=INK, linewidth=1)
i24 = list(yrs).index(2024)
ax.annotate(f"같은 +{delta[2024]:.2f}℃ 인데\n{pct_c[2024]:+.2f}%  vs  {pct_k[2024]:+.3f}%\n"
            f"→ {pct_c[2024]/pct_k[2024]:.0f}배 차이",
            xy=(i24, pct_c[2024]), xytext=(-0.35, 3.95), fontsize=9.8,
            color="#7A4B00", fontweight="bold", linespacing=1.3,
            arrowprops=dict(arrowstyle="->", color="#7A4B00", lw=1.3))
ax.set_title("(b) 변화율(%) — 기온에는 쓸 수 없다", fontsize=12.5,
             fontweight="bold", color=INK, pad=10)
ax.set_ylabel("전년 대비 변화율 (%)", fontsize=10.5)
ax.set_ylim(-6.5, 7.2)
ax.set_xticks(x); ax.set_xticklabels(yrs, fontsize=9, rotation=45)
ax.legend(fontsize=9.5, frameon=False, loc="lower left")
ax.grid(axis="y", color=GRID, linewidth=0.8); ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

# (c) 일수는 비율척도 — 변화율이 성립한다
ax = axes[2]
ax.bar(x - w/2, pct_hw.dropna().values, w, color=UP, label="폭염일수 변화율")
ax.bar(x + w/2, pct_tn.dropna().values, w, color=DOWN, label="열대야일수 변화율")
ax.axhline(0, color=INK, linewidth=1)
ax.annotate(f"2024년 폭염 {pct_hw[2024]:+.0f}%\n열대야 {pct_tn[2024]:+.0f}%",
            xy=(i24 + w/2, pct_tn[2024]), xytext=(i24 - 4.2, 180), fontsize=9.8,
            color="#7A4B00", fontweight="bold", linespacing=1.3,
            arrowprops=dict(arrowstyle="->", color="#7A4B00", lw=1.3))
ax.set_title("(c) 일수는 변화율이 성립한다 — 여기에만 적용", fontsize=12.5,
             fontweight="bold", color=INK, pad=10)
ax.set_ylabel("전년 대비 변화율 (%)", fontsize=10.5)
ax.set_ylim(-90, 265)
ax.set_xticks(x); ax.set_xticklabels(yrs, fontsize=9, rotation=45)
ax.legend(fontsize=9.5, frameon=False, loc="upper left")
ax.grid(axis="y", color=GRID, linewidth=0.8); ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

fig.suptitle("그림 10. 변화율은 어디에 쓰고 어디에 쓰지 않았는가 — 기온은 간격척도, 일수는 비율척도",
             fontsize=14.5, fontweight="bold", color=INK, y=0.985)
fig.text(0.5, 0.012,
         "기온(℃)은 0이 '없음'을 뜻하지 않는 간격척도라 비율 계산이 성립하지 않는다 — (b)가 그 증거다.  |  "
         "폭염·열대야 일수는 0이 진짜 '0일'인 비율척도이므로 변화율이 성립한다.\n"
         "다만 (c)에서 보듯 기준 연도의 값이 작으면 변화율이 과장되므로, 본 리포트는 배율·변화율 대신 '일수 자체'를 우선 인용했다.",
         ha="center", fontsize=9, color=GRAY, linespacing=1.4)
fig.tight_layout(rect=[0, 0.075, 1, 0.945])
fig.savefig("images/10_rate_of_change.png", dpi=150, facecolor="white")
plt.close(fig)
print("\n[저장] images/10_rate_of_change.png")
