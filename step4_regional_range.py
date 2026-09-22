# -*- coding: utf-8 -*-
"""
M1-1 시계열 분석 | STEP 4 : 지역별 연교차(여름-겨울) 분석
왼쪽  — 어느 지역의 여름·겨울 온도차가 심한가 (상위 8 / 하위 8)
오른쪽 — 왜 그런가 : 여름은 전국이 비슷하고 겨울만 벌어진다
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
import numpy as np


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

# 색: 2계열(여름/겨울) — validate_palette.js 통과
#   CVD 최소 ΔE 15.9(protan) / 일반시야 29.3 → 전 항목 PASS
SUMMER, WINTER = "#C2185B", "#0072B2"
INK, MUTED, GRID, SURF = "#1F2933", "#6B7785", "#DDE3E8", "#FCFCFB"

IMG = "images"; os.makedirs(IMG, exist_ok=True)


def style(ax):
    ax.set_facecolor(SURF)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=10)
    ax.title.set_color(INK)


# ---------- 데이터 ----------
df = pd.read_csv("data/processed/asos_2016_2025_clean.csv", parse_dates=["날짜"])
df["월"] = df["날짜"].dt.month

여름 = df[df["월"].isin([6, 7, 8])].groupby("지점명")["평균기온"].mean()
겨울 = df[df["월"].isin([12, 1, 2])].groupby("지점명")["평균기온"].mean()
t = pd.DataFrame({"여름": 여름, "겨울": 겨울})
t["연교차"] = t["여름"] - t["겨울"]
t = t.sort_values("연교차", ascending=False)

N = 8
top, bot = t.head(N), t.tail(N)
sel = pd.concat([top, bot])

fig, (ax1, ax2) = plt.subplots(
    1, 2, figsize=(14.5, 7.4), gridspec_kw={"width_ratios": [1.45, 1]})

# ===== 왼쪽 : 덤벨 차트 — 어느 지역인가 =====
style(ax1)
ax1.grid(axis="x", color=GRID, linewidth=0.8, zorder=0)

y = np.arange(len(sel))[::-1]          # 위에서 아래로
for yi, (nm, r) in zip(y, sel.iterrows()):
    ax1.plot([r["겨울"], r["여름"]], [yi, yi],
             color=GRID, lw=2.4, solid_capstyle="round", zorder=2)
    ax1.scatter(r["겨울"], yi, s=92, color=WINTER, zorder=4,
                edgecolor=SURF, linewidth=1.6)
    ax1.scatter(r["여름"], yi, s=92, color=SUMMER, zorder=4,
                edgecolor=SURF, linewidth=1.6)
    ax1.annotate(f"{r['연교차']:.1f}℃", xy=(r["여름"] + 0.9, yi),
                 va="center", fontsize=10.5, color=INK,
                 fontweight="bold" if yi >= len(sel) - N else "normal")

ax1.set_yticks(y)
ax1.set_yticklabels(sel.index, fontsize=11, color=INK)

# 상위군 / 하위군 구분선
ax1.axhline(N - 0.5, color=GRID, lw=1.4, ls=(0, (4, 3)), zorder=1)
ax1.annotate("연교차 상위 8", xy=(-4.6, len(sel) - 0.65), fontsize=10,
             color=MUTED, fontweight="bold")
ax1.annotate("연교차 하위 8", xy=(-4.6, N - 0.75), fontsize=10,
             color=MUTED, fontweight="bold")

ax1.set_xlim(-5.2, 31.5)
ax1.set_ylim(-0.8, len(sel) - 0.1)
ax1.axvline(0, color=GRID, lw=1, zorder=1)
ax1.set_xlabel("평균기온 (℃)", color=MUTED, fontsize=11)
ax1.set_title("어느 지역이 여름·겨울 온도차가 심한가\n(2016~2025, 98개 지점 중 상·하위 8곳)",
              fontsize=14, fontweight="bold", loc="left", pad=12)

h = [plt.Line2D([], [], marker="o", ls="", ms=10, mfc=WINTER, mec=SURF, label="겨울 (12~2월)"),
     plt.Line2D([], [], marker="o", ls="", ms=10, mfc=SUMMER, mec=SURF, label="여름 (6~8월)")]
ax1.legend(handles=h, frameon=False, fontsize=11, labelcolor=MUTED,
           loc="upper center", bbox_to_anchor=(0.5, -0.085), ncol=2)

# ===== 오른쪽 : 원인 — 겨울만 벌어진다 =====
style(ax2)
ax2.grid(axis="x", color=GRID, linewidth=0.8, zorder=0)

rng = np.random.default_rng(42)
rows = [("여름 (6~8월)", t["여름"], SUMMER, 1.0),
        ("겨울 (12~2월)", t["겨울"], WINTER, 0.0)]
for label, vals, color, yi in rows:
    jit = rng.uniform(-0.13, 0.13, len(vals))
    ax2.scatter(vals, np.full(len(vals), yi) + jit, s=46, color=color,
                alpha=0.55, zorder=3, edgecolor=SURF, linewidth=0.8)
    lo, hi = vals.min(), vals.max()
    ax2.plot([lo, hi], [yi - 0.30, yi - 0.30], color=color, lw=2.6,
             solid_capstyle="round", zorder=4)
    ax2.annotate(f"폭 {hi - lo:.2f}℃   (표준편차 {vals.std():.2f}℃)",
                 xy=((lo + hi) / 2, yi - 0.46), ha="center",
                 fontsize=11, color=color, fontweight="bold")

ax2.set_yticks([0, 1])
ax2.set_yticklabels(["겨울", "여름"], fontsize=12, color=INK)
ax2.set_ylim(-0.75, 1.62)
ax2.set_xlim(-8, 30)
ax2.set_xlabel("지점별 평균기온 (℃)", color=MUTED, fontsize=11)
ax2.set_title("왜 그런가 — 여름은 전국이 붙어 있고,\n겨울만 두 배 넘게 벌어진다 (98개 지점)",
              fontsize=14, fontweight="bold", loc="left", pad=12)

ax2.annotate("내륙 vs 해안·섬  여름 차이 0.00℃  /  겨울 차이 3.10℃\n"
             "연교차와의 상관: 겨울 −0.91,  여름 −0.09",
             xy=(0.29, 0.54), xycoords="axes fraction", ha="center",
             fontsize=10.5, color=INK,
             bbox=dict(boxstyle="round,pad=0.55", fc="#F2F5F7", ec=GRID, lw=1))

fig.suptitle("지역별 여름·겨울 기온차 — 차이를 만드는 계절은 겨울이다",
             fontsize=16.5, fontweight="bold", color=INK, y=1.005)
fig.patch.set_facecolor(SURF)
fig.tight_layout()
fig.savefig(f"{IMG}/07_regional_range.png", dpi=150,
            bbox_inches="tight", facecolor=SURF)
plt.close(fig)
print(f"[저장] {IMG}/07_regional_range.png")

# ---------- 리포트용 수치 ----------
해안 = ["속초", "강릉", "동해", "울진", "포항", "울산", "부산", "통영", "거제", "여수",
        "완도", "진도군", "목포", "군산", "서산", "인천", "백령도", "흑산도", "울릉도",
        "제주", "서귀포", "성산", "고산", "보령", "태안", "영덕", "고흥", "해남",
        "부안", "영광군"]
t["구분"] = np.where(t.index.isin(해안), "해안·섬", "내륙")
g = t.groupby("구분")[["여름", "겨울", "연교차"]].mean().round(2)

print("\n" + "=" * 62)
print("리포트에 쓸 수치")
print("=" * 62)
print(f"① 연교차 최대 {t['연교차'].max():.2f}℃ ({t['연교차'].idxmax()}) / "
      f"최소 {t['연교차'].min():.2f}℃ ({t['연교차'].idxmin()}) / 격차 {t['연교차'].max()-t['연교차'].min():.2f}℃")
print(f"② 여름 지역간 표준편차 {t['여름'].std():.2f}℃ vs 겨울 {t['겨울'].std():.2f}℃")
print(f"③ 연교차 상관 — 겨울 {t['연교차'].corr(t['겨울']):+.3f} / 여름 {t['연교차'].corr(t['여름']):+.3f}")
print(f"④ 내륙(n={(t['구분']=='내륙').sum()}) vs 해안·섬(n={(t['구분']=='해안·섬').sum()})")
print(g.to_string())
print(f"⑤ 대구 연교차 {t.loc['대구','연교차']:.2f}℃ → "
      f"{int((t['연교차']>t.loc['대구','연교차']).sum())+1}위 / 여름 기온은 "
      f"{int((t['여름']>t.loc['대구','여름']).sum())+1}위")
print(f"⑥ 창원 연교차 {t.loc['창원','연교차']:.2f}℃ → "
      f"{int((t['연교차']>t.loc['창원','연교차']).sum())+1}위")
