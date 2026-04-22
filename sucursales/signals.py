from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import CustomUser, Sucursal

from django.db.models.signals import post_save
from .models import Actividad, Incidencia, Notificacion, CustomUser

@receiver(post_delete, sender=CustomUser)
def regenerar_codigo_lider_al_eliminar(sender, instance, **kwargs):
    if instance.rol == 'lider' and instance.sucursal:
        # Regenera el código de la sucursal donde era líder
        instance.sucursal.regenerar_codigo_lider()

@receiver(post_save, sender=Actividad)
def notificar_actividad_a_lider(sender, instance, created, **kwargs):
    if created:
        colaborador = instance.colaborador
        sucursal = colaborador.sucursal
        lider = sucursal.usuarios.filter(rol='lider').first()
        if lider:
            Notificacion.objects.create(
                destinatario=lider,
                tipo='actividad',
                titulo=f'Nueva actividad de {colaborador.username}',
                mensaje=f"El colaborador {colaborador.username} registró la actividad: {instance.titulo}",
                enlace='/actividades/'
            )

@receiver(post_save, sender=Incidencia)
def notificar_incidencia_a_staff(sender, instance, created, **kwargs):
    if created:
        # Obtener todos los usuarios con is_staff=True o rol='admin'
        staff_users = CustomUser.objects.filter(is_staff=True)
        for staff in staff_users:
            Notificacion.objects.create(
                destinatario=staff,
                tipo='incidencia',
                titulo=f'Nueva incidencia de {instance.lider.username}',
                mensaje=f"El líder {instance.lider.username} reportó: {instance.titulo}",
                enlace='/incidencias/'
            )
