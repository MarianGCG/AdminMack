import pandas as pd
import os
import pdfplumber
import re
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from ..models import Movimiento, Regla
import re

MESES_CORTOS = {
    "ENE": "01",
    "FEB": "02",
    "MAR": "03",
    "ABR": "04",
    "MAY": "05",
    "JUN": "06",
    "JUL": "07",
    "AGO": "08",
    "SEP": "09",
    "OCT": "10",
    "NOV": "11",
    "DIC": "12",
}


def obtener_periodo_pdf(texto):

    texto = texto.upper()

    m = re.search(
        r"CIERRE.*?(\d{2})\s+([A-Z]{3})\s+(\d{2})",
        texto,
        re.DOTALL
    )

    if not m:
        print("NO ENCONTRE EL PERIODO")
        return ""

    dia = m.group(1)
    mes = m.group(2)
    anio = m.group(3)

    periodo = "20" + anio + MESES_CORTOS.get(mes, "00")

    print("PERIODO DETECTADO:", periodo)

    return periodo


def obtener_origen_pdf(texto):

    texto = texto.upper()

    titular = "??"

    m = re.search(
        r"CONSUMIDOR FINAL\s+([A-ZÑ ]+?)\s+DR ",
        texto,
        re.DOTALL,
    )

    if m:
        titular = " ".join(m.group(1).split())

    return f"??-??-??-{titular}"




def obtener_datos_nombre_archivo(nombre_archivo):

    nombre = os.path.splitext(os.path.basename(nombre_archivo))[0]

    partes = nombre.split("-")

    if len(partes) < 5:
        raise Exception(
            "El nombre del archivo debe ser:\n"
            "TIPO-MARCA-BANCO-ALIAS-PERIODO.pdf"
        )

    return {

        "tipo": partes[0].upper(),
        "marca": partes[1].upper(),
        "banco": partes[2].upper(),
        "alias": partes[3].upper(),
        "periodo": partes[4],

    }

def buscar_regla(descripcion):

    descripcion = str(descripcion).upper()

    reglas = Regla.objects.filter(activa=True).order_by("-texto")

    for regla in reglas:

        if regla.texto.upper() in descripcion:
            return regla

    return None



def importar_movimientos(archivo):

    datos = obtener_datos_nombre_archivo(archivo.name)

    extension = os.path.splitext(archivo.name)[1].lower()

    if extension == ".pdf":

        return importar_pdf_movimientos(archivo)

    elif extension == ".csv":

        return importar_csv_icbc(
            archivo,
            datos
        )

    elif extension in [".xlsx", ".xls"]:

        return importar_excel_galicia(
            archivo,
            datos
        )

    else:

        raise Exception("Formato no soportado")





    leidos = 0
    clasificados = 0
    pendientes = 0
    ignorados = 0

    for _, row in df.iterrows():

        fecha = row["Fecha"]
        descripcion = str(row["Descripcion"]).strip()
        importe = row["Importe"]

        regla = buscar_regla(descripcion)

        categoria = None
        finalidad = None
        persona = None
        grupo = ""

        if regla:

            if regla.accion == "I":
                ignorados += 1
                continue

            elif regla.accion == "C":

                categoria = regla.categoria
                finalidad = regla.finalidad
                persona = regla.persona

                clasificados += 1

            elif regla.accion == "A":

                grupo = regla.grupo
                persona = regla.persona

                clasificados += 1

        else:

            pendientes += 1

        Movimiento.objects.create(

            fecha=fecha,
            periodo=periodo,
            origen=origen,
            descripcion=descripcion,
            importe=importe,

            categoria=categoria,
            finalidad=finalidad,
            persona=persona,
            grupo=grupo,

            regla_aplicada=regla,

        )

        leidos += 1

    return (
        f"Leídos: {leidos} - "
        f"Clasificados: {clasificados} - "
        f"Pendientes: {pendientes} - "
        f"Ignorados: {ignorados}"
    )

    
def importar_pdf_movimientos(archivo):

    movimientos = []

    leyendo = False

    ultimo_mes = None
    ultimo_anio = None

    with pdfplumber.open(archivo) as pdf:
    # Obtener el texto de la primera página

        texto_caratula = pdf.pages[0].extract_text()
        

        datos = obtener_datos_nombre_archivo(archivo.name)
        origen_pdf = obtener_origen_pdf(texto_caratula)
        titular = origen_pdf.split("-", 3)[3]
        origen = (
            f"{datos['tipo']}-"
            f"{datos['marca']}-"
            f"{datos['banco']}-"
            f"{titular}"
        )
        periodo = datos["periodo"]




        periodo = obtener_periodo_pdf(texto_caratula)

        print("PERIODO:", periodo)
        print()
        print("ORIGEN DETECTADO:", origen)
        print()


        for pagina in pdf.pages:

            texto = pagina.extract_text()

            if not texto:
                continue

            lineas = texto.split("\n")

            for linea in lineas:

                linea = linea.strip()

                # -------------------------------
                # Comenzar después del saldo anterior
                # -------------------------------

                if "SALDO ANTERIOR" in linea:
                    leyendo = True
                    continue

                if not leyendo:
                    continue

                # -------------------------------
                # Terminar al llegar al resumen
                # -------------------------------

                if "Total Consumos" in linea:
                    leyendo = False
                    break

                # -------------------------------
                # Buscar una línea de consumo
                # -------------------------------

                m = re.match(
                    r"^(\d{2})\s+([A-Za-z]+)\s+(\d{2})\s+(.+?)\s+([-\d.,]+)$",
                    linea
                )

                if m:

                    anio = int(m.group(1))
                    mes = m.group(2)
                    dia = int(m.group(3))
                    descripcion = m.group(4)
                    importe = m.group(5)

                    ultimo_mes = mes
                    ultimo_anio = anio

                else:

                    m = re.match(
                        r"^(\d{2})\s+(.+?)\s+([-\d.,]+)$",
                        linea
                    )

                    if not m:
                        continue

                    if ultimo_mes is None:
                        continue

                    dia = int(m.group(1))
                    descripcion = m.group(2)
                    importe = m.group(3)

                    anio = ultimo_anio
                    mes = ultimo_mes

                # Ignorar pagos
                if "SU PAGO" in descripcion.upper():
                    continue

                # Ignorar transferencias
                if "TRANSFERENCIA" in descripcion.upper():
                    continue


                movimientos.append({

                    "fecha": f"{dia:02d}/{mes}/{anio}",
                    "descripcion": descripcion,
                    "importe": importe

                })




    MESES = {
        "Enero": 1,
        "Febrero": 2,
        "Marzo": 3,
        "Abril": 4,
        "Mayo": 5,
        "Junio": 6,
        "Julio": 7,
        "Agosto": 8,
        "Septiembre": 9,
        "Octubre": 10,
        "Noviembre": 11,
        "Diciembre": 12,
    }

    leidos = 0
    clasificados = 0
    pendientes = 0
    ignorados = 0

    # SOLO MIENTRAS HACEMOS PRUEBAS
    Movimiento.objects.filter(
        periodo=periodo,
        origen=origen,
    ).delete()


    for mov in movimientos:

        regla = buscar_regla(mov["descripcion"])

        categoria = None
        finalidad = None
        persona = None
        grupo = ""

        if regla:

            if regla.accion == "I":
                ignorados += 1
                continue

            elif regla.accion == "C":
                categoria = regla.categoria
                finalidad = regla.finalidad
                persona = regla.persona
                clasificados += 1

            elif regla.accion == "A":
                grupo = regla.grupo
                persona = regla.persona
                clasificados += 1

        else:
            pendientes += 1

        # Fecha
        dia, mes_txt, anio = mov["fecha"].split("/")
        fecha = datetime(
            2000 + int(anio),
            MESES[mes_txt],
            int(dia)
        ).date()

        # Importe
        importe = mov["importe"].replace(".", "").replace(",", ".")

        if importe.endswith("-"):
            importe = "-" + importe[:-1]
        print("PERIODO =", periodo)

        Movimiento.objects.create(


            fecha=fecha,
            descripcion=mov["descripcion"],
            importe=importe,

            periodo=periodo,
            origen=origen,

            categoria=categoria,
            finalidad=finalidad,
            persona=persona,
            grupo=grupo,

            regla_aplicada=regla,
        )

        leidos += 1

    return (
        f"Leídos: {leidos} - "
        f"Clasificados: {clasificados} - "
        f"Pendientes: {pendientes} - "
        f"Ignorados: {ignorados}"
    )


def actualizar_movimientos():

    for mov in Movimiento.objects.all():

        regla = buscar_regla(mov.descripcion)

        mov.regla_aplicada = regla

        if regla:

            if regla.accion == "I":
                continue

            elif regla.accion == "C":

                mov.categoria = regla.categoria
                mov.finalidad = regla.finalidad
                mov.persona = regla.persona
                mov.grupo = ""

            elif regla.accion == "A":

                mov.grupo = regla.grupo
                mov.persona = regla.persona
                mov.categoria = None
                mov.finalidad = None

        else:

            mov.categoria = None
            mov.finalidad = None
            mov.persona = None
            mov.grupo = ""
            mov.regla_aplicada = None

        mov.save()


def importar_pdf_cuenta_corriente(archivo, datos):

    movimientos = []

    with pdfplumber.open(archivo) as pdf:

        for pagina in pdf.pages:

            texto = pagina.extract_text()

            if not texto:
                continue


        for linea in texto.split("\n"):

            linea = linea.strip()

            #
            # Buscar fecha al comienzo
            #
            m = re.match(r"^(\d{2})-(\d{2})\s+(.*)$", linea)

            if not m:
                continue

            dia = int(m.group(1))
            mes = int(m.group(2))
            resto = m.group(3)

            #
            # Buscar todos los importes de la línea
            #
            importes = re.findall(r"[\d.]+,\d{2}-?", resto)

            if len(importes) < 2:
                continue

            #
            # El último SIEMPRE es el SALDO
            #
            saldo = importes[-1]

            #
            # El penúltimo es el movimiento
            #
            movimiento = importes[-2]

            #
            # Descripción = todo lo anterior al movimiento
            #
            pos = resto.rfind(movimiento)

            descripcion = resto[:pos].strip()

            #
            # Convertir importe
            #
            importe = movimiento.replace(".", "").replace(",", ".")

            if movimiento.endswith("-"):
                importe = "-" + importe[:-1]

            fecha = datetime(
                int(datos["periodo"][:4]),
                mes,
                dia
            ).date()

            movimientos.append({

                "fecha": fecha,
                "descripcion": descripcion,
                "importe": importe,

            })









    print()
    print("================================")
    print("MOVIMIENTOS LEIDOS:", len(movimientos))
    print("================================")

    Movimiento.objects.filter(

        periodo=datos["periodo"],
        origen=f"{datos['tipo']}-{datos['marca']}-{datos['banco']}"

    ).delete()

    for mov in movimientos:

        regla = buscar_regla(mov["descripcion"])

        categoria = None
        finalidad = None
        persona = None
        grupo = ""

        if regla:

            if regla.accion == "I":
                continue

            elif regla.accion == "C":

                categoria = regla.categoria
                finalidad = regla.finalidad
                persona = regla.persona

            elif regla.accion == "A":

                grupo = regla.grupo
                persona = regla.persona

        Movimiento.objects.create(

            periodo=datos["periodo"],

            origen=f"{datos['tipo']}-{datos['marca']}-{datos['banco']}",

            fecha=mov["fecha"],
            descripcion=mov["descripcion"],
            importe=mov["importe"],

            categoria=categoria,
            finalidad=finalidad,
            persona=persona,
            grupo=grupo,

            regla_aplicada=regla,

        )

    return f"Importados {len(movimientos)} movimientos."


def importar_csv_icbc(archivo, datos):

    df = pd.read_csv(
        archivo,
        header=None,
        names=[
            "Fecha",
            "Descripcion",
            "Debito",
            "Credito",
            "Saldo",
        ]
    )

    Movimiento.objects.filter(
        periodo=datos["periodo"],
        origen=f"{datos['tipo']}-{datos['marca']}-{datos['banco']}"
    ).delete()

    leidos = 0

    for _, row in df.iterrows():

      
        fecha = pd.to_datetime(
            row["Fecha"],
            format="%m/%d/%y"
        ).date()

        descripcion = str(row["Descripcion"]).strip()


        debito = float(row["Debito"])
        credito = float(row["Credito"])

        if debito != 0:
            importe = -debito
        else:
            importe = credito
        regla = buscar_regla(descripcion)

        categoria = None
        finalidad = None
        persona = None
        grupo = ""

        if regla:

            if regla.accion == "I":
                continue

            elif regla.accion == "C":

                categoria = regla.categoria
                finalidad = regla.finalidad
                persona = regla.persona

            elif regla.accion == "A":

                grupo = regla.grupo
                persona = regla.persona

        Movimiento.objects.create(

            periodo=datos["periodo"],

            origen=f"{datos['tipo']}-{datos['marca']}-{datos['banco']}",

            fecha=fecha,
            descripcion=descripcion,
            importe=importe,

            categoria=categoria,
            finalidad=finalidad,
            persona=persona,
            grupo=grupo,

            regla_aplicada=regla,

        )

        leidos += 1

    return f"Importados {leidos} movimientos."



def importar_excel_galicia(archivo, datos):

    df = pd.read_excel(
        archivo,
        skiprows=5
    )
    print(df.columns.tolist())
    print(df.head())
    Movimiento.objects.filter(
        periodo=datos["periodo"],
        origen=f"{datos['tipo']}-{datos['marca']}-{datos['banco']}"
    ).delete()

    leidos = 0

    for _, row in df.iterrows():

        if pd.isna(row["Fecha"]):
            continue

      
        fecha = pd.to_datetime(
            row["Fecha"],
            dayfirst=True
        ).date()
        descripcion = str(row["Movimiento"]).strip()


        debito = row["Debito"]
        credito = row["Credito"]

        if pd.isna(debito):
            debito = 0

        if pd.isna(credito):
            credito = 0

        debito = float(str(debito).replace(".", "").replace(",", "."))
        credito = float(str(credito).replace(".", "").replace(",", "."))

        if debito != 0:

            importe = -abs(debito)

        elif credito != 0:

            importe = abs(credito)

        else:

            importe = 0




        regla = buscar_regla(descripcion)

        categoria = None
        finalidad = None
        persona = None
        grupo = ""

        if regla:

            if regla.accion == "I":
                continue

            elif regla.accion == "C":

                categoria = regla.categoria
                finalidad = regla.finalidad
                persona = regla.persona

            elif regla.accion == "A":

                grupo = regla.grupo
                persona = regla.persona

        Movimiento.objects.create(

            periodo=datos["periodo"],

            origen=f"{datos['tipo']}-{datos['marca']}-{datos['banco']}",

            fecha=fecha,
            descripcion=descripcion,
            importe=importe,

            categoria=categoria,
            finalidad=finalidad,
            persona=persona,
            grupo=grupo,

            regla_aplicada=regla,

        )

        leidos += 1

    return f"Importados {leidos} movimientos."


import pdfplumber
import re
from datetime import datetime


def importar_pdf_tc_galicia(archivo, datos):

    Movimiento.objects.filter(
        periodo=datos["periodo"],
        origen__startswith=f"{datos['tipo']}-{datos['marca']}-{datos['banco']}"
    ).delete()

    origen = (
        f"{datos['tipo']}-"
        f"{datos['marca']}-"
        f"{datos['banco']}-"
        f"{datos['titular']}"
    )

    leyendo = False
    leidos = 0

    patron = re.compile(
        r"(\d{2}-\d{2}-\d{2})\s+(.*?)\s+([\d.,]+)$"
    )

    with pdfplumber.open(archivo) as pdf:

        for pagina in pdf.pages:

            texto = pagina.extract_text()

            if not texto:
                continue

            for linea in texto.split("\n"):

                linea = linea.strip()

                if "DETALLE DEL CONSUMO" in linea:
                    leyendo = True
                    continue

                if not leyendo:
                    continue

                if (
                    "TOTAL A PAGAR" in linea
                    or "Plan V" in linea
                    or "TARJETA " in linea
                ):
                    continue

                m = patron.search(linea)

                if not m:
                    continue

                fecha_txt = m.group(1)
                descripcion = m.group(2).strip()
                importe_txt = m.group(3)

                fecha = datetime.strptime(
                    fecha_txt,
                    "%d-%m-%y"
                ).date()

                importe = float(
                    importe_txt
                        .replace(".", "")
                        .replace(",", ".")
                )

                regla = buscar_regla(descripcion)

                categoria = None
                finalidad = None
                persona = None
                grupo = ""

                if regla:

                    if regla.accion == "I":
                        continue

                    elif regla.accion == "C":

                        categoria = regla.categoria
                        finalidad = regla.finalidad
                        persona = regla.persona

                    elif regla.accion == "A":

                        grupo = regla.grupo
                        persona = regla.persona

                Movimiento.objects.create(

                    periodo=datos["periodo"],

                    origen=origen,

                    fecha=fecha,

                    descripcion=descripcion,

                    importe=importe,

                    categoria=categoria,

                    finalidad=finalidad,

                    persona=persona,

                    grupo=grupo,

                    regla_aplicada=regla,

                )

                leidos += 1

    return f"Importados {leidos} movimientos."