from django.shortcuts import render
from django.db.models import Q

from django.http import HttpResponse
import pandas as pd
from decimal import Decimal
from .models import (
    LiquidacionAseguradora,
    PAS,
    PASCliente,
    Aseguradoras,
    PASAseguradora
) 

def reporte_comisiones_view(request):

    pas_codigo = request.GET.get("pas")
    aseguradora_id = request.GET.get("aseguradora")
    clave1 = request.GET.get("clave1")
    clave2 = request.GET.get("clave2")
    fecha_desde = request.GET.get("fecha_desde")
    fecha_hasta = request.GET.get("fecha_hasta")

    exportar = request.GET.get("exportar")

    datos = LiquidacionAseguradora.objects.select_related("aseguradora")

    # ============================
    # FILTRO PAS (clientes)
    # ============================

    if pas_codigo:

        clientes = PASCliente.objects.filter(
            pas__codigo_pas=pas_codigo
        )

        filtro = Q()

        for c in clientes:

            sub_filtro = Q()

            # 🔥 NUEVO: FILTRO POR ASEGURADORA
            if c.aseguradora_id:
                sub_filtro &= Q(aseguradora_id=c.aseguradora_id)


            if c.aseguradora_id:
                sub_filtro &= Q(aseguradora_id=c.aseguradora_id)
            elif aseguradora_id:
                sub_filtro &= Q(aseguradora_id=aseguradora_id)

                
            if c.cliente_clave1:
                sub_filtro &= Q(cliente__icontains=c.cliente_clave1)

            if c.cliente_clave2:
                sub_filtro &= Q(cliente__icontains=c.cliente_clave2)

            if sub_filtro:
                filtro |= sub_filtro

                
        if filtro:
            datos = datos.filter(filtro)
        else:
            datos = datos.none()

    # ============================
    # OTROS FILTROS
    # ============================

    if aseguradora_id:
        datos = datos.filter(aseguradora_id=aseguradora_id)

    if clave1:
        datos = datos.filter(cliente__icontains=clave1)

    if clave2:
        datos = datos.filter(cliente__icontains=clave2)

    if fecha_desde:
        datos = datos.filter(fecha_liquidacion__gte=fecha_desde)

    if fecha_hasta:
        datos = datos.filter(fecha_liquidacion__lte=fecha_hasta)

    datos = datos.order_by(
        "fecha_liquidacion",
        "quincena",
        "aseguradora__nombre",
        "cliente",
        "poliza",
        "endoso"
    )

    # ============================
    # PAS seleccionado
    # ============================

    pas_obj = PAS.objects.filter(codigo_pas=pas_codigo).first()
    pas_seleccionado = pas_obj.nombre if pas_obj else ""

    filas = []

    for d in datos:

        # 🔹 porcentaje de la liquidación (SIEMPRE)
        porcentaje = d.porcentaje
        comision_compania = d.comision_agente

        # 🔹 default
        porcentaje_pas = 0
        comision_pas = 0

        # ============================
        # BUSCAR % PAS (regla)
        # ============================

        if pas_codigo:

            pa = PASAseguradora.objects.filter(
                pas_id=pas_codigo,
                aseguradora_id=d.aseguradora_id
            ).first()

            if pa:

                from comisiones.models import ReglaComision

   
                moneda = normalizar_texto(d.moneda)
                ramo = normalizar_texto(d.ramo)


                regla = None

                # 1️⃣ intento: match específico por ramo
                if ramo:

                    reglas = ReglaComision.objects.filter(
                        aseguradora_id=d.aseguradora_id,
                        moneda__iexact=moneda,
                        nivel=pa.nivel
                    )

                    regla = None

                    for r in reglas:
                        if normalizar_texto(r.producto) == ramo:
                            regla = r
                            break

                        


                # 2️⃣ fallback: producto vacío (regla general)
                if not regla:
                    regla = ReglaComision.objects.filter(
                        aseguradora_id=d.aseguradora_id,
                        nivel=pa.nivel,
                        moneda__iexact=moneda
                    ).filter(
                        Q(producto__isnull=True) | Q(producto="")
                    ).first()


                # 🔥 comision_agente segun moneda
                comision_agente = d.comision_agente or 0
                if d.moneda == "U$S" and d.cotizacion_dolar:
                    comision_agente = comision_agente * d.cotizacion_dolar

                # 🔥 PRIMA segun moneda
                prima = d.prima or 0
                if d.moneda == "U$S" and d.cotizacion_dolar:
                    prima = prima * d.cotizacion_dolar


                if regla:
                    porcentaje_pas = regla.porcentaje

                    # 🔥 BASE
                    if regla.base_comision == "Comision":
                        base = comision_agente or 0
                    else:
                        base = prima or 0

                    if d.comision_adelantada and d.comision_adelantada > 0:
                        meses = d.meses_adelanto or 1
                        comision_pas = base * porcentaje_pas / 100 * meses
                    else:
                        comision_pas = base * porcentaje_pas / 100

                        

        # ============================
        # 🔥 NEGATIVO (nota crédito)
        # ============================

        valores = [
            d.comision_agente,
            d.descuento_adelanto,
            d.comision_adelantada
        ]

        if any(v and v < 0 for v in valores):
            comision_pas = comision_pas * -1

        # ============================
        # 🔥 COMISION PAS SIN IVA
        # ============================

        if d.aseguradora and d.aseguradora.incluye_iva == "S":
            base = comision_pas or Decimal("0")
            comision_pas_sin_iva = base / Decimal("1.21")
        else:
            comision_pas_sin_iva = comision_pas or Decimal("0")

            

        prima = round(prima, 2)
        comision_pas = round(comision_pas, 2)
        comision_pas_sin_iva = round(comision_pas_sin_iva, 2)


        # ============================
        # ARMAR FILA
        # ============================

        filas.append({
            "fecha": d.fecha_liquidacion,
            "quincena": d.quincena,
            "aseg": d.aseguradora.nombre,
            "pas": pas_seleccionado,   # 🔥 AGREGAR ESTO            
            "cliente": d.cliente,
            "ramo": d.ramo,
            "poliza": d.poliza,
            "endoso": d.endoso,
            "moneda": d.moneda,
            "cotizacion": d.cotizacion_dolar,
            "meses": d.meses_adelanto,
            "premio": d.premio,
            "prima": prima,
            "porcentaje": porcentaje ,
            "comision_agente": comision_agente,
            "descuento_adelanto": d.descuento_adelanto,
            "comision_adelantada": d.comision_adelantada,
            "porcentaje_pas": (porcentaje_pas or 0) ,
            "comision_pas": comision_pas,
            "comision_pas_sin_iva": comision_pas_sin_iva
        })

# ============================
# EXPORTAR EXCEL
# ============================

    if exportar == "excel":

        df = pd.DataFrame(filas)

        if request.GET.get("solo_pas") == "1":
            columnas = [
                "fecha", "quincena", "aseg", "pas", "cliente", "ramo",
                "poliza", "endoso", "moneda", "cotizacion",
                "meses", "premio", "prima",                
                "porcentaje_pas", "comision_pas", "comision_pas_sin_iva"
            ]
        else:
            columnas = [
                "fecha", "quincena", "aseg", "pas", "cliente", "ramo",
                "poliza", "endoso", "moneda", "cotizacion",
                "meses", "premio", "prima",  
                "porcentaje", "comision_agente",
                "descuento_adelanto", "comision_adelantada",
                "porcentaje_pas", "comision_pas", "comision_pas_sin_iva"
            ]

        df = df[columnas]

        df = df.rename(columns={
            "fecha": "Fecha",
            "aseg": "Aseguradora",
            "pas": "PAS",
            "cliente": "Cliente",
            "ramo": "Ramo",
            "poliza": "Poliza",
            "endoso": "Endoso",
            "moneda": "Moneda",
            "cotizacion": "Cotización",
            "meses": "Meses",
            "premio": "Premio",
            "prima": "Prima",
            "porcentaje_pas": "% PAS",
            "comision_pas": "Comisión PAS",
            "comision_pas_sin_iva": "Comisión PAS s/IVA"
        })

        # ============================
        # 🔥 FORZAR NUMÉRICOS (CLAVE)
        # ============================

        columnas_moneda = [
            "Premio",
            "Prima",
            "Comisión PAS",
            "Comisión PAS s/IVA"
        ]

        columnas_porcentaje = [
            "% PAS"
        ]

        for col in columnas_moneda:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        for col in columnas_porcentaje:
            df[col] = pd.to_numeric(df[col], errors='coerce') 

            


        # 👉 CREAR RESPONSE
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=reporte_comisiones.xlsx'

        # 👉 TODO EL EXCEL ADENTRO
        with pd.ExcelWriter(response, engine='xlsxwriter') as writer:

            # mover tabla hacia abajo
            df.to_excel(writer, index=False, sheet_name='Reporte', startrow=4)
            workbook  = writer.book
            worksheet = writer.sheets['Reporte']


            # ============================
            # CALCULAR TOTALES
            # ============================


            total_bruto = df["Comisión PAS"].sum()
            total_neto = df["Comisión PAS s/IVA"].sum()

            descuento = 0.09
            pago = total_neto * (1 - descuento)

            # ============================
            # POSICIÓN (columna O)
            # ============================
            col_inicio = 14   # columna O (empieza en 0)
            fila_inicio = len(df) + 8

            # ============================
            # FORMATOS
            # ============================

            # 🎨 Azul sistema
            azul = '#1F4E78'

            formato_titulo_caja = workbook.add_format({
                'bold': True,
                'align': 'center',
                'valign': 'vcenter',
                'border': 2,
                'bg_color': azul,
                'font_color': 'white'
            })

            formato_label = workbook.add_format({
                'border': 2,
                'bold': True
            })

            formato_moneda = workbook.add_format({
                'num_format': '$ #,##0.00',
                'border': 2
            })

            formato_porcentaje = workbook.add_format({
                'num_format': '0%',
                'border': 2
            })

            # ============================
            # 🧾 TÍTULO CON MERGE
            # ============================

            worksheet.merge_range(
                fila_inicio, col_inicio,
                fila_inicio, col_inicio + 1,
                "Monotributo",
                formato_titulo_caja
            )

            # ============================
            # 📊 CUADRO
            # ============================

            worksheet.write(fila_inicio+1, col_inicio, "Bruto", formato_label)
            worksheet.write(fila_inicio+1, col_inicio+1, total_bruto, formato_moneda)

            worksheet.write(fila_inicio+2, col_inicio, "IVA", formato_label)
            worksheet.write(fila_inicio+2, col_inicio+1, "-", formato_label)

            worksheet.write(fila_inicio+3, col_inicio, "Neto", formato_label)
            worksheet.write(fila_inicio+3, col_inicio+1, total_neto, formato_moneda)

            worksheet.write(fila_inicio+5, col_inicio, "Desc. (Imp.)", formato_label)
            worksheet.write(fila_inicio+5, col_inicio+1, descuento, formato_porcentaje)

            worksheet.write(fila_inicio+6, col_inicio, "Pago", formato_label)
            worksheet.write(fila_inicio+6, col_inicio+1, pago, formato_moneda)


            # =========================
            # ENCABEZADO
            # =========================
            from datetime import date

            formato_titulo = workbook.add_format({
                'bold': True,
                'font_size': 14
            })

            formato_texto = workbook.add_format({
                'bold': True
            })

            worksheet.write("A1", "Reporte de Comisiones", formato_titulo)
            worksheet.write("D1", f"Fecha: {date.today().strftime('%d/%m/%Y')}", formato_texto)

            worksheet.write("A2", f"PAS: {pas_seleccionado or 'Todos'}", formato_texto)

            worksheet.write(
                "A3",
                f"fecha_desde: {fecha_desde or ''} - fecha_hasta: {fecha_hasta or ''}",
                formato_texto
            )

            # =========================
            # FORMATO COLUMNAS
            # =========================

            columnas_moneda = [
                "Premio",
                "Prima",
                "Comisión PAS",
                "Comisión PAS s/IVA"
            ]

            columnas_porcentaje = [
                "% PAS"
            ]

            # 👉 asegurar tipo numérico
            for col in columnas_moneda + columnas_porcentaje:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # 👉 aplicar formato correcto
            for i, col in enumerate(df.columns):

                if col in columnas_moneda:
                    worksheet.set_column(i, i, 18, formato_moneda)

                elif col in columnas_porcentaje:
                    worksheet.set_column(i, i, 12, formato_porcentaje)
                    
            # =========================
            # AUTO ANCHO
            # =========================
            for i, col in enumerate(df.columns):
                ancho = max(
                    df[col].astype(str).map(len).max(),
                    len(col)
                ) + 2

                worksheet.set_column(i, i, ancho)

        return response



    # ============================
    # TOTALES
    # ============================



    total_prima = sum([d["prima"] or 0 for d in filas])
    total_comision = sum([d["comision_agente"] or 0 for d in filas])
    total_comision_pas_sin_iva = sum([d["comision_pas_sin_iva"] or 0 for d in filas])

    # ============================
    # RENDER
    # ============================

    return render(
        request,
        "reportes/comisiones.html",
        {
            "datos": filas,
            "pas": PAS.objects.all().order_by("codigo_pas"),
            "aseguradoras": Aseguradoras.objects.filter(activa=True).order_by("nombre"),
            "pas_seleccionado": pas_seleccionado,
            "total_prima": total_prima,
            "total_comision": total_comision,
            "total_comision_pas_sin_iva": total_comision_pas_sin_iva
        }
    )


import unicodedata

def normalizar_texto(texto):

    if texto is None:
        return ""

    texto = str(texto)

    texto = texto.replace("\xa0", " ")
    texto = texto.replace("\n", " ")
    texto = texto.replace("\r", " ")

    texto = " ".join(texto.split())

    texto = texto.lower().strip()

    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")

    return texto
