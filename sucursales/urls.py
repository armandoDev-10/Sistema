from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registro/', views.registro, name='registro'),
    path('perfil/', views.perfil, name='perfil'),
    # Recuperación de contraseña
    path('reset-password/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt'
    ), name='password_reset'),
    path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    path('actividad/crear/', views.crear_actividad, name='crear_actividad'),
    path('actividades/', views.lista_actividades, name='lista_actividades'),
    path('actividades/reporte/', views.reporte_actividades_sucursal, name='reporte_actividades'),
    path('actividad/<int:pk>/', views.detalle_actividad, name='detalle_actividad'),

    path('actividad/editar/<int:pk>/', views.editar_actividad, name='editar_actividad'),
    path('actividad/eliminar/<int:pk>/', views.eliminar_actividad, name='eliminar_actividad'),
    path('evidencia/eliminar/<int:pk>/', views.eliminar_evidencia, name='eliminar_evidencia'),
    
    path('incidencia/crear/', views.crear_incidencia, name='crear_incidencia'),
    path('incidencias/', views.lista_incidencias, name='lista_incidencias'),
    path('incidencia/editar/<int:pk>/', views.editar_incidencia, name='editar_incidencia'),

    path('notificaciones/', views.mis_notificaciones, name='mis_notificaciones'),
    path('notificacion/marcar/<int:pk>/', views.marcar_como_leida, name='marcar_notificacion'),
    path('api/notificaciones/count/', views.contar_no_leidas, name='contar_notificaciones'),
    path('notificaciones/historial/', views.historial_notificaciones, name='historial_notificaciones'),

    path('regenerar-codigo-colaborador/', views.regenerar_codigo_colaborador, name='regenerar_codigo_colaborador'),
]
