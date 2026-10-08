# El orquestador: ejecuta tareas en el orden que piden sus dependencias,
# reintenta si una falla y deja un registro de lo que pasó.
import json
import time
from datetime import datetime, timezone

import config


def orden_de_ejecucion(tareas):
    # tareas = {"nombre": (funcion, ["tareas de las que depende"])}
    listo, pendientes = [], dict(tareas)
    while pendientes:
        salen = [n for n, (_, deps) in pendientes.items() if all(d in listo for d in deps)]
        if not salen:
            raise ValueError("Hay un ciclo: dos tareas se esperan entre sí.")
        for n in sorted(salen):
            listo.append(n)
            del pendientes[n]
    return listo


def ejecutar(tareas, reintentos=None, espera=None):
    reintentos = config.REINTENTOS if reintentos is None else reintentos
    espera = config.ESPERA_SEG if espera is None else espera
    resultados, registro = {}, []
    for nombre in orden_de_ejecucion(tareas):
        funcion, deps = tareas[nombre]
        if any(registro_de(registro, d) != "ok" for d in deps):
            registro.append({"tarea": nombre, "estado": "omitida", "motivo": "falló una tarea previa"})
            print(f"-- {nombre}: omitida")
            continue
        for intento in range(1, reintentos + 2):
            try:
                print(f"-> {nombre} (intento {intento})")
                resultados[nombre] = funcion(**{d: resultados[d] for d in deps})
                registro.append({"tarea": nombre, "estado": "ok", "intentos": intento})
                break
            except Exception as e:
                print(f"   falló: {e}")
                if intento > reintentos:
                    registro.append({"tarea": nombre, "estado": "fallo", "error": str(e), "intentos": intento})
                else:
                    time.sleep(espera)
    return resultados, registro


def registro_de(registro, nombre):
    return next((r["estado"] for r in registro if r["tarea"] == nombre), None)


def guardar_registro(registro):
    config.LOGS.mkdir(parents=True, exist_ok=True)
    corrida = {"inicio_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "tareas": registro}
    (config.LOGS / "ultima_corrida.json").write_text(json.dumps(corrida, ensure_ascii=False, indent=2), encoding="utf-8")
    return corrida
