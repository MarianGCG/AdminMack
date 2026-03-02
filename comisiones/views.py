from django.shortcuts import render, redirect
from django.db.models import Sum, Count, Q, DecimalField, Value
from django.db.models.functions import Coalesce, Cast

from django.db import connection
from .models import ComprobantesComisiones
import json
from .services.aseguradoras_service import importar_aseguradoras_excel
from .services.parametros_service import get_parametro

from django.db.models.functions import Cast
from django.db.models import IntegerField



import numpy as np
from django.http import HttpResponse
from io import BytesIO

from .models import ParametroSistema


import io
import base64



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
# =====================================================
# GRAFICOS 01 (ANUAL / TRIMESTRAL / MENSUAL)
# =====================================================
# =====================================================
# GRAFICOS 01 (ANUAL / TRIMESTRAL / MENSUAL)
# =====================================================


# =====================================================
# GRAFICOS 01 (ANUAL / TRIMESTRAL / MENSUAL)
# =====================================================
# =====================================================
# GRAFICOS 01 (ANUAL / TRIMESTRAL / MENSUAL)
# =====================================================

{% extends "base.html" %}
{% load l10n %}
{% block content %}

<div class="titulo-grafico">
    Evolución Facturación en USD
</div>

<style>
.barra-controles {
    display:flex;
    flex-direction:column;
    gap:8px;
    margin-bottom:10px;
    font-size:13px;
}

.grupo {
    display:flex;
    align-items:flex-start;
    gap:10px;
    flex-wrap:wrap;
}

.grupo-anios{
    flex-direction:column;
    align-items:flex-start;
}

.contenedor-anios{
    display:grid;
    grid-template-columns: repeat(auto-fill, minmax(70px, 1fr));
    gap:4px 12px;
    max-width:420px;
}

.anio-item{
    font-size:13px;
}

.fila-final{
    display:flex;
    justify-content:space-between;
    align-items:center;
}

.lado-der{
    margin-left:auto;
}

.contenedor-grafico {
    height: calc(100vh - 170px);
    width:100%;
}
</style>

<form method="get" class="barra-controles">

    <div class="grupo">
        <b>Periodo:</b>
        <label><input type="radio" name="tipo" value="mensual" {% if tipo == "mensual" %}checked{% endif %}>Mensual</label>
        <label><input type="radio" name="tipo" value="trimestral" {% if tipo == "trimestral" %}checked{% endif %}>Trimestral</label>
        <label><input type="radio" name="tipo" value="anual" {% if tipo == "anual" %}checked{% endif %}>Anual</label>
    </div>

    <div class="grupo">
        <b>Modo:</b>
        <label><input type="radio" name="modo" value="lineas" {% if modo == "lineas" %}checked{% endif %}>Líneas</label>
        <label><input type="radio" name="modo" value="barras" {% if modo == "barras" %}checked{% endif %}>Barras</label>
    </div>

    <div class="grupo grupo-anios">
        <b>Años:</b>
        <div class="contenedor-anios">
            {% for anio in anios_disponibles %}
                <label class="anio-item">
                    <input type="checkbox" name="anio"
                           value="{{ anio|unlocalize }}"
                           {% if anio in anios_seleccionados %}checked{% endif %}>
                    {{ anio|unlocalize }}
                </label>
            {% endfor %}
        </div>
    </div>

    <div class="grupo fila-final">

        <div>
            <button type="submit"
                style="padding:3px 10px;background:#2c78be;color:white;border:none;border-radius:4px;cursor:pointer;">
                Actualizar
            </button>
        </div>

        <div class="lado-der">
            <label>
                <input type="checkbox" name="desglose" value="1"
                       onchange="this.form.submit();"
                       {% if desglose %}checked{% endif %}>
                Desglose aseguradoras
            </label>
        </div>

    </div>

</form>

<div id="legend-container" style="font-size:12px;margin-bottom:8px;"></div>

<div class="contenedor-grafico">
    <canvas id="grafico"></canvas>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<script>

const labels = {{ labels|safe }};
const datasets = {{ datasets|safe }};
const tipo = "{{ tipo }}";
const modo = "{{ modo }}";
const desglose = {{ desglose|yesno:"true,false" }};
const gruposDeshabilitados = {{ grupos_deshabilitados|default:"[]"|safe }};

let chart = null;


// =============================
// FORMATEAR LABELS
// =============================

function formatearLabel(label)
{
    if(tipo==="mensual")
    {
        const mes = label.split("-")[1];
        const nombres = ["Ene","Feb","Mar","Abr","May","Jun",
                         "Jul","Ago","Sep","Oct","Nov","Dic"];
        return nombres[parseInt(mes)-1];
    }

    if(tipo==="trimestral")
        return label.split("-")[1];

    return label;
}


// =============================
// PLUGIN LINEAS CAMBIO AÑO
// =============================

const lineasCambioAnio = {
    id: "lineasCambioAnio",
    afterDraw(chart){

        if(tipo !== "mensual") return;

        const {ctx, chartArea:{top,bottom}} = chart;
        let ultimoAnio = null;

        labels.forEach((label,index)=>{

            const anio = label.split("-")[0];

            if(ultimoAnio && anio !== ultimoAnio){

                const meta = chart.getDatasetMeta(0);
                if(!meta || !meta.data[index]) return;

                const x = meta.data[index].x;

                ctx.save();
                ctx.beginPath();
                ctx.moveTo(x, top);
                ctx.lineTo(x, bottom);
                ctx.strokeStyle = "#cccccc";
                ctx.lineWidth = 1;
                ctx.stroke();
                ctx.restore();
            }

            ultimoAnio = anio;
        });
    }
};


// =============================
// PLUGIN NOMBRE ASEGURADORA
// =============================

const mostrarNombreLinea = {
    id: "mostrarNombreLinea",
    afterDatasetsDraw(chart){

        if(!desglose) return;
        if(modo !== "lineas") return;

        const { ctx } = chart;

        chart.data.datasets.forEach((dataset, datasetIndex) => {

            if(dataset.hidden) return;

            const meta = chart.getDatasetMeta(datasetIndex);
            if (!meta || meta.data.length === 0) return;

            const punto = meta.data[0];

            let nombre = dataset.label.substring(0,10);

            ctx.save();
            ctx.font = "bold 11px Arial";
            ctx.fillStyle = dataset.borderColor;
            ctx.textAlign = "right";

            ctx.fillText(
                nombre,
                punto.x - 8,
                punto.y
            );

            ctx.restore();
        });
    }
};


// =============================
// CREAR GRAFICO
// =============================

function crearGrafico()
{
    if(chart) chart.destroy();

    datasets.forEach(ds=>{
        if(gruposDeshabilitados.includes(ds.grupo)){
            ds.hidden = true;
        }
    });

    chart = new Chart(document.getElementById("grafico"), {

        type: modo==="barras" ? "bar" : "line",

        data: {
            labels: labels,
            datasets: datasets
        },

        options: {
            responsive:true,
            maintainAspectRatio:false,
            plugins: {
                tooltip: { enabled: tipo==="mensual" },
                legend: { display: !desglose }
            },
            scales: {
                x: {
                    ticks:{
                        autoSkip:false,
                        callback:(value,index)=>{
                            const label = labels[index];
                            const mes = formatearLabel(label);
                            const anio = label.split("-")[0];

                            if(index===0) return mes + "\n" + anio;

                            const anioAnterior = labels[index-1].split("-")[0];

                            if(anio !== anioAnterior)
                                return mes + "\n" + anio;

                            return mes;
                        }
                    }
                }
            }
        },

        plugins: [lineasCambioAnio, mostrarNombreLinea]
    });

    if(desglose)
        generarLeyendaAgrupada(chart);
}


// =============================
// LEYENDA AGRUPADA
// =============================

function generarLeyendaAgrupada(chart)
{
    const container = document.getElementById("legend-container");
    container.innerHTML = "";

    const grupos = {};

    chart.data.datasets.forEach((ds,index)=>{
        const grupo = ds.grupo || "Sin Grupo";

        if(!grupos[grupo])
            grupos[grupo] = [];

        grupos[grupo].push({ index, ds });
    });

    Object.keys(grupos).sort().forEach(grupo=>{

        const divGrupo = document.createElement("div");
        divGrupo.style.marginBottom = "6px";

        const titulo = document.createElement("strong");
        titulo.innerText = grupo + "  ";
        titulo.style.cursor = "pointer";
        titulo.style.marginRight = "12px";

        divGrupo.appendChild(titulo);

        grupos[grupo].forEach(item=>{

            const span = document.createElement("span");

            let nombre = item.ds.label.substring(0,10).padEnd(10," ");

            span.innerText = nombre;
            span.style.display = "inline-block";
            span.style.width = "110px";
            span.style.textAlign = "center";
            span.style.fontFamily = "monospace";
            span.style.marginRight = "6px";
            span.style.cursor = "pointer";
            span.style.backgroundColor = item.ds.borderColor;
            span.style.color = "black";
            span.style.borderRadius = "4px";
            span.style.padding = "2px 6px";

            if(item.ds.hidden){
                span.style.textDecoration = "line-through";
                span.style.opacity = "0.5";
            }

            span.onclick = ()=>{
                item.ds.hidden = !item.ds.hidden;
                chart.update();
                generarLeyendaAgrupada(chart);
            };

            divGrupo.appendChild(span);
        });

        container.appendChild(divGrupo);
    });
}

crearGrafico();

</script>

{% endblock %}




def graficos02(request):

    import io
    import base64
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    from django.db import connection

    from .services.parametros_service import get_parametro

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
        tope = 100.0


    # ===============================
    # QUERY
    # ===============================

    with connection.cursor() as cursor:

        cursor.execute("""
            SELECT
                c.periodo_anio,
                ((c.periodo_mes - 1) / 3 + 1)::int AS trimestre,
                a.nombre,
                COALESCE(a.color, '#3366cc') AS color,
                SUM((c.neto + c.no_gravado + c.exento) / d.valor) AS total_usd

            FROM comprobantes_comisiones c

            JOIN aseguradoras a
                ON a.id = c.aseguradora_id

            JOIN cotizaciones_dolar d
                ON c.periodo_anio = d.periodo_anio
                AND c.periodo_mes = d.periodo_mes

            GROUP BY
                c.periodo_anio,
                trimestre,
                a.nombre,
                a.color

            ORDER BY
                c.periodo_anio,
                trimestre;
        """)

        rows = cursor.fetchall()


    # ===============================
    # Sin datos
    # ===============================

    if not rows:

        return render(request, "graficos02.html", {
            "grafico": "",
            "top_n": top_n,
            "tope": tope,
            "anios_disponibles": [],
            "anios_seleccionados": []
        })


    # ===============================
    # Años disponibles
    # ===============================

    anios_disponibles = sorted(list({
        row[0] for row in rows
    }))


    # ===============================
    # Años seleccionados (GET o DEFAULT PARAMETRO)
    # ===============================

    anios_raw = request.GET.getlist("anio")

    if anios_raw:

        anios_seleccionados = []

        for a in anios_raw:
            try:
                anios_seleccionados.append(int(str(a).replace(".", "")))
            except:
                pass

    else:

        cantidad_default = int(get_parametro("CANTIDAD_ANIOS_DEFAULT", 5))

        cantidad_default = min(cantidad_default, len(anios_disponibles))

        anios_seleccionados = anios_disponibles[-cantidad_default:]


    # ===============================
    # Organizar datos (FILTRANDO AÑOS)
    # ===============================

    data = {}
    anio_por_periodo = {}
    color_map = {}

    for anio, trimestre, nombre, color, total in rows:

        if anio not in anios_seleccionados:
            continue

        periodo = f"{anio}-T{trimestre}"

        if periodo not in data:

            data[periodo] = {}
            anio_por_periodo[periodo] = anio

        data[periodo][nombre] = float(total)

        color_map[nombre] = color


    # ===============================
    # Si no hay datos luego del filtro
    # ===============================

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
    # GRÁFICO
    # ===============================

    fig, ax = plt.subplots(figsize=(14,6))


    for idx, periodo in enumerate(periodos):

        trimestre_data = data[periodo]

        total_trimestre = sum(trimestre_data.values())

        participaciones = []

        for aseg, valor in trimestre_data.items():

            pct = (valor / total_trimestre) * 100 if total_trimestre > 0 else 0

            if pct <= tope:
                participaciones.append((aseg, valor, pct))

        participaciones.sort(key=lambda x: x[1], reverse=True)

        seleccionadas = participaciones[:top_n]

        bottom = 0

        for aseg, valor, pct in seleccionadas:

            color = color_map.get(aseg, "#3366cc")

            ax.bar(
                idx,
                valor,
                bottom=bottom,
                color=color
            )

            texto = aseg.title()

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


    # ===============================
    # Separadores de año
    # ===============================

    for i in range(1, len(periodos)):

        if anio_por_periodo[periodos[i]] != anio_por_periodo[periodos[i-1]]:

            ax.axvline(
                x=i-0.5,
                linestyle="--",
                linewidth=1,
                color="gray"
            )


    ax.set_xticks(range(len(periodos)))
    ax.set_xticklabels(periodos, rotation=45)

    ax.set_title(f"Facturación trimestral en USD - Top {top_n} ≤ {tope}%")

    formatter = FuncFormatter(lambda x, _: f"{x:,.0f}")
    ax.yaxis.set_major_formatter(formatter)

    plt.tight_layout()


    # ===============================
    # Convertir a imagen
    # ===============================

    buffer = io.BytesIO()

    plt.savefig(buffer, format='png')

    buffer.seek(0)

    grafico = base64.b64encode(buffer.getvalue()).decode('utf-8')

    buffer.close()

    plt.close()


    # ===============================
    # Render
    # ===============================

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
    import matplotlib.pyplot as plt
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

    from .services.parametros_service import get_parametro

    anios_raw = request.GET.getlist("anio")

    if anios_raw:

        anios_seleccionados = []

        for a in anios_raw:
            try:
                anios_seleccionados.append(int(str(a).replace(".", "")))
            except:
                pass

    else:

        cantidad_default = int(get_parametro("CANTIDAD_ANIOS_DEFAULT", 5))

        anios_seleccionados = anios_disponibles[-cantidad_default:]
        
        


        
    # ===============================
    # Año base dinámico desde parámetros
    # ===============================
    from .services.parametros_service import get_parametro

    anio_base_raw = request.GET.get("anio_base")

    if anio_base_raw:

        anio_base = int(str(anio_base_raw).replace(".", ""))

    else:

        anio_base_param = get_parametro("ANIO_BASE_INDICE")

        if anio_base_param is not None:

            anio_base = int(anio_base_param)

        else:

            anio_base = anios_disponibles[0]
                

    # ===============================
    # Query
    # ===============================
    placeholders = ",".join(["%s"] * len(anios_seleccionados))

    query = f"""
        SELECT
            c.periodo_anio,
            c.periodo_mes,
            SUM((c.neto + c.no_gravado + c.exento) / d.valor_promedio)
        FROM comprobantes_comisiones c
        JOIN (
            SELECT periodo_anio, periodo_mes, AVG(valor) AS valor_promedio
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
            "anios_seleccionados": anios_seleccionados,
            "anio_base": anio_base
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

    # ===============================
    # Gráfico
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

        ax.bar(posiciones, valores_usd, width=ancho, label=str(anio))

        # TEXTO
        for pos, mes, valor in zip(posiciones, meses_ordenados, valores_usd):

            base = data[mes].get(anio_base, 0)

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

    ax.set_title(f"Facturación Mensual en USD + % vs Base {anio_base}")

    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        ncol=len(anios),
        frameon=False
    )

    formatter = FuncFormatter(lambda x, _: f"{x:,.0f}")
    ax.yaxis.set_major_formatter(formatter)

    plt.subplots_adjust(bottom=0.2)
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)

    grafico = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return render(request, "grafico_indice_mensual.html", {
        "grafico": grafico,
        "anios_disponibles": anios_disponibles,
        "anios_seleccionados": anios_seleccionados,
        "anio_base": anio_base
    })




def parametros_view(request):

    parametros = ParametroSistema.objects.all().order_by("codigo")

    return render(
        request,
        "parametros.html",
        {
            "parametros": parametros
        }
    )


def parametro_nuevo(request):

    if request.method == "POST":

        codigo = request.POST.get("codigo").strip().upper()
        valor = request.POST.get("valor")
        descripcion = request.POST.get("descripcion")

        ParametroSistema.objects.update_or_create(
            codigo=codigo,
            defaults={
                "valor": valor,
                "descripcion": descripcion
            }
        )

        return redirect("parametros")

    return render(request, "parametro_nuevo.html")



from django.shortcuts import render, redirect, get_object_or_404
from .models import ParametroSistema


# ============================
# LISTAR
# ============================

def parametros_view(request):

    parametros = ParametroSistema.objects.all().order_by("codigo")

    return render(request, "parametros.html", {
        "parametros": parametros
    })


# ============================
# NUEVO
# ============================

def parametro_nuevo_view(request):

    if request.method == "POST":

        codigo = request.POST.get("codigo").strip()
        valor = request.POST.get("valor").strip()
        descripcion = request.POST.get("descripcion").strip()

        ParametroSistema.objects.create(
            codigo=codigo,
            valor=valor,
            descripcion=descripcion
        )

        return redirect("parametros")

    return render(request, "parametro_form.html", {
        "modo": "nuevo"
    })


# ============================
# EDITAR
# ============================

def parametro_editar_view(request, id):

    parametro = get_object_or_404(ParametroSistema, id=id)

    if request.method == "POST":

        parametro.valor = request.POST.get("valor").strip()
        parametro.descripcion = request.POST.get("descripcion").strip()

        parametro.save()

        return redirect("parametros")

    return render(request, "parametro_form.html", {
        "modo": "editar",
        "parametro": parametro
    })


# ============================
# ELIMINAR
# ============================

def parametro_eliminar_view(request, id):

    parametro = get_object_or_404(ParametroSistema, id=id)

    parametro.delete()

    return redirect("parametros")







def graficos22(request):

    import json
    from django.db import connection
    from django.shortcuts import render

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
        tope = 100.0


    # ===============================
    # QUERY
    # ===============================

    with connection.cursor() as cursor:

        cursor.execute("""
            SELECT
                c.periodo_anio,
                ((c.periodo_mes - 1) / 3 + 1)::int AS trimestre,
                a.nombre,
                COALESCE(a.color, '#3366cc') AS color,
                SUM((c.neto + c.no_gravado + c.exento) / d.valor) AS total_usd

            FROM comprobantes_comisiones c

            JOIN aseguradoras a ON a.id = c.aseguradora_id

            JOIN cotizaciones_dolar d
              ON c.periodo_anio = d.periodo_anio
             AND c.periodo_mes = d.periodo_mes

            GROUP BY
                c.periodo_anio,
                trimestre,
                a.nombre,
                a.color

            ORDER BY
                c.periodo_anio,
                trimestre;
        """)

        rows = cursor.fetchall()


    if not rows:

        return render(request, "graficos22.html", {
            "labels": "[]",
            "datasets": "[]",
            "totales": "[]",
            "top_n": top_n,
            "tope": tope,
            "anios_disponibles": [],
            "anios_seleccionados": []
        })


    # ===============================
    # Años disponibles
    # ===============================

    anios_disponibles = sorted(list({row[0] for row in rows}))


    # ===============================
    # Años seleccionados
    # default = últimos 4 años
    # ===============================

    anios_raw = request.GET.getlist("anio")

    if anios_raw:

        anios_seleccionados = []

        for a in anios_raw:
            try:
                anios_seleccionados.append(int(str(a)))
            except:
                pass

    else:

        anios_seleccionados = anios_disponibles[-4:]


    # ===============================
    # Organizar datos
    # ===============================

    data = {}
    color_map = {}

    for anio, trimestre, nombre, color, total in rows:

        if anio not in anios_seleccionados:
            continue

        periodo = f"{anio}-T{trimestre}"

        if periodo not in data:
            data[periodo] = {}

        data[periodo][nombre] = float(total)
        color_map[nombre] = color


    periodos = sorted(data.keys())


    # ===============================
    # Totales reales
    # ===============================

    totales_periodo = []

    for periodo in periodos:
        totales_periodo.append(sum(data.get(periodo, {}).values()))


    # ===============================
    # Datasets por posición
    # ===============================

    datasets = []

    for pos in range(top_n):

        datasets.append({
            "label": f"pos{pos}",
            "data": [],
            "backgroundColor": [],
            "labels": [],
            "stack": "stack1"
        })


    for periodo in periodos:

        trimestre_data = data.get(periodo, {})
        total_trimestre = sum(trimestre_data.values())

        participaciones = []

        for aseg, valor in trimestre_data.items():

            pct = (valor / total_trimestre) * 100 if total_trimestre else 0

            if pct <= tope:
                participaciones.append((aseg, valor, pct))

        participaciones.sort(key=lambda x: x[1], reverse=True)

        seleccionadas = participaciones[:top_n]


        for pos in range(top_n):

            if pos < len(seleccionadas):

                aseg, valor, pct = seleccionadas[pos]

                datasets[pos]["data"].append(valor)
                datasets[pos]["backgroundColor"].append(
                    color_map.get(aseg, "#3366cc")
                )
                datasets[pos]["labels"].append(aseg)

            else:

                datasets[pos]["data"].append(0)
                datasets[pos]["backgroundColor"].append("rgba(0,0,0,0)")
                datasets[pos]["labels"].append("")


    # ===============================
    # Render FINAL
    # ===============================

    return render(request, "graficos22.html", {

        "labels": json.dumps(periodos),
        "datasets": json.dumps(datasets),
        "totales": json.dumps(totales_periodo),

        "top_n": top_n,
        "tope": tope,

        "anios_disponibles": anios_disponibles,
        "anios_seleccionados": anios_seleccionados

    })