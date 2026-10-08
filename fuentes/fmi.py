# Fuente 2b: crecimiento del PIB según el FMI (DataMapper).
import pandas as pd
import requests

import config


def traer():
    if config.MODO != "respaldo":
        try:
            anios = ",".join(str(a) for a in range(config.BM_DESDE, config.BM_HASTA + 2))
            url = f"https://www.imf.org/external/datamapper/api/v1/{config.FMI_INDICADOR}/{config.PAIS}?periods={anios}"
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            valores = r.json()["values"][config.FMI_INDICADOR][config.PAIS]
            df = pd.DataFrame([{"anio": int(a), "indicador": "pib_crecimiento_fmi_pct", "valor": v, "fuente": "FMI"}
                               for a, v in valores.items()])
            if df.empty:
                raise RuntimeError("el FMI no devolvió datos")
            return df
        except Exception as e:
            print(f"   aviso FMI: {e}. Uso el respaldo.")
    return pd.read_csv(config.RESPALDO / "respaldo_fmi.csv")
