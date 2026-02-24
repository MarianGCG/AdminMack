import pandas as pd
from datetime import datetime
from ..models import Aseguradoras, ComprobantesComisiones

def limpiar_cuit(valor):
    if pd.isna(valor):
        return None

    cuit = str(valor).replace("-", "").replace(".0", "").strip()
    return cuit if cuit else None


def limpiar_importe(valor):

    if pd.isna(valor):
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



def importar_comprobantes_arca(archivo):

    df = pd.read_excel(archivo, header=1)
    df.columns = df.columns.str.strip()

    insertados = 0
    actualizados = 0
    no_encontrados = 0
    omitidos = 0

    for _, row in df.iterrows():

        fecha = row.get("Fecha")
        tipo_texto = str(row.get("Tipo", "")).strip()
        numero = str(row.get("Número Desde", "")).replace(".0", "").strip()
        cuit = limpiar_cuit(row.get("Nro. Doc. Receptor"))
        print("Fecha leída:", fecha)

        if pd.isna(fecha) or not numero or not cuit:
            omitidos += 1
            continue

        #fecha = pd.to_datetime(fecha).date()
        fecha = pd.to_datetime(fecha, dayfirst=True).date()
        print("Fecha fecha =  pd.to_datetime(fecha, dayfirst=True).date()", fecha)
        # 🔹 PERIODO = MES ANTERIOR
        periodo_mes = fecha.month - 1
        periodo_anio = fecha.year

        print("fecha.month:",fecha.month)
        print("Periodo_mes:", periodo_mes)

        if periodo_mes == 0:
            periodo_mes = 12
            periodo_anio -= 1

 


        # 🔹 IMPORTES
        neto = limpiar_importe(row.get("Neto Gravado Total"))
        no_gravado = limpiar_importe(row.get("Neto No Gravado"))
        exento = limpiar_importe(row.get("Op. Exentas"))
        iva = limpiar_importe(row.get("Total IVA"))
        total = limpiar_importe(row.get("Imp. Total"))

        # 🔹 TIPO COMPROBANTE
        if "nota de crédito" in tipo_texto.lower():
            tipo_comprobante = "NOTA_CREDITO"
            neto = -neto
            no_gravado = -no_gravado
            exento = -exento
            iva = -iva
            total = -total
        else:
            tipo_comprobante = "FACTURA"

        # 🔹 TIPO FACTURA (A/B/C)
        if tipo_texto.strip().endswith("A"):
            tipo_factura = "A"
        elif tipo_texto.strip().endswith("B"):
            tipo_factura = "B"
        elif tipo_texto.strip().endswith("C"):
            tipo_factura = "C"
        else:
            tipo_factura = "A"

        # 🔹 ASEGURADORA
        aseguradora = Aseguradoras.objects.filter(cuit=cuit).first()

        if not aseguradora:
            no_encontrados += 1
            continue

        # 🔹 INSERT / UPDATE (SIN OMITIR)
        obj, created = ComprobantesComisiones.objects.update_or_create(
            aseguradora=aseguradora,
            tipo_comprobante=tipo_comprobante,
            tipo_factura=tipo_factura,
            numero_comprobante=numero,
            periodo_anio=periodo_anio,
            periodo_mes=periodo_mes,
            defaults={
                "fecha_comprobante": fecha,
                "moneda": "$",
                "neto": neto,
                "no_gravado": no_gravado,
                "exento": exento,
                "iva": iva,
                "total": total,
            }
        )

        if created:
            insertados += 1
        else:
            actualizados += 1

    return {
        "insertados": insertados,
        "actualizados": actualizados,
        "omitidos": omitidos,
        "no_encontrados": no_encontrados
    }