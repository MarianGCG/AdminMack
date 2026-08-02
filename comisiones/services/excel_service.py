from django.http import HttpResponse
import pandas as pd

from finanzas.models import (
    Categoria,
    Persona,
    Finalidad,
    Regla,
)

def exportar_configuracion_excel():

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response["Content-Disposition"] = (
        'attachment; filename="Configuracion.xlsx"'
    )

    with pd.ExcelWriter(response, engine="openpyxl") as writer:

        # -------------------------
        # Categorías
        # -------------------------

        datos = []

        for c in Categoria.objects.all().order_by("codigo"):

            datos.append({
                "codigo": c.codigo,
                "nombre": c.nombre,
                "color": c.color,
                "grupo_dashboard": c.grupo_dashboard,
                "mostrar_dashboard": c.mostrar_dashboard,
                "activo": c.activo,
            })

        pd.DataFrame(datos).to_excel(
            writer,
            sheet_name="Categorias",
            index=False,
        )

        # -------------------------
        # Personas
        # -------------------------

        datos = []

        for p in Persona.objects.all().order_by("codigo"):

            datos.append({
                "codigo": p.codigo,
                "nombre": p.nombre,
                "activo": p.activo,
            })

        pd.DataFrame(datos).to_excel(
            writer,
            sheet_name="Personas",
            index=False,
        )

        # -------------------------
        # Finalidades
        # -------------------------

        datos = []

        for f in Finalidad.objects.all().order_by("codigo"):

            datos.append({
                "codigo": f.codigo,
                "nombre": f.nombre,
                "activo": f.activo,
            })

        pd.DataFrame(datos).to_excel(
            writer,
            sheet_name="Finalidades",
            index=False,
        )

        # -------------------------
        # Reglas
        # -------------------------

        datos = []

        for r in Regla.objects.all().order_by("texto"):

            datos.append({
                "texto": r.texto,
                "accion": r.accion,
                "categoria": r.categoria.codigo if r.categoria else "",
                "finalidad": r.finalidad.codigo if r.finalidad else "",
                "persona": r.persona.codigo if r.persona else "",
                "grupo": r.grupo,
                "activa": r.activa,
                "observacion": r.observacion,
            })

        pd.DataFrame(datos).to_excel(
            writer,
            sheet_name="Reglas",
            index=False,
        )

    return response