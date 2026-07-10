from django.contrib import admin
from django.urls import path, include
from comisiones.views import ver_comprobantes, ver_saldos, graficos01, graficos02, graficos22
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

urlpatterns = [

    path('', lambda request: redirect('/comprobantes/')),  # 👈 ESTA LINEA SOLUCIONA TODO

    path('admin/', admin.site.urls),
    path('comprobantes/', ver_comprobantes),
    path('saldos/', ver_saldos),
    path('graficos01/', graficos01),
    path("graficos22/", graficos22, name="graficos22"),
    path('', include('comisiones.urls')),
    path('calculadora/', include('calculadora.urls')),
    path('simulacion/', include('simulacion.urls')),
    path("finanzas/", include("finanzas.urls")),
    path("login/",    auth_views.LoginView.as_view(template_name="login.html"),    name="login",),
    path("logout/",   auth_views.LogoutView.as_view(),                             name="logout",),

]
