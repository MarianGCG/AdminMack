from django.urls import path
from . import views

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
    path( "medios_pago/",                   views.medios_pago,          name="medios_pago"),
    path( "medio_pago-guardar/",            views.medio_pago_guardar,   name="medio_pago_guardar"),
    path( "medio_pago-eliminar/<int:id>/",  views.medio_pago_eliminar,  name="medio_pago_eliminar"),

]