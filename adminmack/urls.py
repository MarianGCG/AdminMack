from django.contrib import admin
from django.urls import path, include
from comisiones.views import ver_comprobantes, ver_saldos, graficos01, graficos02
from django.shortcuts import redirect
urlpatterns = [

    path('', lambda request: redirect('/saldos/')),  # 👈 ESTA LINEA SOLUCIONA TODO

    path('admin/', admin.site.urls),
    path('comprobantes/', ver_comprobantes),
    path('saldos/', ver_saldos),
    path('graficos01/', graficos01),
    path('graficos02/', graficos02),

    path('', include('comisiones.urls')),
]
