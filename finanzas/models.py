from django.db import models

# ==========================================
# FINANZAS
# ==========================================
# Categoria




class Categoria(models.Model):

    GRUPOS_DASHBOARD = [
        ("INGRESOS", "Ingresos"),
        ("EGRESOS", "Egresos"),
        ("TRANSFERENCIAS", "Transferencias"),
        ("INVERSIONES", "Inversiones"),
        ("OTROS", "Otros"),
    ]

    codigo = models.CharField(
        max_length=50,
        unique=True
    )

    nombre = models.CharField(max_length=100)

    color = models.CharField(
        max_length=7,
        default="#4e79a7"
    )

    grupo_dashboard = models.CharField(
        max_length=20,
        choices=GRUPOS_DASHBOARD,
        default="EGRESOS"
    )

    mostrar_dashboard = models.BooleanField(
        default=True,
        verbose_name="Mostrar en Dashboard"
    )    

    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "fin_categorias"




# Finalidad
class Finalidad(models.Model):

    codigo = models.CharField(
        max_length=50,
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


# REGLA

class Regla(models.Model):

    ACCIONES = [
        ("C", "Clasificar"),
        ("A", "Agrupar"),
        ("I", "Ignorar"),
    ]

    texto = models.CharField(max_length=100,    unique=True)

    accion = models.CharField(
        max_length=1,
        choices=ACCIONES,
        default="C"
    )

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    finalidad = models.ForeignKey(
        Finalidad,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    persona = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    grupo = models.CharField(
        max_length=50,
        blank=True,
        default=""
    )

    activa = models.BooleanField(default=True)

    observacion = models.CharField(
        max_length=200,
        blank=True,
        default=""
    )

    class Meta:
        db_table = "fin_reglas"
        ordering = ["texto"]
        verbose_name = "Regla"
        verbose_name_plural = "Reglas"

    def __str__(self):
        return self.texto

class Movimiento(models.Model):

    fecha = models.DateField()

    periodo = models.CharField(
        max_length=6,
        blank=True,
        default="",
        db_index=True
    )
    descripcion = models.CharField(max_length=250)

    importe = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    origen = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    finalidad = models.ForeignKey(
        Finalidad,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    persona = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    regla_aplicada = models.ForeignKey(
        Regla,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    grupo = models.CharField(
        max_length=50,
        blank=True,
        default=""
    )

    observacion = models.CharField(
        max_length=250,
        blank=True,
        default=""
    )

    tipo = models.CharField(
        max_length=1,
        choices=[
            ("I", "Ingreso"),
            ("G", "Gasto"),
        ],
        default="G"
    )   

    nombre_archivo = models.CharField(
        max_length=150,
        blank=True,
        default="",
        db_index=True
    ) 

    class Meta:
        db_table = "fin_movimientos"
        ordering = ["-fecha", "-id"]
        verbose_name = "Movimiento"
        verbose_name_plural = "Movimientos"

    def __str__(self):
        return f"{self.fecha} - {self.descripcion}"
        