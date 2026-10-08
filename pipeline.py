# El pipeline del Observatorio de Referencia: BUSCAR, GUARDAR, LIMPIAR, CONTROLAR, ANALIZAR, MOSTRAR.
import sys

import config
import analisis
import limpieza
import orquestador
import reporte
from fuentes import banco_mundial, fmi, remax


def guardar(df, nombre):
    config.DATOS.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.DATOS / nombre, index=False)                     # GUARDAR


def t_remax():
    df = remax.traer()
    guardar(df, "remax_crudo.csv")
    return df


def t_banco_mundial():
    df = banco_mundial.traer()
    guardar(df, "banco_mundial_crudo.csv")
    return df


def t_fmi():
    df = fmi.traer()
    guardar(df, "fmi_crudo.csv")
    return df


def t_limpiar(remax, banco_mundial, fmi):
    import pandas as pd
    anuncios, descartes = limpieza.limpiar_con_descartes(remax)
    macro = limpieza.limpiar_macro(pd.concat([banco_mundial, fmi], ignore_index=True))
    guardar(anuncios, "anuncios_limpios.csv")
    guardar(macro, "macro_limpia.csv")
    return {"anuncios": anuncios, "macro": macro, "descartes": descartes}


def t_control_calidad(limpiar):
    """El portero del pipeline: si los datos no son confiables, FALLA A PROPÓSITO y nada se guarda."""
    a, lo, hi = limpiar["anuncios"], *config.MEDIANA_M2_PLAUSIBLE
    if len(a) < config.MIN_ANUNCIOS_LIMPIOS:
        raise ValueError(f"Control de calidad: solo {len(a)} anuncios limpios (mínimo {config.MIN_ANUNCIOS_LIMPIOS}).")
    mediana = a["precio_m2"].median()
    if not lo <= mediana <= hi:
        raise ValueError(f"Control de calidad: mediana de {mediana:.0f} USD/m² fuera de lo plausible ({lo}-{hi}).")
    if limpiar["macro"].empty:
        raise ValueError("Control de calidad: no llegó ningún dato macroeconómico.")
    return limpiar


def t_analizar(control_calidad):
    return analisis.analizar(control_calidad["anuncios"], control_calidad["macro"], control_calidad["descartes"])


def t_reportar(analizar):
    return reporte.escribir(analizar)


# El DAG: cada tarea dice de quién depende.
TAREAS = {
    "remax": (t_remax, []),
    "banco_mundial": (t_banco_mundial, []),
    "fmi": (t_fmi, []),
    "limpiar": (t_limpiar, ["remax", "banco_mundial", "fmi"]),
    "control_calidad": (t_control_calidad, ["limpiar"]),
    "analizar": (t_analizar, ["control_calidad"]),
    "reportar": (t_reportar, ["analizar"]),
}


def main():
    print(f"Observatorio de Referencia · modo {config.MODO}")
    _, registro = orquestador.ejecutar(TAREAS)
    orquestador.guardar_registro(registro)
    fallas = [r for r in registro if r["estado"] != "ok"]
    print("RESULTADO:", "todo bien" if not fallas else f"{len(fallas)} tarea(s) con problemas")
    sys.exit(1 if fallas else 0)


if __name__ == "__main__":
    main()
