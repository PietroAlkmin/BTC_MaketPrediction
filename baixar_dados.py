"""Baixa o fechamento diário de IBOV e DJP (BCOM) do Yahoo Finance e grava dados/indices.csv.

Roda uma vez, fora do Docker. Requer yfinance.
"""
from pathlib import Path

import pandas as pd
import yfinance as yf

SAIDA = Path(__file__).parent / "dados" / "indices.csv"

precos = yf.download(["^BVSP", "DJP"], start="2010-01-01", auto_adjust=False, progress=False)["Close"]
precos = precos.rename(columns={"^BVSP": "ibov", "DJP": "bcom"})[["ibov", "bcom"]].dropna()
# o dia corrente fica de fora: com o pregão aberto, o valor não é fechamento
precos = precos[precos.index < pd.Timestamp.today().normalize()]
precos.index.name = "data"

SAIDA.parent.mkdir(exist_ok=True)
precos.to_csv(SAIDA)
print(len(precos), "dias em comum, de", precos.index[0].date(), "a", precos.index[-1].date())
