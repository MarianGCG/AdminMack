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
        managed = False
        db_table = 'aseguradoras'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


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
        managed = False
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
        managed = False
        db_table = 'comprobantes_comisiones'
        unique_together = (('aseguradora', 'tipo_comprobante', 'tipo_factura', 'numero_comprobante', 'periodo_anio', 'periodo_mes'),)

class CotizacionesDolar(models.Model):
    periodo_anio = models.IntegerField(primary_key=True)
    periodo_mes = models.IntegerField()
    valor = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cotizaciones_dolar'
        unique_together = (('periodo_anio', 'periodo_mes'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
