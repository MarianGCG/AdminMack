import pandas as pd

from ..models import ReglaComision, Aseguradoras


def importar_reglas_comision_excel(archivo, aseguradora_id):

    aseguradora = Aseguradoras.objects.get(id=aseguradora_id)

    # borrar reglas existentes
    ReglaComision.objects.filter(
        aseguradora_id=aseguradora_id
    ).delete()

    df = pd.read_excel(archivo)
    
    df.columns = [str(c).strip().lower() for c in df.columns]

    registros = 0
    errores = 0

    for i, row in df.iterrows():

        try:

            # ------------------------
            # ASEGURADORA
            # ------------------------

            nombre_aseg = str(row.get("aseguradora")).strip()

            if nombre_aseg == "" or nombre_aseg.lower() == "nan":
                continue

            aseguradora = Aseguradoras.objects.filter(
                nombre__iexact=nombre_aseg
            ).first()

            if not aseguradora:
                errores += 1
                continue


            # ------------------------
            # PRODUCTO
            # ------------------------

            producto = str(row.get("producto")).strip().upper()

            if producto == "" or producto.lower() == "nan":
                producto = None


            # ------------------------
            # NIVEL
            # ------------------------

            nivel = row.get("nivel")

            try:
                nivel = int(float(nivel))
            except:
                errores += 1
                continue


            # ------------------------
            # AÑO POLIZA
            # ------------------------

            anio = row.get("anio_poliza")

            if pd.isna(anio) or str(anio).strip() == "":
                anio_poliza = None
            else:
                try:
                    anio_poliza = int(float(anio))
                except:
                    anio_poliza = None


            # ------------------------
            # MONEDA
            # ------------------------

            moneda = str(row.get("moneda")).strip().upper()

            if moneda in ["U$S", "USD"]:
                moneda = "U$S"

            if moneda in ["$", "ARS"]:
                moneda = "$"

            if moneda == "" or moneda.lower() == "nan":
                moneda = None


            # ------------------------
            # RANGO
            # ------------------------

            rango = row.get("rango")

            if pd.isna(rango):
                rango = None
            else:
                rango = str(rango).strip().upper()


            # ------------------------
            # TOPE
            # ------------------------

            tope = row.get("tope")

            if pd.isna(tope) or str(tope).strip() == "":
                tope = None
            else:
                try:
                    tope = float(
                        str(tope)
                        .replace("U$S", "")
                        .replace(".", "")
                        .replace(",", ".")
                        .strip()
                    )
                except:
                    tope = None


            # ------------------------
            # PORCENTAJE
            # ------------------------

            porcentaje = row.get("porcentaje")

            if pd.isna(porcentaje):
                errores += 1
                continue

            try:
                porcentaje = float(
                    str(porcentaje)
                    .replace("%", "")
                    .replace(",", ".")
                )
            except:
                errores += 1
                continue

            # ------------------------
            # BASE COMISION
            # ------------------------

            base = str(row.get("base_comision")).strip().upper()

            if base in ["PRIMA"]:
                base_comision = "Prima"
            elif base in ["COMISION", "COMISIÓN"]:
                base_comision = "Comision"
            else:
                base_comision = "Prima"

                


            # ------------------------
            # GUARDAR
            # ------------------------

            ReglaComision.objects.update_or_create(

                aseguradora=aseguradora,
                producto=producto,
                nivel=nivel,
                anio_poliza=anio_poliza,
                moneda=moneda,
                rango=rango,
                tope=tope,

                defaults={
                    "porcentaje": porcentaje,
                    "base_comision": base_comision   # 🔥 NUEVO                    
                }

            )

            registros += 1

        except:
            errores += 1


    return f"{registros} reglas importadas - {errores} errores"