from django.urls import path
from . import views
from . import views_importaciones
from .views_importaciones import importar_comprobantes_arca_view
from .views_importaciones import importar_cobranzas_view

urlpatterns = [

    # Importaciones
    path("importar-dolar/", views_importaciones.importar_dolar_view, name="importar_dolar"),
    path("aseguradoras/",  views_importaciones.aseguradoras_view,  name="aseguradoras"),
    path("aseguradoras/activar/<int:id>/",     views_importaciones.activar_aseguradora,   name="activar_aseguradora"),
    path("aseguradoras/eliminar/<int:id>/",    views_importaciones.eliminar_o_desactivar_aseguradora,  name="eliminar_aseguradora"),
    path("importaciones/comprobantes-arca/",   importar_comprobantes_arca_view, name="importar_comprobantes_arca" ),
    path("importaciones/cobranzas/", importar_cobranzas_view, name="importar_cobranzas"),
    path("grafico-indice-mensual/", views.grafico_indice_mensual, name="grafico_indice_mensual"),
]
