from django.db import models
import os
from django.conf import settings

# Create your models here.

from django.contrib.auth.models import AbstractUser
import secrets

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(unique=True)
    ROLES = (
        ('admin', 'Administrador'),
        ('lider', 'Líder'),
        ('colaborador', 'Colaborador'),
    )
    rol = models.CharField(max_length=20, choices=ROLES, default='colaborador')
    # Relación con sucursal (solo para líderes y colaboradores)
    sucursal = models.ForeignKey(
        'Sucursal', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='usuarios'
    )

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"

class Sucursal(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.TextField()
    codigo_lider = models.CharField(max_length=50, unique=True, blank=True)
    codigo_colaborador = models.CharField(max_length=50, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.codigo_lider:
            self.codigo_lider = self._generar_codigo()
        if not self.codigo_colaborador:
            self.codigo_colaborador = self._generar_codigo()
        super().save(*args, **kwargs)

    def _generar_codigo(self):
        # Genera código único de 12 caracteres alfanuméricos
        return secrets.token_urlsafe(12)
    
    def regenerar_codigo_colaborador(self):
        self.codigo_colaborador = self._generar_codigo()
        self.save(update_fields=['codigo_colaborador'])


    def regenerar_codigo_lider(self):
        self.codigo_lider = self._generar_codigo()
        self.save(update_fields=['codigo_lider'])

    def __str__(self):
        return self.nombre

class Actividad(models.Model):
    colaborador = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'rol': 'colaborador'}, related_name='actividades')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actividad = models.DateField()
    # Puedes agregar campos como horas trabajadas, tipo, etc.

    class Meta:
        ordering = ['-fecha_actividad', '-fecha_creacion']
    
    def delete(self, *args, **kwargs):
        for ev in self.evidencias.all():
            ev.delete()  # Esto eliminará las imágenes asociadas
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.colaborador.username} - {self.titulo} ({self.fecha_actividad})"

class Evidencia(models.Model):
    actividad = models.ForeignKey('Actividad', on_delete=models.CASCADE, related_name='evidencias')
    imagen = models.ImageField(upload_to='evidencias/')
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    subido_en = models.DateTimeField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        if self.imagen:
            ruta_imagen = os.path.join(settings.MEDIA_ROOT, self.imagen.name)
            if os.path.isfile(ruta_imagen):
                os.remove(ruta_imagen)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Evidencia de {self.actividad.titulo}"


class Incidencia(models.Model):
    PRIORIDAD_CHOICES = (
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    )
    lider = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'rol': 'lider'}, related_name='incidencias')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    resuelta = models.BooleanField(default=False)
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media')

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.titulo} ({self.get_prioridad_display()})"

class Notificacion(models.Model):
    TIPOS = (
        ('actividad', 'Nueva actividad'),
        ('incidencia', 'Nueva incidencia'),
    )
    destinatario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=20, choices=TIPOS)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    enlace = models.CharField(max_length=200, blank=True, null=True)  # URL a la que lleva al hacer clic
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.titulo} para {self.destinatario.username}"
