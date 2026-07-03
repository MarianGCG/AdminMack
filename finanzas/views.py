from django.shortcuts import render

from .models import Categoria, Finalidad, Persona, MedioPago
from django.http import JsonResponse
import json
from django.views.decorators.http import require_GET



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


def medios_pago(request):

    medios_pago = MedioPago.objects.order_by("nombre")

    return render(
        request,
        "finanzas/medios_pago.html",
        {
            "medios_pago": medios_pago
        }
    )


def medio_pago_guardar(request):

    if request.method != "POST":
        return JsonResponse({"ok": False})

    datos = json.loads(request.body)

    id = datos.get("id")

    if id:
        medio_pago = MedioPago.objects.get(id=id)
    else:
        medio_pago = MedioPago()

    medio_pago.codigo = datos.get("codigo")
    medio_pago.nombre = datos.get("nombre")
    medio_pago.activo = datos.get("activo")
    medio_pago.save()

    return JsonResponse({"ok": True})


def medio_pago_eliminar(request, id):

    MedioPago.objects.filter(id=id).delete()

    return JsonResponse({"ok": True})
