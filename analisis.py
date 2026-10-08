# Paso ANALIZAR: una tabla por sector, el cambio contra la corrida anterior y el cruce con la macro.
from datetime import date

import pandas as pd

import config

ARCHIVO_RESUMEN = config.HISTORICO / "resumen_diario.csv"


def resumen_por_sector(anuncios):
    t = (anuncios.groupby("sector")
         .agg(anuncios=("id", "count"), mediana_m2=("precio_m2", "median"), precio_mediano=("precio_usd", "median"))
         .round(0).sort_values("mediana_m2", ascending=False).reset_index())
    return t[t["anuncios"] >= config.MIN_ANUNCIOS_SECTOR].reset_index(drop=True)


def ultimo_valor(macro, indicador):
    # Solo años ya cerrados: el año en curso del FMI es una proyección.
    s = macro[(macro["indicador"] == indicador) & (macro["anio"] < date.today().year)].sort_values("anio")
    return None if s.empty else (int(s.iloc[-1]["anio"]), float(s.iloc[-1]["valor"]))


def cambio_contra_anterior(mediana_hoy):
    # Compara con la última corrida de un día distinto a hoy.
    if not ARCHIVO_RESUMEN.exists():
        return None
    h = pd.read_csv(ARCHIVO_RESUMEN)
    h = h[h["fecha"] != date.today().isoformat()]
    if h.empty:
        return None
    anterior = float(h.sort_values("fecha").iloc[-1]["mediana_m2"])
    return round((mediana_hoy / anterior - 1) * 100, 2)


def guardar_resumen(n, mediana_m2):
    config.HISTORICO.mkdir(parents=True, exist_ok=True)
    hoy = date.today().isoformat()
    nueva = pd.DataFrame([{"fecha": hoy, "anuncios": n, "mediana_m2": mediana_m2}])
    if ARCHIVO_RESUMEN.exists():
        h = pd.read_csv(ARCHIVO_RESUMEN)
        h = h[h["fecha"] != hoy]        # si corre dos veces el mismo día, no duplica
        nueva = pd.concat([h, nueva], ignore_index=True)
    nueva.sort_values("fecha").to_csv(ARCHIVO_RESUMEN, index=False)


def analizar(anuncios, macro, descartes=None):
    mediana = float(anuncios["precio_m2"].median())
    origen = ", ".join(sorted(anuncios["origen"].unique()))
    es_respaldo = "respaldo" in origen
    # Regla de oro: los datos de respaldo NUNCA entran al histórico (lo contaminarían).
    cambio = None if es_respaldo else cambio_contra_anterior(mediana)
    alerta = cambio is not None and abs(cambio) >= config.UMBRAL_ALERTA_PCT
    if not es_respaldo:
        guardar_resumen(len(anuncios), round(mediana, 2))
    return {
        "descartes": descartes or {},
        "es_respaldo": es_respaldo,
        "n_anuncios": int(len(anuncios)),
        "mediana_m2": round(mediana, 2),
        "cambio_pct": cambio,
        "alerta": bool(alerta),
        "por_sector": resumen_por_sector(anuncios),
        "inflacion": ultimo_valor(macro, "inflacion_pct"),
        "pib_bm": ultimo_valor(macro, "pib_crecimiento_pct"),
        "pib_fmi": ultimo_valor(macro, "pib_crecimiento_fmi_pct"),
        "credito": ultimo_valor(macro, "credito_privado_pib_pct"),
        "origen": origen,
    }
