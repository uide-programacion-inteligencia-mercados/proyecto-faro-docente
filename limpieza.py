# Paso LIMPIAR: deja los anuncios listos para medir y anota por qué descartó cada uno.
import pandas as pd

import config


def limpiar_con_descartes(df):
    """Devuelve (anuncios limpios, dict con cuántos se descartaron por cada motivo)."""
    df = df.copy()
    descartes = {"anuncios_crudos": len(df)}
    for c in ["precio_usd", "area_m2", "area_terreno_m2", "dormitorios", "banos"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["sector"] = df["sector"].astype(str).str.strip().str.title()

    def quitar(motivo, mascara_a_conservar):
        nonlocal df
        descartes[motivo] = int((~mascara_a_conservar).sum())
        df = df[mascara_a_conservar]

    quitar("id_repetido", ~df["id"].duplicated())
    quitar("no_es_venta", df["operacion"] == "venta")          # el arriendo es un precio mensual: otra medida
    quitar("no_es_vivienda", df["tipo"].isin(config.TIPOS_VIVIENDA))
    quitar("no_esta_activo", df["estado"] == "active")          # reservado o en negociación ya no es oferta

    # Error común de digitación: 75.579 (con punto de miles) llega como 75,579 dólares.
    df = df.copy()
    arregla = (df["precio_usd"] < 1000) & (df["precio_usd"] % 1 != 0)
    df.loc[arregla, "precio_usd"] = (df.loc[arregla, "precio_usd"] * 1000).round(0)
    descartes["precio_corregido_por_punto_de_miles"] = int(arregla.sum())

    quitar("sin_precio", df["precio_usd"] > 0)
    quitar("area_imposible", df["area_m2"].between(config.AREA_MIN_M2, config.AREA_MAX_M2))
    cols = ["sector", "tipo", "precio_usd", "area_m2", "dormitorios", "banos"]
    quitar("duplicado_con_otro_id", ~df.duplicated(subset=cols))   # mismo anuncio publicado dos veces

    df = df.copy()
    df["precio_m2"] = (df["precio_usd"] / df["area_m2"]).round(2)
    quitar("precio_m2_imposible", df["precio_m2"].between(config.PRECIO_M2_MIN, config.PRECIO_M2_MAX))
    df = df.copy()
    med = df["precio_m2"].median()
    mad = (df["precio_m2"] - med).abs().median()
    if mad > 0:   # fuera lo extremo: más de 3 desviaciones (errores de digitación)
        quitar("precio_m2_extremo", (df["precio_m2"] - med).abs() <= 3 * mad * 1.4826)
    else:
        descartes["precio_m2_extremo"] = 0
    descartes["anuncios_limpios"] = len(df)
    return df.reset_index(drop=True), descartes


def limpiar_anuncios(df):
    return limpiar_con_descartes(df)[0]


def limpiar_macro(df):
    df = df.copy()
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df = df.dropna(subset=["valor"]).drop_duplicates(subset=["anio", "indicador", "fuente"])
    return df.sort_values(["indicador", "anio"]).reset_index(drop=True)
