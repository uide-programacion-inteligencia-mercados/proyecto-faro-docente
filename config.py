# Todo lo que se puede cambiar del observatorio vive aquí.
import os
from pathlib import Path

RAIZ = Path(__file__).parent
DATOS = RAIZ / "data"
RESPALDO = DATOS / "respaldo"
HISTORICO = DATOS / "historico"
REPORTES = RAIZ / "reports"
LOGS = RAIZ / "logs"

# "auto" = intenta la fuente real y, si falla, usa el respaldo.
# "respaldo" = no sale a internet (sirve para probar).
MODO = os.environ.get("FARO_MODO", "auto")

PAIS = "ECU"
CIUDAD = "Quito"

# El cambio (en %) del precio por m2 que hace sonar la alerta.
UMBRAL_ALERTA_PCT = 5.0

# La página de RE/MAX saca sus anuncios de esta API pública (la misma que usa su sitio web).
REMAX_API = "https://api-ec.redremax.com/remaxweb-ec/api/listings/findAllWithEntrepreneurships"
REMAX_TAMANO_PAGINA = 100
REMAX_MAX_PAGINAS = 80          # tope de seguridad: hoy son unas 64 páginas en todo el país
REMAX_PAUSA_SEG = 1             # cortesía con el sitio entre una página y otra
UBICACION = "Quito, Pichincha"  # el anuncio cuenta si su ubicación termina así

TIPOS_VIVIENDA = ["casa", "departamento", "penthouse"]   # terrenos, oficinas y locales no se comparan con vivienda
AREA_MIN_M2, AREA_MAX_M2 = 15, 3000
PRECIO_M2_MIN, PRECIO_M2_MAX = 100, 10000   # fuera de este rango (USD por m²) es error de digitación
MIN_ANUNCIOS_SECTOR = 3                      # un sector con menos anuncios no tiene mediana confiable

# Control de calidad: si no se cumple, el pipeline se detiene a propósito.
MIN_ANUNCIOS_LIMPIOS = 30
MEDIANA_M2_PLAUSIBLE = (300, 6000)   # USD por m² razonable para vivienda en Quito

BM_INDICADORES = {
    "inflacion_pct": "FP.CPI.TOTL.ZG",
    "pib_crecimiento_pct": "NY.GDP.MKTP.KD.ZG",
    "credito_privado_pib_pct": "FS.AST.PRVT.GD.ZS",
}
BM_DESDE, BM_HASTA = 2015, 2025
FMI_INDICADOR = "NGDP_RPCH"   # crecimiento real del PIB

REINTENTOS = 2
ESPERA_SEG = 3
