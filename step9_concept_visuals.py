# -*- coding: utf-8 -*-
"""
M1-1 시계열 분석 | STEP 9 : 개념을 눈으로 확인하는 그림 2장

과제 목표 2-① "시계열의 트렌드/계절성/노이즈 개념을 설명할 수 있다"
과제 목표 2-② "이동평균 … 을 왜/어떻게 적용했는지 설명할 수 있다" 에 대응한다.

그림 11  세 성분을 **같은 눈금**으로 그린다 — 추세가 얼마나 작은지 눈으로 보인다
그림 12  이동평균 창을 7 → 30 → 90 → 365일로 넓히면 계절성이 사라지는 과정
         + min_periods 설정 하나가 결론을 +2.35℃ / +0.38℃ 로 가르는 장면
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose


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

CRIM, BLUE, TEAL = "#C2185B", "#0072B2", "#00897B"
INK, GRID, GRAY, FAINT = "#1F2933", "#DDE3E8", "#6B7785", "#C9D2D8"

nat = pd.read_csv("data/processed/nation_daily.csv", parse_dates=["날짜"]).set_index("날짜")
s = nat["전국평균기온"]
m = s.resample("MS").mean()
dec = seasonal_decompose(m, model="additive", period=12)

# =====================================================================
# 그림 11 — 세 성분을 같은 눈금으로
# =====================================================================
parts = [
    ("원본 (월평균기온)", m - m.mean(), INK,
     "추세 + 계절성 + 노이즈가 모두 섞여 있는 상태"),
    ("추세 (Trend)", (dec.trend - dec.trend.mean()).dropna(), CRIM,
     "여러 해에 걸쳐 한 방향 — 같은 눈금에서는 거의 직선으로 보인다"),
    ("계절성 (Seasonality)", dec.seasonal, BLUE,
     "1년 주기로 정확히 반복 — 매년 같은 모양"),
    ("노이즈 (Noise) = 잔차 (Residual)", dec.resid.dropna(), TEAL,
     "추세로도 계절성으로도 설명되지 않는 나머지"),
]
YL = 16.5

fig, axes = plt.subplots(4, 1, figsize=(13.6, 8.4), sharex=True)
fig.patch.set_facecolor("white")
for ax, (name, ser, col, note) in zip(axes, parts):
    ax.axhline(0, color=FAINT, linewidth=1)
    ax.plot(ser.index, ser.values, color=col, linewidth=1.9)
    ax.fill_between(ser.index, 0, ser.values, color=col, alpha=0.12)
    p2p = float(ser.max() - ser.min())
    ax.set_ylim(-YL, YL)
    ax.set_yticks([-15, 0, 15])
    ax.set_ylabel("평균 대비 ℃", fontsize=9.5, color=GRAY)
    BB = dict(facecolor="white", alpha=0.88, edgecolor="none", pad=2.5)
    ax.text(0.004, 0.94, name, transform=ax.transAxes, fontsize=13, fontweight="bold",
            color=col, va="top", bbox=BB, zorder=6)
    ax.text(0.004, 0.68, note, transform=ax.transAxes, fontsize=10, color=GRAY,
            va="top", bbox=BB, zorder=6)
    ax.text(0.996, 0.94, f"최대−최소 = {p2p:.2f}℃", transform=ax.transAxes, fontsize=12,
            fontweight="bold", color=col, ha="right", va="top", bbox=BB, zorder=6)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)

# 추세 패널에 확대 인셋
tr = (dec.trend - dec.trend.mean()).dropna()
ins = axes[1].inset_axes([0.545, 0.10, 0.40, 0.46])
ins.plot(tr.index, tr.values, color=CRIM, linewidth=1.8)
ins.axhline(0, color=FAINT, linewidth=0.9)
ins.set_ylim(-1.1, 1.5)
ins.tick_params(labelsize=7.5, colors=GRAY)
ins.set_title("추세만 14배 확대", fontsize=9, color=CRIM, fontweight="bold", pad=3)
for sp in ("top", "right"):
    ins.spines[sp].set_visible(False)

axes[-1].set_xlabel("")
fig.suptitle("그림 11. 같은 눈금으로 그리면 — 찾으려는 '추세'가 셋 중 가장 작다",
             fontsize=15.5, fontweight="bold", color=INK, y=0.985)
fig.text(0.5, 0.055,
         "네 패널의 세로 눈금(−16.5 ~ +16.5℃)을 모두 같게 맞췄다. 각 성분에서 평균을 뺀 값이다.",
         ha="center", fontsize=10, color=GRAY)
fig.text(0.5, 0.018,
         "계절성 25.96℃  ≫  노이즈 5.29℃  ≫  추세 1.97℃   —   "
         "계절성을 먼저 걷어내지 않으면 추세는 보이지 않는다. 이것이 365일 이동평균을 쓴 이유다.",
         ha="center", fontsize=11.5, color=INK, fontweight="bold")
fig.tight_layout(rect=[0, 0.085, 1, 0.955])
fig.savefig("images/11_three_components_samescale.png", dpi=150, facecolor="white")
plt.close(fig)
print("[저장] images/11_three_components_samescale.png")
for name, ser, _, _ in parts:
    print(f"    {name:34s} 최대−최소 {float(ser.max()-ser.min()):6.2f}℃")

# =====================================================================
# 그림 12 — 이동평균 창 크기 · min_periods
# =====================================================================
WINS = [(7, "#9FB3BF"), (30, TEAL), (90, "#9A7D0A"), (365, CRIM)]
fig, axes = plt.subplots(1, 2, figsize=(15.2, 5.4))
fig.patch.set_facecolor("white")

# (a) 창 크기
ax = axes[0]
ax.plot(s.index, s.values, color="#E4EAEE", linewidth=0.7, label="일별 원자료")
for w, c in WINS:
    r = s.rolling(w, min_periods=w).mean()
    ax.plot(r.index, r.values, color=c, linewidth=2.0 if w == 365 else 1.5,
            label=f"{w}일 이동평균  (σ {r.std():.2f}℃)")
ax.set_title("(a) 창을 넓힐수록 계절성이 깎인다 — 365일에서 거의 사라진다",
             fontsize=12.5, fontweight="bold", color=INK, pad=10)
ax.set_ylabel("전국 일평균기온 (℃)", fontsize=10.5)
ax.set_ylim(-10, 34)
ax.legend(fontsize=9.5, frameon=False, loc="lower center", ncol=2)
ax.grid(axis="y", color=GRID, linewidth=0.8); ax.set_axisbelow(True)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
ax.annotate("창 90일까지는 여전히\n계절 주기가 남아 있다", xy=(s.index[1500], 26.7),
            xytext=(s.index[300], 31.2), fontsize=9.5, color="#9A7D0A", fontweight="bold",
            linespacing=1.3, arrowprops=dict(arrowstyle="->", color="#9A7D0A", lw=1.2))

# (b) min_periods
ax = axes[1]
r200 = s.rolling(365, min_periods=200).mean().dropna()
r365 = s.rolling(365, min_periods=365).mean().dropna()
ax.plot(r200.index, r200.values, color=BLUE, linewidth=2.0,
        label="min_periods=200  (AI 초안)")
ax.plot(r365.index, r365.values, color=CRIM, linewidth=2.0,
        label="min_periods=365  (수정 후 · 본 분석)")
for r, c, lab in [(r200, BLUE, "200"), (r365, CRIM, "365")]:
    ax.scatter([r.index[0]], [r.iloc[0]], s=58, color=c, zorder=5)
    ax.annotate(f"첫 값 {r.iloc[0]:.2f}℃\n({r.index[0].date()})",
                xy=(r.index[0], r.iloc[0]),
                xytext=(r.index[0] + pd.Timedelta(days=240), r.iloc[0] - (0.75 if lab == "200" else -0.62)),
                fontsize=9.5, color=c, fontweight="bold", linespacing=1.3,
                arrowprops=dict(arrowstyle="->", color=c, lw=1.2))
ax.scatter([r365.index[-1]], [r365.iloc[-1]], s=58, color=INK, zorder=5)
ax.text(r365.index[-1], r365.iloc[-1] + 0.22, f"끝 값 {r365.iloc[-1]:.2f}℃",
        ha="right", fontsize=9.5, color=INK, fontweight="bold")
ax.set_title("(b) 설정 하나가 결론을 가른다 — 같은 데이터, 같은 365일 창",
             fontsize=12.5, fontweight="bold", color=INK, pad=10)
ax.set_ylabel("365일 이동평균 (℃)", fontsize=10.5)
ax.set_ylim(10.9, 15.6)
ax.legend(fontsize=10, frameon=False, loc="lower right")
ax.grid(axis="y", color=GRID, linewidth=0.8); ax.set_axisbelow(True)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
ax.text(0.5, 0.955,
        f"끝점 − 첫값 :   200 → {r200.iloc[-1]-r200.iloc[0]:+.2f}℃        "
        f"365 → {r365.iloc[-1]-r365.iloc[0]:+.2f}℃",
        transform=ax.transAxes, ha="center", va="top", fontsize=12, fontweight="bold",
        color="#7A4B00")

fig.suptitle("그림 12. 이동평균을 왜 365일로, 왜 min_periods까지 지정했는가",
             fontsize=15, fontweight="bold", color=INK, y=0.985)
fig.text(0.5, 0.015,
         "(a) 기온의 지배 주기가 1년이므로 창을 정확히 1주기로 잡아야 계절 성분이 상쇄된다.  |  "
         "(b) min_periods=200이면 첫 값이 2016-07-18 기준 200일(겨울·봄 포함) 평균인 11.64℃가 되어 상승폭이 6배 부풀려진다.\n"
         "일별 원자료의 표준편차 9.4℃가 365일 창에서 0.45℃까지 줄어든다 — 계절성이 제거된 것이지 추세가 커진 것이 아니다.",
         ha="center", fontsize=9.5, color=GRAY, linespacing=1.4)
fig.tight_layout(rect=[0, 0.075, 1, 0.945])
fig.savefig("images/12_moving_average_window.png", dpi=150, facecolor="white")
plt.close(fig)
print("[저장] images/12_moving_average_window.png")
for w, _ in WINS:
    r = s.rolling(w, min_periods=w).mean().dropna()
    print(f"    창 {w:3d}일 : σ {r.std():5.2f}℃   진폭 {r.max()-r.min():5.2f}℃")
print(f"    min_periods=200 : 첫값 {r200.iloc[0]:.2f}℃ ({r200.index[0].date()}) → "
      f"끝점차 {r200.iloc[-1]-r200.iloc[0]:+.2f}℃")
print(f"    min_periods=365 : 첫값 {r365.iloc[0]:.2f}℃ ({r365.index[0].date()}) → "
      f"끝점차 {r365.iloc[-1]-r365.iloc[0]:+.2f}℃")
