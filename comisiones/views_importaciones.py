from django.shortcuts import render, redirect
from .forms import ImportarExcelForm
from .models import Aseguradoras, ComprobantesComisiones

from .services.dolar_service import importar_cotizaciones_excel
from .services.aseguradoras_service import importar_aseguradoras_excel
from .services.comprobantes_arca_service import importar_comprobantes_arca
from .services.cobranzas_service import importar_cobranzas_excel


# ================================
# IMPORTAR DÓLAR
# ================================
def importar_dolar_view(request):

    resultado = None

    if request.method == "POST":
        form = ImportarExcelForm(request.POST, request.FILES)

        if form.is_valid():
            archivo = request.FILES["archivo"]
            resultado = importar_cotizaciones_excel(archivo)
    else:
        form = ImportarExcelForm()

    return render(
        request,
        "importaciones/form_importar.html",
        {
            "form": form,
            "resultado": resultado,
            "titulo": "Importar cotizaciones dólar"
        }
    )


# ================================
# LISTAR ASEGURADORAS
# ================================
def listar_aseguradoras_view(request):

    aseguradoras = Aseguradoras.objects.all().order_by("nombre")

    return render(
        request,
        "importaciones/listar_aseguradoras.html",
        {
            "aseguradoras": aseguradoras,
            "titulo": "Listado de Aseguradoras"
        }
    )


# ================================
# IMPORTAR ASEGURADORAS
# ================================



def aseguradoras_view(request):

    resultado = None

    if request.method == "POST":
        form = ImportarExcelForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES["archivo"]
            resultado = importar_aseguradoras_excel(archivo)
    else:
        form = ImportarExcelForm()

    aseguradoras = Aseguradoras.objects.all().order_by("nombre")

    # 🔎 Filtros
    nombre = request.GET.get("nombre")
    estado = request.GET.get("estado")

    if nombre:
        aseguradoras = aseguradoras.filter(nombre__icontains=nombre)

    if estado == "activas":
        aseguradoras = aseguradoras.filter(activa=True)

    elif estado == "inactivas":
        aseguradoras = aseguradoras.filter(activa=False)

    return render(
        request,
        "importaciones/aseguradoras.html",
        {
            "form": form,
            "resultado": resultado,
            "aseguradoras": aseguradoras,
        }
    )


# ================================
# ACTIVAR ASEGURADORA
# ================================


def activar_aseguradora(request, id):

    aseguradora = Aseguradoras.objects.get(id=id)

    # guardar color si viene
    color = request.POST.get("color")
    if color:
        aseguradora.color = color

    aseguradora.activa = True
    aseguradora.save()

    return redirect("aseguradoras")




# ================================
# ELIMINAR / DESACTIVAR ASEGURADORA
# ================================
def eliminar_o_desactivar_aseguradora(request, id):

    aseguradora = Aseguradoras.objects.get(id=id)

    tiene_movimientos = ComprobantesComisiones.objects.filter(
        aseguradora_id=aseguradora.id
    ).exists()

    if tiene_movimientos:
        aseguradora.activa = False
        aseguradora.save()
    else:
        aseguradora.delete()

    return redirect("aseguradoras")


# ================================
# IMPORTAR COMPROBANTES ARCA
# ================================
def importar_comprobantes_arca_view(request):

    resultado = None

    if request.method == "POST":
        archivo = request.FILES.get("archivo")

        if archivo:
            resultado = importar_comprobantes_arca(archivo)

    return render( request, "importaciones/comprobantes_arca.html", {"resultado": resultado }
    )

def importar_cobranzas_view(request):

    resultado = None

    if request.method == "POST":
        archivo = request.FILES.get("archivo")

        if archivo:
            resultado = importar_cobranzas_excel(archivo)

    return render(
        request,
        "importaciones/cobranzas.html",
        {
            "resultado": resultado
        }
    )

