"""Treina a regressão logística que estima se o IBOV fecha em alta no pregão seguinte."""
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

DADOS = Path("/dados/indices.csv")
MODELO = Path("/modelo")
ENTRADAS = [f"{i}_{n}" for i in ("ibov", "bcom") for n in ("rsi", "macd", "macd_sinal", "macd_hist")]
AQUECIMENTO = 35  # 26 + 9 dias para as médias do MACD estabilizarem


def indicadores(preco: pd.Series) -> pd.DataFrame:
    delta = preco.diff()
    ganho = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    perda = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    rsi = 100 - 100 / (1 + ganho / perda)
    # MACD em % do preço: em pontos, a escala muda com o nível do índice
    macd = (preco.ewm(span=12, adjust=False).mean() - preco.ewm(span=26, adjust=False).mean()) / preco * 100
    sinal = macd.ewm(span=9, adjust=False).mean()
    return pd.DataFrame({"rsi": rsi, "macd": macd, "macd_sinal": sinal, "macd_hist": macd - sinal})


precos = pd.read_csv(DADOS, index_col="data", parse_dates=True)
x = pd.concat([indicadores(precos[i]).add_prefix(f"{i}_") for i in ("ibov", "bcom")], axis=1)[ENTRADAS]
# alvo: fechamento do pregão seguinte acima do fechamento do dia
alta = (precos["ibov"].shift(-1) > precos["ibov"]).astype(int)

exemplo = x.iloc[-1]  # último dia: sem pregão seguinte, serve de entrada para a predição
x, alta = x.iloc[AQUECIMENTO:-1], alta.iloc[AQUECIMENTO:-1]
assert x.notna().all().all(), "indicador com valor ausente"

corte = int(len(x) * 0.8)  # corte cronológico, sem embaralhar
x_treino, x_teste, y_treino, y_teste = x[:corte], x[corte:], alta[:corte], alta[corte:]

modelo = make_pipeline(StandardScaler(), LogisticRegression()).fit(x_treino.to_numpy(), y_treino)
previsto = modelo.predict(x_teste.to_numpy())

metricas = {
    "treino": {"de": str(x_treino.index[0].date()), "ate": str(x_treino.index[-1].date()), "dias": len(x_treino)},
    "teste": {"de": str(x_teste.index[0].date()), "ate": str(x_teste.index[-1].date()), "dias": len(x_teste)},
    "acerto_treino": round(float(modelo.score(x_treino.to_numpy(), y_treino)), 4),
    "acerto_teste": round(float((previsto == y_teste).mean()), 4),
    "acerto_sempre_sobe": round(float(y_teste.mean()), 4),
    "previsoes_de_alta_no_teste": round(float(previsto.mean()), 4),
}

MODELO.mkdir(exist_ok=True)
joblib.dump({"modelo": modelo, "entradas": ENTRADAS}, MODELO / "modelo.joblib")
(MODELO / "metricas.json").write_text(json.dumps(metricas, indent=2))
(MODELO / "exemplo.json").write_text(json.dumps(exemplo.round(4).to_dict(), indent=2))
print(json.dumps(metricas, indent=2))
