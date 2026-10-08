# Fuente 2a: indicadores del Banco Mundial para Ecuador.
import pandas as pd
import requests

import config


def _uno(codigo, nombre):
    url = (f"https://api.worldbank.org/v2/country/{config.PAIS}/indicator/{codigo}"
           f"?format=json&date={config.BM_DESDE}:{config.BM_HASTA}&per_page=100")
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    datos = r.json()[1]
    df = pd.DataFrame([{"anio": int(d["date"]), "indicador": nombre, "valor": d["value"], "fuente": "Banco Mundial"}
                       for d in datos if d["value"] is not None])
    if df.empty:
        raise RuntimeError(f"Banco Mundial no devolvió datos para {codigo}")
    return df


def traer():
    if config.MODO != "respaldo":
        try:
            return pd.concat([_uno(c, n) for n, c in config.BM_INDICADORES.items()], ignore_index=True)
        except Exception as e:
            print(f"   aviso Banco Mundial: {e}. Uso el respaldo.")
    return pd.read_csv(config.RESPALDO / "respaldo_banco_mundial.csv")
