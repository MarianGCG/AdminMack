from django.contrib import admin
from django.urls import path, include
from comisiones.views import ver_comprobantes, ver_saldos, graficos01, graficos02

urlpatterns = [

    path('admin/', admin.site.urls),

    path('comprobantes/', ver_comprobantes),
    path('saldos/', ver_saldos),
    path('graficos01/', graficos01),
    path('graficos02/', graficos02),

    # ESTA línea conecta TODO comisiones.urls
    path('', include('comisiones.urls')),

]