# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Aseguradoras(models.Model):
    nombre = models.TextField()
    cuit = models.CharField(max_length=13, blank=True, null=True)
    tipo_factura = models.CharField(max_length=1, blank=True, null=True)
    activa = models.BooleanField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    codigo_interno = models.CharField(max_length=20, blank=True, null=True)
    razon_social_afip = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'aseguradoras'



class CobranzasComisiones(models.Model):
    comprobante = models.ForeignKey('ComprobantesComisiones', models.DO_NOTHING, blank=True, null=True)
    fecha_cobro = models.DateField()
    tipo_factura = models.CharField(max_length=1, blank=True, null=True)
    numero_comprobante = models.IntegerField(blank=True, null=True)
    importe = models.DecimalField(max_digits=15, decimal_places=2)
    moneda = models.CharField(max_length=1, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.comprobante} - {self.importe}"

    class Meta:
        db_table = 'cobranzas_comisiones'


class ComprobantesComisiones(models.Model):
    aseguradora = models.ForeignKey(Aseguradoras, models.DO_NOTHING)
    fecha_comprobante = models.DateField()
    periodo_anio = models.IntegerField()
    periodo_mes = models.IntegerField()
    tipo_comprobante = models.CharField(max_length=20)
    tipo_factura = models.CharField(max_length=1)
    numero_comprobante = models.CharField(max_length=20)
    moneda = models.CharField(max_length=1, blank=True, null=True)
    neto = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    exento = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    iva = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    total = models.DecimalField(max_digits=14, decimal_places=2)
    observaciones = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    codigo_interno = models.CharField(max_length=20, blank=True, null=True)
    no_gravado = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.numero_comprobante}"
    
    class Meta:
        db_table = 'comprobantes_comisiones'
        unique_together = (('aseguradora', 'tipo_comprobante', 'tipo_factura', 'numero_comprobante', 'periodo_anio', 'periodo_mes'),)

class CotizacionesDolar(models.Model):
    periodo_anio = models.IntegerField(primary_key=True)
    periodo_mes = models.IntegerField()
    valor = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)

    class Meta:
        db_table = 'cotizaciones_dolar'
        unique_together = (('periodo_anio', 'periodo_mes'),)


