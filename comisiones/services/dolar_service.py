import pandas as pd
from ..models import CotizacionesDolar

def limpiar_importe(valor):
    if valor is None:
        return 0

    if isinstance(valor, (int, float)):
        return float(valor)

    texto = str(valor).strip()

    if texto == "" or texto.lower() == "nan":
        return 0

    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    else:
        texto = texto.replace(",", "")

    try:
        return float(texto)
    except:
        return 0
    
from django.db import connection

def importar_cotizaciones_excel(archivo):

    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip().str.lower()

    insertadas = 0
    actualizadas = 0
    omitidas = 0

    with connection.cursor() as cursor:

        for _, row in df.iterrows():

            anio = row.get("periodo_anio")
            mes = row.get("periodo_mes")
            valor = limpiar_importe(row.get("valor"))

            if pd.isna(anio) or pd.isna(mes):
                omitidas += 1
                continue

            anio = int(anio)
            mes = int(mes)

            cursor.execute("""
                INSERT INTO cotizaciones_dolar (periodo_anio, periodo_mes, valor)
                VALUES (%s, %s, %s)
                ON CONFLICT (periodo_anio, periodo_mes)
                DO UPDATE SET valor = EXCLUDED.valor
            """, [anio, mes, valor])

            # No podemos saber fácil si fue insert o update,
            # así que lo contamos como procesado
            actualizadas += 1

    return {
        "insertadas": insertadas,
        "actualizadas": actualizadas,
        "omitidas": omitidas
    }