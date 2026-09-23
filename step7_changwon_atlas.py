# -*- coding: utf-8 -*-
"""
M1-1 시계열 분석 | STEP 7 : 창원 — 관측값과 기상청 전망값의 대조 (부록 C)

그림 8  같은 '창원'인데 왜 숫자가 다른가 — 본 분석 지점 관측 vs 기상청 상황지도 창원시
그림 9  창원 5개 구의 차이 — 낮 더위(폭염)와 밤 더위(열대야)의 위험 지역이 다르다

전망값 출처 : 기상청 「기후변화 상황지도」 climate.go.kr/atlas
              창원시(38110) 및 5개 구를 직접 조회, 조회일 2026-09-23
              값은 연대별 평균 일수, SSP1-2.6(저탄소) / SSP5-8.5(고탄소)
관측값 출처 : 본 분석 data/processed/asos_2016_2025_clean.csv (창원 지점)
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd


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
os.makedirs("images", exist_ok=True)

# 색 : step4와 동일 팔레트(validate_palette.js 통과, ΔE 15.9 protan)
OBS, PRJ = "#C2185B", "#0072B2"     # 관측(본 분석) / 전망(상황지도)
DAY, NIGHT = "#C2185B", "#0072B2"   # 낮 더위(폭염) / 밤 더위(열대야)
INK, GRID = "#1F2933", "#DDE3E8"

# =====================================================================
# 0. 본 분석의 창원 지점 관측값 재계산
# =====================================================================
df = pd.read_csv("data/processed/asos_2016_2025_clean.csv", parse_dates=["날짜"])
cw = df[df["지점명"] == "창원"].copy()
cw["연"] = cw["날짜"].dt.year
cw["폭염"] = (cw["최고기온"] >= 33).astype(int)
cw["열대야"] = (cw["최저기온"] >= 25).astype(int)
yr = cw.groupby("연")[["폭염", "열대야"]].sum()

obs_2010s = yr.loc[2016:2019].mean()   # 2010년대 '후반 4년'만 관측 보유
obs_2020s = yr.loc[2020:2025].mean()   # 2020년대 '전반 6년'
print("\n[관측] 창원 지점")
print(yr.to_string())
print(f"  2016~2019 평균 : 폭염 {obs_2010s['폭염']:.1f}일 / 열대야 {obs_2010s['열대야']:.1f}일")
print(f"  2020~2025 평균 : 폭염 {obs_2020s['폭염']:.1f}일 / 열대야 {obs_2020s['열대야']:.1f}일")

# =====================================================================
# 1. 기상청 기후변화 상황지도 조회값 (2026-09-23 조회)
#    연대 : 2000 2010 2020 2030 2040 2050 2060 2070 2080 2090
# =====================================================================
DECADES = [2000, 2010, 2020, 2030, 2040, 2050, 2060, 2070, 2080, 2090]
ATLAS = {
    # 지역 : {시나리오 : {지표 : 연대별 값}}
    "창원시": {
        "lo": {"폭염": [11.1, 13.1, 20.2, 23.9, 29.1, 27.0, 28.4, 29.3, 34.7, 30.1],
               "열대야": [4.0, 8.9, 24.9, 31.2, 35.5, 33.7, 33.7, 33.4, 40.4, 31.2]},
        "hi": {"폭염": [11.1, 13.1, 21.7, 23.0, 37.0, 43.2, 57.9, 69.8, 87.7, 100.8],
               "열대야": [4.0, 8.9, 25.7, 28.6, 43.9, 45.7, 58.7, 68.8, 79.9, 89.4]},
    },
    "의창구": {
        "lo": {"폭염": [18.8, 16.2, 26.8, 30.9, 36.5, 34.2, 36.2, 37.5, 43.4, 39.0],
               "열대야": [5.1, 7.9, 25.4, 31.3, 35.6, 33.6, 33.8, 33.3, 40.1, 31.2]},
        "hi": {"폭염": [18.8, 16.2, 29.2, 30.6, 45.1, 51.7, 66.7, 79.0, 96.8, 110.3],
               "열대야": [5.1, 7.9, 25.8, 28.9, 43.6, 45.4, 58.2, 68.0, 79.1, 88.2]},
    },
    "성산구": {
        "lo": {"폭염": [12.4, 16.9, 23.9, 28.1, 33.5, 31.2, 33.1, 34.4, 40.3, 35.7],
               "열대야": [4.2, 11.8, 27.7, 33.9, 37.9, 36.7, 36.2, 36.3, 43.1, 34.0]},
        "hi": {"폭염": [12.4, 16.9, 25.8, 27.5, 42.7, 48.8, 63.9, 76.3, 94.5, 108.1],
               "열대야": [4.2, 11.8, 28.6, 31.3, 46.7, 48.2, 61.2, 71.3, 82.6, 91.7]},
    },
    "마산회원구": {
        "lo": {"폭염": [11.1, 12.7, 20.0, 23.7, 29.1, 26.9, 28.4, 29.3, 34.6, 30.1],
               "열대야": [4.0, 7.9, 24.9, 31.2, 35.4, 33.5, 33.5, 33.2, 40.2, 31.2]},
        "hi": {"폭염": [11.1, 12.7, 21.5, 23.0, 37.0, 43.3, 58.0, 70.1, 88.3, 101.4],
               "열대야": [4.0, 7.9, 25.5, 28.7, 43.5, 45.7, 58.5, 68.7, 79.9, 89.3]},
    },
    "마산합포구": {
        "lo": {"폭염": [8.2, 10.6, 16.1, 19.5, 24.7, 22.7, 23.6, 24.3, 29.1, 24.6],
               "열대야": [4.0, 9.1, 24.4, 30.7, 35.2, 33.3, 33.5, 33.1, 40.2, 30.8]},
        "hi": {"폭염": [8.2, 10.6, 17.5, 18.3, 31.7, 37.9, 52.2, 64.0, 81.8, 94.4],
               "열대야": [4.0, 9.1, 25.3, 28.1, 43.3, 45.6, 58.5, 68.7, 79.9, 89.9]},
    },
    "진해구": {
        "lo": {"폭염": [5.0, 9.3, 14.1, 17.2, 22.1, 20.3, 20.8, 21.1, 25.9, 21.0],
               "열대야": [2.9, 7.6, 22.2, 28.8, 33.4, 31.2, 31.7, 31.2, 38.4, 28.6]},
        "hi": {"폭염": [5.0, 9.3, 14.6, 15.7, 28.6, 34.5, 48.4, 59.9, 76.8, 89.6],
               "열대야": [2.9, 7.6, 23.4, 26.2, 42.2, 44.0, 56.9, 67.2, 78.3, 88.1]},
    },
}
i2010, i2020, i2090 = DECADES.index(2010), DECADES.index(2020), DECADES.index(2090)

# =====================================================================
# 그림 8 — 같은 '창원'인데 왜 숫자가 다른가
# =====================================================================
fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.6))
fig.patch.set_facecolor("white")

panels = [
    ("폭염일수 (일 최고기온 33℃ 이상)", "폭염",
     [obs_2010s["폭염"], obs_2020s["폭염"]],
     [ATLAS["창원시"]["lo"]["폭염"][i2010], ATLAS["창원시"]["hi"]["폭염"][i2020]]),
    ("열대야일수 (일 최저기온 25℃ 이상)", "열대야",
     [obs_2010s["열대야"], obs_2020s["열대야"]],
     [ATLAS["창원시"]["lo"]["열대야"][i2010], ATLAS["창원시"]["hi"]["열대야"][i2020]]),
]

for ax, (title, key, obs, prj) in zip(axes, panels):
    x = np.arange(2)
    w = 0.34
    b1 = ax.bar(x - w/2, obs, w, color=OBS, label="본 분석 — 창원 관측지점 실측")
    b2 = ax.bar(x + w/2, prj, w, color=PRJ, label="기상청 상황지도 — 창원시 연대평균")
    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.6,
                    f"{b.get_height():.1f}", ha="center", va="bottom",
                    fontsize=10.5, fontweight="bold", color=INK)
    for i in range(2):
        ratio = obs[i] / prj[i]
        if ratio > 1.15:
            lab, col = f"관측이 {ratio:.2f}배 많음", "#7A4B00"
        elif ratio < 0.87:
            lab, col = f"전망이 {1/ratio:.2f}배 많음", "#0072B2"
        else:
            lab, col = f"거의 같음 ({ratio:.2f}배)", "#3A7D44"
        ax.text(i, max(obs[i], prj[i]) + 3.0, lab,
                ha="center", fontsize=10.5, fontweight="bold", color=col)
    ax.set_xticks(x)
    ax.set_xticklabels(["2010년대\n(관측 2016~2019 · 전망 2010~2019)",
                        "2020년대\n(관측 2020~2025 · 전망 2020~2029)"], fontsize=10)
    ax.set_title(title, fontsize=13, fontweight="bold", color=INK, pad=12)
    ax.set_ylabel("연평균 일수 (일)", fontsize=11)
    ax.set_ylim(0, max(max(obs), max(prj)) * 1.30)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, fontsize=10.5, frameon=False, ncol=2,
           loc="upper center", bbox_to_anchor=(0.5, 0.925))
fig.suptitle("그림 8. 같은 '창원'인데 숫자가 다르다 — 2010년대는 1.8배 차이, 2020년대는 거의 일치",
             fontsize=14.5, fontweight="bold", color=INK, y=0.995)
fig.text(0.5, 0.015,
         "관측: 본 분석 ASOS 창원 지점(창원기상대, 마산합포구 소재)  |  "
         "전망: 기상청 기후변화 상황지도 창원시 — 읍면동 값의 산술평균, 2026-09-23 조회\n"
         "2010년대 전망은 두 시나리오 값이 동일(과거 구간), 2020년대는 고탄소(SSP5-8.5) 기준",
         ha="center", fontsize=9, color="#6B7785")
fig.tight_layout(rect=[0, 0.055, 1, 0.885])
fig.savefig("images/08_changwon_obs_vs_atlas.png", dpi=150, facecolor="white")
plt.close(fig)
print("\n[저장] images/08_changwon_obs_vs_atlas.png")

# =====================================================================
# 그림 9 — 창원 5개 구 : 낮 더위와 밤 더위의 위험 지역이 다르다
# =====================================================================
GU = ["의창구", "성산구", "마산회원구", "마산합포구", "진해구"]
past_day = [ATLAS[g]["lo"]["폭염"][i2010] for g in GU]
past_ngt = [ATLAS[g]["lo"]["열대야"][i2010] for g in GU]
fut_day = [ATLAS[g]["hi"]["폭염"][i2090] for g in GU]

order = np.argsort(past_day)[::-1]
GU_s = [GU[i] for i in order]
pd_s = [past_day[i] for i in order]
pn_s = [past_ngt[i] for i in order]

fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.6))
fig.patch.set_facecolor("white")

# (a) 2010년대 — 낮과 밤의 순위가 다르다
ax = axes[0]
x = np.arange(len(GU_s)); w = 0.36
b1 = ax.bar(x - w/2, pd_s, w, color=DAY, label="폭염일수 (낮 더위)")
b2 = ax.bar(x + w/2, pn_s, w, color=NIGHT, label="열대야일수 (밤 더위)")
for bars in (b1, b2):
    for b in bars:
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.3,
                f"{b.get_height():.1f}", ha="center", va="bottom",
                fontsize=10, fontweight="bold", color=INK)
ax.set_xticks(x); ax.set_xticklabels(GU_s, fontsize=11)
ax.set_ylabel("연평균 일수 (일)", fontsize=11)
ax.set_ylim(0, 21.8)
ax.set_title("(a) 2010년대 — 의창구와 마산합포구는 낮·밤 순위가 뒤집힌다",
             fontsize=12.5, fontweight="bold", color=INK, pad=12)
ax.legend(fontsize=10, frameon=False, ncol=2,
          loc="upper center", bbox_to_anchor=(0.5, -0.11))
ax.grid(axis="y", color=GRID, linewidth=0.8); ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
i_uc, i_mh = GU_s.index("의창구"), GU_s.index("마산합포구")
ax.annotate("", xy=(i_uc, 18.6), xytext=(i_mh, 18.6),
            arrowprops=dict(arrowstyle="<->", color="#7A4B00", lw=1.4))
ax.text((i_uc + i_mh) / 2, 19.1,
        "낮 더위는 의창구가 1.53배 많지만\n밤 더위는 마산합포구가 1.15배 많다",
        ha="center", va="bottom", fontsize=9.8, color="#7A4B00", fontweight="bold",
        linespacing=1.3)

# (b) 2090년대 고탄소 폭염 전망
ax = axes[1]
o2 = np.argsort(fut_day)
gu2 = [GU[i] for i in o2]; v2 = [fut_day[i] for i in o2]
bars = ax.barh(np.arange(len(gu2)), v2, 0.6, color=DAY)
for i, b in enumerate(bars):
    ax.text(b.get_width() + 1.2, i, f"{v2[i]:.1f}일", va="center",
            fontsize=11, fontweight="bold", color=INK)
ax.axvline(ATLAS["창원시"]["hi"]["폭염"][i2090], color="#6B7785",
           linestyle="--", linewidth=1.4)
ax.text(ATLAS["창원시"]["hi"]["폭염"][i2090] - 2.0, 0.5,
        f"창원시 평균 {ATLAS['창원시']['hi']['폭염'][i2090]:.1f}일",
        ha="right", va="center", fontsize=9.5, color="#4A5560", fontweight="bold")
ax.set_yticks(np.arange(len(gu2))); ax.set_yticklabels(gu2, fontsize=11)
ax.set_xlabel("연평균 폭염일수 (일)", fontsize=11)
ax.set_xlim(0, 128)
ax.set_title("(b) 2090년대 고탄소(SSP5-8.5) 폭염 전망 — 구별 20.7일 차이",
             fontsize=12.5, fontweight="bold", color=INK, pad=12)
ax.grid(axis="x", color=GRID, linewidth=0.8); ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

fig.suptitle("그림 9. 같은 창원시 안에서도 구별로 다르다 — 낮 더위와 밤 더위의 위험 지역이 일치하지 않는다",
             fontsize=14.5, fontweight="bold", color=INK, y=0.99)
fig.text(0.5, 0.015,
         "자료: 기상청 기후변화 상황지도 (2026-09-23 조회) · 시군구 값은 해당 구 읍면동 값의 산술평균\n"
         "(a)는 두 시나리오 값이 동일한 과거 구간, (b)는 고탄소 시나리오 전망값 — 시나리오이지 예측이 아님",
         ha="center", fontsize=9, color="#6B7785")
fig.tight_layout(rect=[0, 0.055, 1, 0.955])
fig.savefig("images/09_changwon_gu_gap.png", dpi=150, facecolor="white")
plt.close(fig)
print("[저장] images/09_changwon_gu_gap.png")

# =====================================================================
# 수치 요약 출력
# =====================================================================
print("\n[요약] 2010년대 구별 (과거 구간)")
for g in GU:
    print(f"  {g:7s} 폭염 {ATLAS[g]['lo']['폭염'][i2010]:5.1f}일 | "
          f"열대야 {ATLAS[g]['lo']['열대야'][i2010]:5.1f}일")
print(f"  {'창원시':7s} 폭염 {ATLAS['창원시']['lo']['폭염'][i2010]:5.1f}일 | "
      f"열대야 {ATLAS['창원시']['lo']['열대야'][i2010]:5.1f}일")
_hi, _lo = int(np.argmax(past_day)), int(np.argmin(past_day))
print(f"  폭염 최대/최소 배율 : {past_day[_hi]/past_day[_lo]:.2f}배 "
      f"({GU[_hi]} {past_day[_hi]} / {GU[_lo]} {past_day[_lo]})")
print(f"  의창구 vs 마산합포구 — 폭염 {past_day[0]/past_day[3]:.2f}배(의창 우세) / "
      f"열대야 {past_ngt[3]/past_ngt[0]:.2f}배(합포 우세)")
print(f"\n[요약] 2090년대 고탄소 폭염 : {min(fut_day):.1f} ~ {max(fut_day):.1f}일 "
      f"(차이 {max(fut_day)-min(fut_day):.1f}일)")
