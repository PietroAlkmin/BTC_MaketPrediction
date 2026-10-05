"""Gera os gráficos de resultado a partir de modelo/metricas.json.

Roda fora do Docker, depois do treino. Requer matplotlib.
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = Path(__file__).parent
SAIDA = RAIZ / "imagens"
m = json.loads((RAIZ / "modelo" / "metricas.json").read_text())

FUNDO, TINTA, APAGADO, EIXO = "#fcfcfb", "#0b0b0b", "#898781", "#c3c2b7"
AZUL, LARANJA, CINZA = "#2a78d6", "#eb6834", "#c3c2b7"
plt.rcParams.update({
    "font.family": ["Segoe UI", "DejaVu Sans"], "font.size": 11, "text.color": TINTA,
    "figure.facecolor": FUNDO, "axes.facecolor": FUNDO, "savefig.facecolor": FUNDO,
    "axes.edgecolor": EIXO, "xtick.color": APAGADO, "ytick.color": TINTA,
})


def limpar(ax):
    for lado in ("top", "right", "left", "bottom"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(length=0)


def pct(v):
    return f"{v:.1f}%".replace(".", ",")


# 1. acerto do modelo contra o palpite que diz "sobe" todo dia
nomes = ['Palpite "sobe todo dia"', "Modelo"]
valores = [m["acerto_sempre_sobe"] * 100, m["acerto_teste"] * 100]
fig, ax = plt.subplots(figsize=(8, 2.6))
ax.barh(nomes, valores, color=[CINZA, AZUL], height=0.5)
for y, v in enumerate(valores):
    ax.text(v + 1.5, y, pct(v), va="center", fontweight="bold")
ax.axvline(50, color=APAGADO, lw=1, ls=(0, (3, 3)))
ax.text(48.5, 1.42, "50%: cara ou coroa", color=APAGADO, ha="right", va="bottom", fontsize=9)
ax.set_xlim(0, 100)
ax.set_ylim(-0.5, 1.75)
ax.set_xticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
ax.set_title(f"Dias em que a direção prevista se confirmou ({m['teste']['dias']} dias de teste)",
             loc="left", fontsize=12, fontweight="bold", pad=12)
limpar(ax)
fig.savefig(SAIDA / "resultado-acerto.png", dpi=160, bbox_inches="tight")

# 2. peso de cada indicador na decisão
ROTULO = {"rsi": "RSI", "macd": "MACD", "macd_sinal": "MACD sinal", "macd_hist": "MACD histograma"}
nomes = [f"{k.split('_', 1)[0].upper()}  {ROTULO[k.split('_', 1)[1]]}" for k in m["pesos"]][::-1]
valores = list(m["pesos"].values())[::-1]
limite = max(abs(v) for v in valores) * 1.35
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.barh(nomes, valores, color=[AZUL if v >= 0 else LARANJA for v in valores], height=0.55)
for y, v in enumerate(valores):
    ax.text(v + (limite * 0.02 if v >= 0 else -limite * 0.02), y, f"{v:+.3f}".replace(".", ","),
            va="center", ha="left" if v >= 0 else "right", fontsize=10)
ax.axvline(0, color=EIXO, lw=1)
ax.set_xlim(-limite, limite)
ax.set_xticks([])
ax.set_xlabel("← diminui a chance de alta          aumenta a chance de alta →", color=APAGADO, labelpad=10)
ax.set_title("Peso de cada indicador na decisão do modelo", loc="left", fontsize=12, fontweight="bold", pad=12)
limpar(ax)
fig.savefig(SAIDA / "resultado-pesos.png", dpi=160, bbox_inches="tight")
print("gravados:", *(p.name for p in sorted(SAIDA.glob("resultado-*.png"))))
