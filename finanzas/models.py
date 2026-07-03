from django.db import models

# ==========================================
# FINANZAS
# ==========================================
# Categoria
class Categoria(models.Model):

    codigo = models.CharField(
        max_length=10,
        unique=True
    )

    nombre = models.CharField(max_length=100)

    color = models.CharField(
        max_length=7,
        default="#4e79a7"
    )

    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "fin_categorias"


# Finalidad
class Finalidad(models.Model):

    codigo = models.CharField(
        max_length=20,
        unique=True
    )

    nombre = models.CharField(max_length=100)

    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "fin_finalidades"


# Persona
class Persona(models.Model):

    codigo = models.CharField(
        max_length=20,
        unique=True
    )

    nombre = models.CharField(max_length=100)

    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "fin_personas"







# TIPOS_MEDIO_PAGO
TIPOS_MEDIO_PAGO = [

    ("TC", "Tarjeta Crédito"),
    ("TD", "Tarjeta Débito"),
    ("CB", "Cuenta Bancaria"),
    ("MP", "Mercado Pago"),
    ("EF", "Efectivo"),

]

# MedioPago

class MedioPago(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "fin_medios_pago"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
