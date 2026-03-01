from django.contrib import admin
from django.urls import path, include
from comisiones.views import ver_comprobantes, ver_saldos, graficos01, graficos02, graficos22
from django.shortcuts import redirect
urlpatterns = [

    path('', lambda request: redirect('/saldos/')),  # 👈 ESTA LINEA SOLUCIONA TODO

    path('admin/', admin.site.urls),
    path('comprobantes/', ver_comprobantes),
    path('saldos/', ver_saldos),
    path('graficos01/', graficos01),
    path("graficos22/", graficos22, name="graficos22"),
    path('', include('comisiones.urls')),
]
