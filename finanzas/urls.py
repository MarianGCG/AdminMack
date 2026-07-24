from django.urls import path
from . import views
from . import views_importaciones

urlpatterns = [
  
    path( "categorias/",                    views.categorias,           name="categorias"),
    path( "categoria-guardar/",             views.categoria_guardar,    name="categoria_guardar"),
    path( "categoria-eliminar/<int:id>/",   views.categoria_eliminar,   name="categoria_eliminar"),
    path( "finalidades/",                   views.finalidades,          name="finalidades"),
    path( "finalidad-guardar/",             views.finalidad_guardar,    name="finalidad_guardar"),
    path( "finalidad-eliminar/<int:id>/",   views.finalidad_eliminar,   name="finalidad_eliminar"),
    path( "personas/",                      views.personas,             name="personas"),
    path( "persona-guardar/",               views.persona_guardar,      name="persona_guardar"),
    path( "persona-eliminar/<int:id>/",     views.persona_eliminar,     name="persona_eliminar"),
    path("reglas/",                         views.reglas,               name="reglas"),
    path("regla-guardar/",                  views.regla_guardar,        name="regla_guardar"),
    path("regla-eliminar/<int:id>/",        views.regla_eliminar,       name="regla_eliminar"),
    path("movimientos/",                    views.movimientos,          name="movimientos"    ),
    path("movimiento-guardar/",             views.movimiento_guardar,   name="movimiento_guardar"    ),
    path("movimiento-eliminar/<int:id>/",   views.movimiento_eliminar,  name="movimiento_eliminar"    ),
    path("movimiento-importar/",            views_importaciones.importar_movimientos_view,   name="movimiento_importar"),
    path("movimiento-actualizar/",          views.movimiento_actualizar,name="movimiento_actualizar" ),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("eliminar_resumen/",  views.eliminar_resumen,   name="eliminar_resumen",),
    path("movimientos/exportar_excel/",    views.movimientos_exportar_excel,    name="movimientos_exportar_excel"),  
    path(
        "regla-json/<int:id>/",
        views.regla_json,
        name="regla_json",
    ),
    path(
        "regla-movimiento/<int:id>/",
        views.regla_movimiento,
        name="regla_movimiento"
    ),
    path(
        "desvincular-regla/<int:id>/",
        views.desvincular_regla,
        name="desvincular_regla",
    ),

]