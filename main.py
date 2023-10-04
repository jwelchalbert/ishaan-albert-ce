from fastapi import FastAPI
from data_engineer_ce.pubchem import ChemicalDataFetcher

app = FastAPI()


@app.get("/")
def read_root() -> dict[str, str]:
    return {"Hello": "World"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
