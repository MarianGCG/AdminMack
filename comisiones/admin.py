from django.contrib import admin
from .models import *

@admin.register(Aseguradoras)
class AseguradorasAdmin(admin.ModelAdmin):
    list_display = ("nombre", "cuit", "tipo_factura", "activa")
    search_fields = ("nombre", "cuit")
    ordering = ("nombre",)


@admin.register(ComprobantesComisiones)
class ComprobantesAdmin(admin.ModelAdmin):
    list_display = ("numero_comprobante", "periodo_anio", "periodo_mes", "total")
    list_filter = ("periodo_anio", "periodo_mes")
    search_fields = ("numero_comprobante",)


@admin.register(CobranzasComisiones)
class CobranzasAdmin(admin.ModelAdmin):
    list_display = ("comprobante", "fecha_cobro", "importe")
    list_filter = ("fecha_cobro",)


@admin.register(CotizacionesDolar)
class CotizacionesAdmin(admin.ModelAdmin):
    list_display = ("periodo_anio", "periodo_mes", "valor")
    ordering = ("-periodo_anio", "-periodo_mes")

