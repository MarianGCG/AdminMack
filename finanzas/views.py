from django.shortcuts import render

from .models import Movimiento, Categoria, Finalidad, Persona,  Regla
from comisiones.models import ParametroSistema
from django.http import JsonResponse
import json
from django.views.decorators.http import require_GET
from .services.movimientos_service import importar_movimientos,  buscar_regla, actualizar_movimientos
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Sum
@require_GET
def categoria_eliminar(request, id):

    Categoria.objects.filter(id=id).delete()

    return JsonResponse({"ok": True})


def categorias(request):
    categorias = Categoria.objects.order_by("nombre")



    return render(
        request,
        "finanzas/categorias.html",
        {
            "categorias": categorias
        }
    )

def categoria_guardar(request):

    if request.method != "POST":
        return JsonResponse({"ok": False})

    datos = json.loads(request.body)

    id = datos.get("id")

    if id:
        categoria = Categoria.objects.get(id=id)
    else:
        categoria = Categoria()

    categoria.codigo = datos.get("codigo")
    categoria.nombre = datos.get("nombre")
    categoria.color = datos.get("color")
    categoria.activo = datos.get("activo")

    categoria.save()

    return JsonResponse({"ok": True})


def finalidades(request):

    finalidades = Finalidad.objects.order_by("nombre")

    return render(
        request,
        "finanzas/finalidades.html",
        {
            "finalidades": finalidades
        }
    )

def finalidad_guardar(request):

    if request.method != "POST":
        return JsonResponse({"ok": False})

    datos = json.loads(request.body)

    id = datos.get("id")

    if id:
        finalidad = Finalidad.objects.get(id=id)
    else:
        finalidad = Finalidad()

    finalidad.codigo = datos.get("codigo")
    finalidad.nombre = datos.get("nombre")
    finalidad.activo = datos.get("activo")

    finalidad.save()

    return JsonResponse({"ok": True})

def finalidad_eliminar(request, id):

    Finalidad.objects.filter(id=id).delete()

    return JsonResponse({"ok": True})





def personas(request):

    personas = Persona.objects.order_by("nombre")

    return render(
        request,
        "finanzas/personas.html",
        {
            "personas": personas
        }
    )

def persona_guardar(request):

    if request.method != "POST":
        return JsonResponse({"ok": False})

    datos = json.loads(request.body)

    id = datos.get("id")

    if id:
        persona = Persona.objects.get(id=id)
    else:
        persona = Persona()

    persona.codigo = datos.get("codigo")
    persona.nombre = datos.get("nombre")
    persona.activo = datos.get("activo")
    persona.save()

    return JsonResponse({"ok": True})



def persona_eliminar(request, id):

    Persona.objects.filter(id=id).delete()

    return JsonResponse({"ok": True})





# ==========================================
# REGLAS
# ==========================================




def reglas(request):

    reglas = Regla.objects.order_by("texto")

    popup = request.GET.get("popup") == "1"

    return render(
        request,
        "finanzas/reglas.html",
        {
            "reglas": reglas,
            "categorias": Categoria.objects.order_by("nombre"),
            "finalidades": Finalidad.objects.order_by("nombre"),
            "personas": Persona.objects.order_by("nombre"),
            "parametros": ParametroSistema.objects.filter(valor="REGLA").order_by("codigo"),
            "popup": popup,
        }
    )


def regla_guardar(request):

    print("******** ENTRO A REGLA_GUARDAR ********")

    if request.method != "POST":
        return JsonResponse({"ok": False})

    datos = json.loads(request.body)
    print(datos)
    id = datos.get("id")

    if id:
        regla = Regla.objects.get(id=id)
    else:
        regla = Regla()

    regla.texto = datos.get("texto")
    regla.accion = datos.get("accion")

    regla.categoria_id = datos.get("categoria") or None
    regla.finalidad_id = datos.get("finalidad") or None
    regla.persona_id = datos.get("persona") or None

    regla.grupo = datos.get("grupo", "")

    regla.activa = datos.get("activo")
    regla.observacion = datos.get("observacion", "")

    regla.save()

    # ---------------------------------
    # Reaplicar reglas automáticamente
    # ---------------------------------
    actualizar_movimientos()

    return JsonResponse({
        "ok": True,
        "cerrar": True
    })

def regla_eliminar(request, id):

    Regla.objects.filter(id=id).delete()

    return JsonResponse({"ok": True})


# ==========================================
# MOVIMIENTOS
# ==========================================

def movimientos(request):

    movimientos = Movimiento.objects.select_related(
        "categoria",
        "finalidad",
        "persona",
        "regla_aplicada",
    )

    # ------------------------
    # FILTROS
    # ------------------------

    periodo = request.GET.get("periodo", "")
    if periodo:
        movimientos = movimientos.filter(periodo=periodo)
        
    categoria = request.GET.get("categoria")

    if categoria:
        movimientos = movimientos.filter(
            categoria_id=categoria
        )

    finalidad = request.GET.get("finalidad")

    if finalidad:
        movimientos = movimientos.filter(
            finalidad_id=finalidad
        )

    persona = request.GET.get("persona")

    if persona:
        movimientos = movimientos.filter(
            persona_id=persona
        )

        

    # ------------------------
    # ORDEN
    # ------------------------

    orden = request.GET.get("orden")

    if orden:
        movimientos = movimientos.order_by(orden)
    else:
        orden = "-periodo"
        movimientos = movimientos.order_by(
            "-periodo",
            "-regla_aplicada",
            "-fecha"
        )

    periodos = (
        Movimiento.objects
        .exclude(periodo="")
        .values("periodo")
        .distinct()
        .order_by("-periodo")
    )

    # =====================================
    # RESUMEN POR ORIGEN
    # =====================================

    resumen_origen = (
        movimientos
        .values("origen")
        .annotate(
            cantidad=Count("id"),
            total=Sum("importe")
        )
        .order_by("origen")
    )

    totales = movimientos.aggregate(
        cantidad=Count("id"),
        total=Sum("importe")
    )

    return render(
        request,
        "finanzas/movimientos.html",
        {

            "movimientos": movimientos,

            "categorias": Categoria.objects.all(),
            "finalidades": Finalidad.objects.all(),
            "personas": Persona.objects.all(),

            "periodos": periodos,
            "orden": orden,

            # NUEVO
            "resumen_origen": resumen_origen,
            "totales": totales,

        }
    )

def movimiento_guardar(request):

    return JsonResponse({"ok": True})


def movimiento_eliminar(request, id):

    return JsonResponse({"ok": True})


def movimiento_importar(request):

    if request.method != "POST":
        return JsonResponse({
            "ok": False,
            "error": "Método no permitido"
        })

    archivo = request.FILES.get("archivo")

    if not archivo:
        return JsonResponse({
            "ok": False,
            "error": "No se recibió ningún archivo"
        })

    try:

        mensaje = importar_movimientos(archivo)

        return JsonResponse({
            "ok": True,
            "mensaje": mensaje
        })

    except Exception as e:

        return JsonResponse({
            "ok": False,
            "error": str(e)
        })




def movimiento_actualizar(request):

    actualizar_movimientos()

    return redirect("movimientos")