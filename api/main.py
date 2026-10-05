"""Backend de inferência: carrega o modelo treinado e responde a predição."""
import joblib
from fastapi import FastAPI
from pydantic import BaseModel

artefato = joblib.load("/modelo/modelo.joblib")
modelo, entradas = artefato["modelo"], artefato["entradas"]

app = FastAPI(title="Predição do movimento do IBOV")


class Indicadores(BaseModel):
    ibov_rsi: float
    ibov_macd: float
    ibov_macd_sinal: float
    ibov_macd_hist: float
    bcom_rsi: float
    bcom_macd: float
    bcom_macd_sinal: float
    bcom_macd_hist: float


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(indicadores: Indicadores):
    # a ordem das entradas vem do artefato, a mesma usada no treino
    linha = [[getattr(indicadores, nome) for nome in entradas]]
    probabilidade = float(modelo.predict_proba(linha)[0, 1])
    return {"direcao": "alta" if probabilidade >= 0.5 else "queda", "probabilidade_alta": round(probabilidade, 4)}
