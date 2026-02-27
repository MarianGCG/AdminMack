from django.shortcuts import render
from django.db.models import Sum, Count, Q, DecimalField, Value
from django.db.models.functions import Coalesce, Cast

from django.db import connection
from .models import ComprobantesComisiones
import json
from .services.aseguradoras_service import importar_aseguradoras_excel

from django.db.models.functions import Cast
from django.db.models import IntegerField


import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from django.http import HttpResponse
from io import BytesIO



# =====================================================
# 1️⃣ VER COMPROBANTES
# =====================================================




def ver_comprobantes(request):

    anio = request.GET.get("anio")
    mes = request.GET.get("mes")
    aseguradora = request.GET.get("aseguradora")
    numero = request.GET.get("numero")

    orden1 = request.GET.get("orden1")
    orden2 = request.GET.get("orden2")

    comprobantes = ComprobantesComisiones.objects.all()

    # ============================
    # 🔎 FILTROS
    # ============================

    if anio:
        comprobantes = comprobantes.filter(periodo_anio=anio)

    if mes:
        comprobantes = comprobantes.filter(periodo_mes=mes)

    if aseguradora:
        comprobantes = comprobantes.filter(
            aseguradora__nombre__icontains=aseguradora
        )

    if numero:
        comprobantes = comprobantes.filter(
            numero_comprobante__icontains=numero
        )

    # ============================
    # 💰 COBRADO DINÁMICO
    # ============================

    comprobantes = comprobantes.annotate(
        cobrado=Coalesce(
            Sum("cobranzascomisiones__importe"),
            Value(0),
            output_field=DecimalField()
        )
    )

    # ============================
    # 🔢 NUMERO COMO ENTERO
    # ============================

    comprobantes = comprobantes.annotate(
        numero_int=Cast("numero_comprobante", IntegerField())
    )

    # ============================
    # 🔀 ORDEN DOBLE
    # ============================

    orden_campos = []

    def agregar_orden(valor):
        if not valor:
            return

        if valor == "aseguradora":
            orden_campos.append("aseguradora__nombre")

        elif valor == "periodo":
            orden_campos.extend(["periodo_anio", "periodo_mes"])

        elif valor == "numero":
            orden_campos.append("numero_int")

        elif valor == "cobrado":
            orden_campos.append("-cobrado")

    agregar_orden(orden1)

    if orden2 and orden2 != orden1:
        agregar_orden(orden2)

    if orden_campos:
        comprobantes = comprobantes.order_by(*orden_campos)
    else:
        comprobantes = comprobantes.order_by(
            "aseguradora__nombre",
            "periodo_anio",
            "periodo_mes",
            "numero_int"
        )

    # ============================
    # 📊 TOTALES
    # ============================

    totales = comprobantes.aggregate(
        sum_neto=Coalesce(Sum("neto"), Value(0), output_field=DecimalField()),
        sum_no_gravado=Coalesce(Sum("no_gravado"), Value(0), output_field=DecimalField()),
        sum_exento=Coalesce(Sum("exento"), Value(0), output_field=DecimalField()),
        sum_iva=Coalesce(Sum("iva"), Value(0), output_field=DecimalField()),
        sum_total=Coalesce(Sum("total"), Value(0), output_field=DecimalField()),
        sum_cobrado=Coalesce(Sum("cobranzascomisiones__importe"), Value(0), output_field=DecimalField()),
    )

    return render(request, "ver_comprobantes.html", {
        "comprobantes": comprobantes,
        "totales": totales
    })


# =====================================================
# 2️⃣ VER SALDOS POR PERIODO
# =====================================================

def ver_saldos(request):

    anio = request.GET.get("anio")

    comprobantes = ComprobantesComisiones.objects.all()

    if anio:
        comprobantes = comprobantes.filter(periodo_anio=anio)

    saldos = (
        comprobantes
        .values("periodo_anio", "periodo_mes")
        .annotate(
            cant_facturas=Count("id", filter=Q(tipo_comprobante="FACTURA")),
            cant_creditos=Count("id", filter=Q(tipo_comprobante="NOTA_CREDITO")),
            sum_neto=Sum("neto"),
            sum_no_gravado=Sum("no_gravado"),
            sum_exento=Sum("exento"),
            sum_iva=Sum("iva"),
            sum_total=Sum("total"),
            sum_cobrado=Sum("cobranzascomisiones__importe")
        )
        .order_by("-periodo_anio", "-periodo_mes")
    )

    totales = comprobantes.aggregate(
        total_facturas=Count("id", filter=Q(tipo_comprobante="FACTURA")),
        total_creditos=Count("id", filter=Q(tipo_comprobante="NOTA_CREDITO")),
        sum_neto=Sum("neto"),
        sum_no_gravado=Sum("no_gravado"),
        sum_exento=Sum("exento"),
        sum_iva=Sum("iva"),
        sum_total=Sum("total"),
        sum_cobrado=Sum("cobranzascomisiones__importe")
    )

    return render(request, "ver_saldos.html", {
        "saldos": saldos,
        "totales": totales,
        "anio": anio
    })

# =====================================================
# FUNCIÓN: tendencia lineal
# =====================================================
def calcular_tendencia_lineal(valores):

    n = len(valores)

    if n < 2:
        return valores

    x = list(range(n))

    sum_x = sum(x)
    sum_y = sum(valores)
    sum_xy = sum(x[i] * valores[i] for i in range(n))
    sum_x2 = sum(x[i] ** 2 for i in range(n))

    denominador = (n * sum_x2 - sum_x ** 2)

    if denominador == 0:
        return valores

    m = (n * sum_xy - sum_x * sum_y) / denominador
    b = (sum_y - m * sum_x) / n

    return [(m * i + b) for i in x]


# =====================================================
# GRAFICOS 01 (ANUAL / TRIMESTRAL / MENSUAL)
# =====================================================
def graficos01(request):

    from django.db import connection
    import json

    tipo = request.GET.get("tipo", "anual")
    modo = request.GET.get("modo", "lineas")

    # ==========================================
    # DETECTAR MOTOR BD
    # ==========================================

    motor = connection.vendor

    if motor == "sqlite":

        trimestre_expr_fact = "CAST(((c.periodo_mes - 1) / 3 + 1) AS INTEGER)"
        trimestre_expr_dolar = "CAST(((periodo_mes - 1) / 3 + 1) AS INTEGER)"

    else:  # postgresql

        trimestre_expr_fact = "((c.periodo_mes - 1) / 3 + 1)::int"
        trimestre_expr_dolar = "((periodo_mes - 1) / 3 + 1)::int"

    # ==========================================
    # AÑOS DISPONIBLES
    # ==========================================

    anios_disponibles = list(
        ComprobantesComisiones.objects
        .values_list("periodo_anio", flat=True)
        .distinct()
        .order_by("periodo_anio")
    )

    anios_seleccionados = request.GET.getlist("anio")

    if not anios_seleccionados:

        anios_seleccionados = anios_disponibles

    else:

        anios_seleccionados = [
            int(str(a).replace(".", ""))
            for a in anios_seleccionados
        ]

    placeholders = ",".join(["%s"] * len(anios_seleccionados))

    filtro_where = f"WHERE c.periodo_anio IN ({placeholders})"

    # ==========================================
    # QUERIES
    # ==========================================

    if tipo == "mensual":

        query_facturacion = f"""
            SELECT
                c.periodo_anio,
                c.periodo_mes,
                SUM((c.neto + c.no_gravado + c.exento) / NULLIF(d.valor,0))
            FROM comprobantes_comisiones c
            JOIN cotizaciones_dolar d
              ON c.periodo_anio = d.periodo_anio
             AND c.periodo_mes = d.periodo_mes
            {filtro_where}
            GROUP BY c.periodo_anio, c.periodo_mes
            ORDER BY c.periodo_anio, c.periodo_mes;
        """

        query_dolar = f"""
            SELECT
                periodo_anio,
                periodo_mes,
                valor
            FROM cotizaciones_dolar
            WHERE periodo_anio IN ({placeholders})
            ORDER BY periodo_anio, periodo_mes;
        """

    elif tipo == "trimestral":

        query_facturacion = f"""
            SELECT 
                c.periodo_anio,
                {trimestre_expr_fact} AS trimestre,
                SUM((c.neto + c.no_gravado + c.exento) / NULLIF(d.valor,0))
            FROM comprobantes_comisiones c
            JOIN cotizaciones_dolar d
              ON c.periodo_anio = d.periodo_anio
             AND c.periodo_mes = d.periodo_mes
            {filtro_where}
            GROUP BY c.periodo_anio, trimestre
            ORDER BY c.periodo_anio, trimestre;
        """

        query_dolar = f"""
            SELECT
                periodo_anio,
                {trimestre_expr_dolar} AS trimestre,
                AVG(valor)
            FROM cotizaciones_dolar
            WHERE periodo_anio IN ({placeholders})
            GROUP BY periodo_anio, trimestre
            ORDER BY periodo_anio, trimestre;
        """

    else:  # anual

        query_facturacion = f"""
            SELECT
                c.periodo_anio,
                SUM((c.neto + c.no_gravado + c.exento) / NULLIF(d.valor,0))
            FROM comprobantes_comisiones c
            JOIN cotizaciones_dolar d
              ON c.periodo_anio = d.periodo_anio
             AND c.periodo_mes = d.periodo_mes
            {filtro_where}
            GROUP BY c.periodo_anio
            ORDER BY c.periodo_anio;
        """

        query_dolar = f"""
            SELECT
                periodo_anio,
                AVG(valor)
            FROM cotizaciones_dolar
            WHERE periodo_anio IN ({placeholders})
            GROUP BY periodo_anio
            ORDER BY periodo_anio;
        """

    # ==========================================
    # EJECUTAR
    # ==========================================

    with connection.cursor() as cursor:

        cursor.execute(query_facturacion, anios_seleccionados)
        facturacion = cursor.fetchall()

        cursor.execute(query_dolar, anios_seleccionados)
        dolar = cursor.fetchall()

    # ==========================================
    # PROCESAR
    # ==========================================

    if tipo == "mensual":

        labels = [f"{r[0]}-{r[1]:02d}" for r in facturacion]

        valores_usd = [float(r[2] or 0) for r in facturacion]

        dolar_dict = {
            f"{r[0]}-{r[1]:02d}": float(r[2] or 0)
            for r in dolar
        }

        valores_dolar = [
            dolar_dict.get(label, 0)
            for label in labels
        ]

        valores_usd_tendencia = []

    elif tipo == "trimestral":

        labels = [f"{r[0]}-T{r[1]}" for r in facturacion]

        valores_usd = [float(r[2] or 0) for r in facturacion]

        dolar_dict = {
            f"{r[0]}-T{r[1]}": float(r[2] or 0)
            for r in dolar
        }

        valores_dolar = [
            dolar_dict.get(label, 0)
            for label in labels
        ]

        valores_usd_tendencia = calcular_tendencia_lineal(valores_usd)

    else:

        labels = [str(r[0]) for r in facturacion]

        valores_usd = [float(r[1] or 0) for r in facturacion]

        dolar_dict = {
            str(r[0]): float(r[1] or 0)
            for r in dolar
        }

        valores_dolar = [
            dolar_dict.get(label, 0)
            for label in labels
        ]

        valores_usd_tendencia = []

    # ==========================================
    # RENDER
    # ==========================================

    return render(request, "graficos01.html", {

        "labels": json.dumps(labels),

        "valores_usd": json.dumps(valores_usd),

        "valores_dolar": json.dumps(valores_dolar),

        "valores_usd_tendencia": json.dumps(valores_usd_tendencia),

        "tipo": tipo,

        "modo": modo,

        "anios_disponibles": anios_disponibles,

        "anios_seleccionados": anios_seleccionados

    })



from django.shortcuts import render
from django.db import connection
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import io
import base64


def graficos02(request):

    # ===============================
    # Parámetros seguros
    # ===============================
    try:
        top_n = int(request.GET.get("top") or 5)
    except:
        top_n = 5

    try:
        tope = float(request.GET.get("tope") or 100)
    except:
        tope = 100

# ===============================
# Parámetros seguros DEFINITIVOS
# ===============================

# Top N
    top_raw = request.GET.get("top")
    try:
        top_n = int(top_raw) if top_raw else 5
    except:
        top_n = 5

# Participación Tope
    tope_raw = request.GET.get("tope")

    try:
        tope = float(tope_raw) if tope_raw not in [None, ""] else 100.0
    except:
        tope = 100.0





    # Años seleccionados
    anios_raw = request.GET.getlist("anio")
    anios_seleccionados = []

    for a in anios_raw:
        try:
            anios_seleccionados.append(int(str(a).replace(".", "")))
        except:
            pass

    # ===============================
    # Query
    # ===============================
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                c.periodo_anio,
                ((c.periodo_mes - 1) / 3 + 1)::int AS trimestre,
                a.nombre,
                SUM((c.neto + c.no_gravado + c.exento) / d.valor) AS total_usd
            FROM comprobantes_comisiones c
            JOIN aseguradoras a ON a.id = c.aseguradora_id
            JOIN cotizaciones_dolar d
              ON c.periodo_anio = d.periodo_anio
             AND c.periodo_mes = d.periodo_mes
            GROUP BY c.periodo_anio, trimestre, a.nombre
            ORDER BY c.periodo_anio, trimestre;
        """)
        rows = cursor.fetchall()

    if not rows:
        return render(request, "graficos02.html", {
            "grafico": "",
            "top_n": top_n,
            "tope": tope,
            "anios_disponibles": [],
            "anios_seleccionados": []
        })

    # ===============================
    # Organizar datos
    # ===============================
    data = {}
    anio_por_periodo = {}
    anios_disponibles = set()

    for anio, trimestre, nombre, total in rows:

        anios_disponibles.add(anio)

        if anios_seleccionados and anio not in anios_seleccionados:
            continue

        periodo = f"{anio}-T{trimestre}"

        if periodo not in data:
            data[periodo] = {}
            anio_por_periodo[periodo] = anio

        data[periodo][nombre] = float(total)

    anios_disponibles = sorted(anios_disponibles)

# Si no seleccionó años, seleccionar todos por defecto
    if not anios_seleccionados:
        anios_seleccionados = anios_disponibles.copy()


    if not data:
        return render(request, "graficos02.html", {
            "grafico": "",
            "top_n": top_n,
            "tope": tope,
            "anios_disponibles": anios_disponibles,
            "anios_seleccionados": anios_seleccionados
        })

    periodos = sorted(data.keys())

    # ===============================
    # Gráfico
    # ===============================
    fig, ax = plt.subplots(figsize=(14,6))

    palette = [
        "tab:blue","tab:orange","tab:green","tab:red",
        "tab:purple","tab:brown","tab:pink","tab:gray",
        "gold","teal","navy","coral"
    ]

    color_map = {}

    for idx, periodo in enumerate(periodos):

        trimestre_data = data[periodo]
        total_trimestre = sum(trimestre_data.values())

        participaciones = []

        for aseg, valor in trimestre_data.items():
            pct = (valor / total_trimestre) * 100 if total_trimestre > 0 else 0

            # FILTRO TOPE antes del Top N
            if pct <= tope:
                participaciones.append((aseg, valor, pct))

        participaciones.sort(key=lambda x: x[1], reverse=True)

        seleccionadas = participaciones[:top_n]

        bottom = 0

        for aseg, valor, pct in seleccionadas:

            nombre_formateado = aseg.title()

            if nombre_formateado not in color_map:
                color_map[nombre_formateado] = palette[len(color_map) % len(palette)]

            ax.bar(
                idx,
                valor,
                bottom=bottom,
                color=color_map[nombre_formateado]
            )

            texto = nombre_formateado
            if pct >= 0:
                texto += f"\n{pct:.0f}%"

            ax.text(
                idx,
                bottom + valor/2,
                texto,
                ha='center',
                va='center',
                color='white',
                fontsize=8,
                fontweight='bold'
            )

            bottom += valor

    # Separadores año
    for i in range(1, len(periodos)):
        if anio_por_periodo[periodos[i]] != anio_por_periodo[periodos[i-1]]:
            ax.axvline(x=i-0.5, linestyle="--", linewidth=1)

    ax.set_xticks(range(len(periodos)))
    ax.set_xticklabels(periodos, rotation=45)

    ax.set_title(f"Facturación trimestral en USD - Top {top_n} ≤ {tope}%")

    formatter = FuncFormatter(lambda x, _: f"{x:,.0f}")
    ax.yaxis.set_major_formatter(formatter)

    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()

    grafico = base64.b64encode(image_png).decode('utf-8')

    return render(request, "graficos02.html", {
        "grafico": grafico,
        "top_n": top_n,
        "tope": tope,
        "anios_disponibles": anios_disponibles,
        "anios_seleccionados": anios_seleccionados
    })




def importar_aseguradoras_view(request):

    resultado = None

    if request.method == "POST":
        form = ImportarExcelForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES["archivo"]
            resultado = importar_aseguradoras_excel(archivo)
    else:
        form = ImportarExcelForm()

    return render(request, "importaciones/form_importar.html", {
        "form": form,
        "resultado": resultado,
        "titulo": "Importar Aseguradoras"
    })

def grafico_indice_mensual(request):

    import io
    import base64
    from matplotlib.ticker import FuncFormatter

    # ===============================
    # Años disponibles
    # ===============================
    anios_disponibles = list(
        ComprobantesComisiones.objects
        .values_list("periodo_anio", flat=True)
        .distinct()
        .order_by("periodo_anio")
    )

    anios_raw = request.GET.getlist("anio")

    if anios_raw:
        anios_seleccionados = [
            int(str(a).replace(".", ""))
            for a in anios_raw
        ]
    else:
        anios_seleccionados = anios_disponibles.copy()

    if not anios_seleccionados:
        return render(request, "grafico_indice_mensual.html", {
            "grafico": "",
            "anios_disponibles": anios_disponibles,
            "anios_seleccionados": []
        })

    # ===============================
    # Query mensual en USD
    # (promedio mensual dólar)
    # ===============================
    placeholders = ",".join(["%s"] * len(anios_seleccionados))

    query = f"""
        SELECT
            c.periodo_anio,
            c.periodo_mes,
            SUM((c.neto + c.no_gravado + c.exento) / d.valor_promedio) AS total_usd
        FROM comprobantes_comisiones c
        JOIN (
            SELECT
                periodo_anio,
                periodo_mes,
                AVG(valor) AS valor_promedio
            FROM cotizaciones_dolar
            GROUP BY periodo_anio, periodo_mes
        ) d
          ON c.periodo_anio = d.periodo_anio
         AND c.periodo_mes = d.periodo_mes
        WHERE c.periodo_anio IN ({placeholders})
        GROUP BY c.periodo_anio, c.periodo_mes
        ORDER BY c.periodo_anio, c.periodo_mes;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, anios_seleccionados)
        rows = cursor.fetchall()

    if not rows:
        return render(request, "grafico_indice_mensual.html", {
            "grafico": "",
            "anios_disponibles": anios_disponibles,
            "anios_seleccionados": anios_seleccionados
        })

    # ===============================
    # Organizar datos
    # ===============================
    data = {}

    for anio, mes, total in rows:
        if mes not in data:
            data[mes] = {}
        data[mes][anio] = float(total or 0)

    meses_ordenados = sorted(data.keys())

    anios = sorted({
        anio for anio_dict in data.values()
        for anio in anio_dict.keys()
    })

    if 2023 not in anios:
        return render(request, "grafico_indice_mensual.html", {
            "grafico": "",
            "anios_disponibles": anios_disponibles,
            "anios_seleccionados": anios_seleccionados
        })

    # ===============================
    # Gráfico en USD reales
    # ===============================
    fig, ax = plt.subplots(figsize=(14,6))

    x = np.arange(len(meses_ordenados))
    ancho = 0.25

    meses_nombre = ["Ene","Feb","Mar","Abr","May","Jun",
                    "Jul","Ago","Sep","Oct","Nov","Dic"]

    for i, anio in enumerate(anios):

        valores_usd = [
            data[mes].get(anio, 0)
            for mes in meses_ordenados
        ]

        posiciones = x + (i - len(anios)/2)*ancho + ancho/2

        ax.bar(
            posiciones,
            valores_usd,
            width=ancho,
            label=str(anio)
        )

        # Texto USD + %
        for pos, mes, valor in zip(posiciones, meses_ordenados, valores_usd):

            base = data[mes].get(2023, 0)

            porcentaje = (valor / base) * 100 if base > 0 else 0

            if valor > 0:
                ax.text(
                    pos,
                    valor * 1.02,
                    f"USD {valor:,.0f}\n{porcentaje:.0f}%",
                    ha="center",
                    va="bottom",
                    fontsize=8
                )

    ax.set_xticks(x)
    ax.set_xticklabels([meses_nombre[m-1] for m in meses_ordenados])

    ax.set_ylabel("Facturación en USD")
    ax.set_title("Facturación Mensual en USD + % vs Base 2023")

    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        ncol=len(anios),
        frameon=False
    )


    # ===============================
    # Líneas verticales por mes
    # ===============================
    for i in range(1, len(meses_ordenados)):
        ax.axvline(
            x=i - 0.5,
            linestyle="--",
            linewidth=0.8,
            color="gray",
            alpha=0.5
        )

    # Formato eje Y con separador miles
    formatter = FuncFormatter(lambda x, _: f"{x:,.0f}")
    ax.yaxis.set_major_formatter(formatter)


    plt.subplots_adjust(bottom=0.2)
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()

    grafico = base64.b64encode(image_png).decode("utf-8")

    return render(request, "grafico_indice_mensual.html", {
        "grafico": grafico,
        "anios_disponibles": anios_disponibles,
        "anios_seleccionados": anios_seleccionados
    })