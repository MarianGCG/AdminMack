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
    path("aseguradoras/actualizar-grupo/<int:id>/", views_importaciones.actualizar_grupo_aseguradora, name="actualizar_grupo_aseguradora"),    
    path("importaciones/comprobantes-arca/",   importar_comprobantes_arca_view, name="importar_comprobantes_arca" ),
    path("importaciones/cobranzas/", importar_cobranzas_view, name="importar_cobranzas"),
    path("grafico-indice-mensual/", views.grafico_indice_mensual, name="grafico_indice_mensual"),
    path("parametros/", views.parametros_view, name="parametros"),
    path("parametros/nuevo/", views.parametro_nuevo_view, name="parametro_nuevo"),
    path("parametros/editar/<int:id>/", views.parametro_editar_view, name="parametro_editar"),
    path("parametros/eliminar/<int:id>/", views.parametro_eliminar_view, name="parametro_eliminar"),
]

