# -*- coding: utf-8 -*-
"""
M1-1 시계열 분석 | STEP 2 : 시각화
전국 기온 10년(2016~2025) — 추세 / 계절성 / 극한기상 / 지역비교 4장
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd

# ---------- 한글 폰트 (윈도우/맥/리눅스 어디서든 동작) ----------
def set_korean_font():
    import glob
    names = {f.name for f in fm.fontManager.ttflist}
    for c in ["Malgun Gothic", "NanumGothic", "NanumBarunGothic", "AppleGothic",
              "Noto Sans CJK KR", "Noto Sans KR", "Noto Sans CJK JP"]:
        if c in names:
            plt.rc("font", family=c)
            return c
    for pat in [r"C:\Windows\Fonts\malgun.ttf",
                "/usr/share/fonts/**/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/**/*Nanum*.ttf",
                "/System/Library/Fonts/AppleSDGothicNeo.ttc"]:
        for p in glob.glob(pat, recursive=True):
            try:
                fm.fontManager.addfont(p)
                nm = fm.FontProperties(fname=p).get_name()
                plt.rc("font", family=nm)
                return nm
            except Exception:
                pass
    return None

print(f"[폰트] {set_korean_font()} 적용")
plt.rc("axes", unicode_minus=False)

# ---------- 색 (colorblind-safe, 검증 통과) ----------
C = {"서울": "#0072B2", "강릉": "#D55E00", "대구": "#00897B",
     "창원": "#C2185B", "부산": "#7B3FA0", "제주": "#9A7D0A"}
INK, MUTED, GRID = "#1F2933", "#6B7785", "#DDE3E8"
LINE, ACCENT = "#0072B2", "#C2185B"
SURF = "#FCFCFB"

IMG = "images"
os.makedirs(IMG, exist_ok=True)

def style(ax):
    ax.set_facecolor(SURF)
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=10)
    ax.title.set_color(INK)

def save(fig, name):
    fig.patch.set_facecolor(SURF)
    fig.tight_layout()
    p = f"{IMG}/{name}"
    fig.savefig(p, dpi=150, bbox_inches="tight", facecolor=SURF)
    plt.close(fig)
    print(f"[저장] {p}")

# ---------- 데이터 ----------
df = pd.read_csv("data/processed/asos_2016_2025_clean.csv", parse_dates=["날짜"])
nat = pd.read_csv("data/processed/nation_daily.csv", parse_dates=["날짜"]).set_index("날짜")
df["연"] = df["날짜"].dt.year
df["월"] = df["날짜"].dt.month

RESULT = {}

# ===== 그래프 1 : 추세 — 일평균기온 + 이동평균 =====
nat["MA30"] = nat["전국평균기온"].rolling(30, min_periods=15).mean()
nat["MA365"] = nat["전국평균기온"].rolling(365, min_periods=365).mean()

fig, ax = plt.subplots(figsize=(13, 5.2))
style(ax)
ax.plot(nat.index, nat["전국평균기온"], color="#C7D2D9", lw=0.7, zorder=2, label="일별 평균기온")
ax.plot(nat.index, nat["MA30"], color=LINE, lw=1.6, zorder=3, label="30일 이동평균")
ax.plot(nat.index, nat["MA365"], color=ACCENT, lw=2.6, zorder=4, label="365일 이동평균 (연간 추세)")
ax.set_title("전국 일평균기온 추이와 이동평균 (2016~2025)", fontsize=15, fontweight="bold", pad=14)
ax.set_ylabel("기온 (℃)", color=MUTED, fontsize=11)
ax.legend(frameon=False, loc="lower left", fontsize=10, labelcolor=MUTED, ncol=3)
s, e = nat["MA365"].dropna().iloc[0], nat["MA365"].dropna().iloc[-1]
ax.annotate(f"{e:.2f}℃", xy=(nat["MA365"].dropna().index[-1], e), xytext=(-8, 10),
            textcoords="offset points", color=ACCENT, fontsize=10, fontweight="bold", ha="right")
save(fig, "01_trend_moving_average.png")
RESULT["MA365_시작"], RESULT["MA365_끝"] = round(s, 2), round(e, 2)

# ===== 그래프 2 : 계절성 — 전반5년 vs 후반5년 월별 평균 =====
early = df[df["연"] <= 2020].groupby("월")["평균기온"].mean()
late = df[df["연"] >= 2021].groupby("월")["평균기온"].mean()
x = range(1, 13); w = 0.4

fig, ax = plt.subplots(figsize=(11, 5))
style(ax)
ax.bar([i - w/2 for i in x], early.values, w-0.03, color="#9FB3C0",
       label="2016~2020 평균", zorder=3)
ax.bar([i + w/2 for i in x], late.values, w-0.03, color=ACCENT,
       label="2021~2025 평균", zorder=3)
for i in x:
    d = late[i] - early[i]
    ax.annotate(f"{d:+.1f}", xy=(i, max(early[i], late[i]) + 0.6), ha="center",
                fontsize=9, color=INK if abs(d) >= 0.5 else MUTED,
                fontweight="bold" if abs(d) >= 0.5 else "normal")
ax.set_xticks(list(x)); ax.set_xticklabels([f"{m}월" for m in x])
ax.set_title("월별 평균기온 — 전반 5년 vs 후반 5년 (숫자는 차이 ℃)",
             fontsize=15, fontweight="bold", pad=14)
ax.set_ylabel("평균기온 (℃)", color=MUTED, fontsize=11)
ax.legend(frameon=False, fontsize=10, labelcolor=MUTED, loc="upper left")
save(fig, "02_monthly_seasonality.png")
RESULT["월별차이"] = (late - early).round(2).to_dict()

# ===== 그래프 3 : 극한기상 — 연도별 지점평균 폭염일·열대야 =====
df["폭염"] = (df["최고기온"] >= 33).astype(int)
df["열대야"] = (df["최저기온"] >= 25).astype(int)
ext = df.groupby(["연", "지점번호"])[["폭염", "열대야"]].sum().groupby("연").mean().round(1)

fig, ax = plt.subplots(figsize=(11, 5))
style(ax)
yrs = ext.index.tolist()
ax.bar([y - 0.2 for y in yrs], ext["폭염"], 0.37, color=ACCENT, label="폭염일 (최고 33℃ 이상)", zorder=3)
ax.bar([y + 0.2 for y in yrs], ext["열대야"], 0.37, color=LINE, label="열대야 (최저 25℃ 이상)", zorder=3)
for y in yrs:
    ax.annotate(f"{ext.loc[y,'폭염']:.0f}", xy=(y - 0.2, ext.loc[y, "폭염"] + 0.5),
                ha="center", fontsize=9, color=INK, fontweight="bold")
ax.set_xticks(yrs)
ax.set_title("연도별 지점 평균 폭염일수·열대야일수 (2016~2025)",
             fontsize=15, fontweight="bold", pad=14)
ax.set_ylabel("일수 (지점 평균)", color=MUTED, fontsize=11)
ax.legend(frameon=False, fontsize=10, labelcolor=MUTED, loc="upper left")
save(fig, "03_heatwave_tropicalnight.png")
RESULT["연도별극한"] = ext.to_dict("index")

# ===== 그래프 4 : 지역 비교 — 6곳 연평균기온 =====
regions = ["서울", "강릉", "대구", "창원", "부산", "제주"]
reg = (df[df["지점명"].isin(regions)]
       .groupby(["연", "지점명"])["평균기온"].mean().unstack().round(2))

fig, ax = plt.subplots(figsize=(11.5, 5.4))
style(ax)
for r in regions:
    lw = 3.0 if r == "창원" else 1.8
    ax.plot(reg.index, reg[r], color=C[r], lw=lw, marker="o", ms=5,
            markeredgecolor=SURF, markeredgewidth=1.2, zorder=3, label=r)

# 끝점 라벨이 겹치지 않도록 최소 간격 확보
ends = sorted(((reg[r].iloc[-1], r) for r in regions), reverse=True)
MIN_GAP = 0.32
ypos = []
for v, r in ends:
    y = v if not ypos else min(v, ypos[-1][0] - MIN_GAP)
    ypos.append((y, r))
for y, r in ypos:
    ax.annotate(r, xy=(reg.index[-1], y), xytext=(10, 0),
                textcoords="offset points", color=C[r], fontsize=10.5,
                fontweight="bold" if r == "창원" else "normal", va="center")

ax.set_xticks(reg.index.tolist())
ax.set_xlim(reg.index.min() - 0.3, reg.index.max() + 1.1)
ax.set_title("지역별 연평균기온 추이 (2016~2025) — 창원 강조",
             fontsize=15, fontweight="bold", pad=34)
ax.set_ylabel("연평균기온 (℃)", color=MUTED, fontsize=11)
ax.legend(frameon=False, fontsize=9.5, labelcolor=MUTED, ncol=6,
          loc="upper center", bbox_to_anchor=(0.5, 1.09))
save(fig, "04_region_comparison.png")
RESULT["지역연평균"] = reg.to_dict("index")

# ===== 리포트용 핵심 숫자 =====
print("\n" + "=" * 62)
print("리포트에 쓸 핵심 수치")
print("=" * 62)
print(f"① 365일 이동평균: {RESULT['MA365_시작']}℃ → {RESULT['MA365_끝']}℃  "
      f"(변화 {RESULT['MA365_끝']-RESULT['MA365_시작']:+.2f}℃)")
yr = df.groupby("연")["평균기온"].mean().round(2)
print(f"② 연평균기온: {yr.to_dict()}")
print(f"   최고 연도 {yr.idxmax()}년 {yr.max()}℃ / 최저 연도 {yr.idxmin()}년 {yr.min()}℃")
print(f"③ 전반5년 평균 {df[df['연']<=2020]['평균기온'].mean():.2f}℃ → "
      f"후반5년 {df[df['연']>=2021]['평균기온'].mean():.2f}℃ "
      f"({df[df['연']>=2021]['평균기온'].mean()-df[df['연']<=2020]['평균기온'].mean():+.2f}℃)")
print(f"④ 월별 차이 상위3: {sorted(RESULT['월별차이'].items(), key=lambda t:-t[1])[:3]}")
print(f"⑤ 폭염일수 최다 {ext['폭염'].idxmax()}년 {ext['폭염'].max()}일 / "
      f"최소 {ext['폭염'].idxmin()}년 {ext['폭염'].min()}일")
print(f"⑥ 열대야 최다 {ext['열대야'].idxmax()}년 {ext['열대야'].max()}일")
print(f"⑦ 지역 10년 상승폭(2025-2016):")
for r in regions:
    print(f"     {r}: {reg[r].iloc[0]:.2f} → {reg[r].iloc[-1]:.2f}  ({reg[r].iloc[-1]-reg[r].iloc[0]:+.2f}℃)")
print(f"⑧ 극값: 최고 {df['최고기온'].max()}℃ / 최저 {df['최저기온'].min()}℃")
