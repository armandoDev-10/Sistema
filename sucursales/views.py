from django.shortcuts import render, redirect

# Create your views here.
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied


from .forms import RegistroConCodigoForm

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.utils import timezone
from .models import Actividad, Incidencia, Evidencia
from .forms import ActividadForm, IncidenciaForm
from django.contrib import messages
from django.db.models import Q

from django.http import JsonResponse
from .models import Notificacion

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

def registro(request):
    if request.method == 'POST':
        form = RegistroConCodigoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = RegistroConCodigoForm()
    return render(request, 'registration/registro.html', {'form': form})

@login_required
def perfil(request):
    return render(request, 'perfil.html', {'user': request.user})

# Helper de roles
def es_colaborador(user):
    return user.rol == 'colaborador'

def es_lider(user):
    return user.rol == 'lider'

@login_required
@user_passes_test(es_lider)
def regenerar_codigo_colaborador(request):
    lider = request.user
    sucursal = lider.sucursal
    if sucursal:
        sucursal.regenerar_codigo_colaborador()
        messages.success(request, 'El código para registro de colaboradores ha sido regenerado exitosamente.')
    else:
        messages.error(request, 'No tienes una sucursal asignada.')
    return redirect('perfil')


# ================= ACTIVIDADES =================
@login_required
@user_passes_test(es_colaborador)
def crear_actividad(request):
    if request.method == 'POST':
        form = ActividadForm(request.POST, request.FILES)
        if form.is_valid():
            actividad = form.save(commit=False)
            actividad.colaborador = request.user
            actividad.save()
            # Procesar múltiples imágenes
            imagenes = request.FILES.getlist('imagenes')
            for img in imagenes:
                Evidencia.objects.create(actividad=actividad, imagen=img)
            messages.success(request, 'Actividad registrada correctamente.')
            return redirect('lista_actividades')
    else:
        form = ActividadForm()
    return render(request, 'actividades/crear_actividad.html', {'form': form})


@login_required
def lista_actividades(request):
    user = request.user
    if user.rol == 'colaborador':
        actividades = Actividad.objects.filter(colaborador=user)
    elif user.rol == 'lider':
        # Ver actividades de todos los colaboradores de su misma sucursal
        actividades = Actividad.objects.filter(colaborador__sucursal=user.sucursal)
    else:
        actividades = Actividad.objects.none()  # admin no usa esta vista
    return render(request, 'actividades/lista_actividades.html', {'actividades': actividades})


@login_required
@user_passes_test(es_lider)
def detalle_actividad(request, pk):
    actividad = get_object_or_404(Actividad, pk=pk)
    # Verificar que la actividad pertenezca a un colaborador de la sucursal del líder
    if actividad.colaborador.sucursal != request.user.sucursal:
        raise PermissionDenied("No tienes permiso para ver esta actividad.")
    evidencias = actividad.evidencias.all()
    return render(request, 'actividades/detalle_actividad.html', {
        'actividad': actividad,
        'evidencias': evidencias
    })

@login_required
@user_passes_test(es_colaborador)
def editar_actividad(request, pk):
    actividad = get_object_or_404(Actividad, pk=pk, colaborador=request.user)
    if request.method == 'POST':
        form = ActividadForm(request.POST, request.FILES, instance=actividad)
        if form.is_valid():
            actividad = form.save()
            # Procesar nuevas imágenes (se agregan a las existentes)
            nuevas_imagenes = request.FILES.getlist('imagenes')
            for img in nuevas_imagenes:
                Evidencia.objects.create(actividad=actividad, imagen=img)
            messages.success(request, 'Actividad actualizada correctamente.')
            return redirect('lista_actividades')
    else:
        form = ActividadForm(instance=actividad)
    return render(request, 'actividades/editar_actividad.html', {'form': form, 'actividad': actividad})

@login_required
def eliminar_actividad(request, pk):
    actividad = get_object_or_404(Actividad, pk=pk)
    usuario = request.user
    
    # Verificar permisos:
    # - Colaborador: solo sus propias actividades
    # - Líder: actividades de colaboradores de su misma sucursal
    if usuario.rol == 'colaborador':
        if actividad.colaborador != usuario:
            raise PermissionDenied("No tienes permiso para eliminar esta actividad.")
    elif usuario.rol == 'lider':
        if actividad.colaborador.sucursal != usuario.sucursal:
            raise PermissionDenied("No tienes permiso para eliminar actividades de otra sucursal.")
    else:
        raise PermissionDenied("No tienes permiso para realizar esta acción.")
    
    if request.method == 'POST':
        actividad.delete()
        messages.success(request, 'Actividad eliminada correctamente.')
        return redirect('lista_actividades')
    return render(request, 'actividades/eliminar_actividad.html', {'actividad': actividad})

@login_required
def eliminar_evidencia(request, pk):
    evidencia = get_object_or_404(Evidencia, pk=pk, actividad__colaborador=request.user)
    evidencia.delete()
    messages.success(request, 'Imagen eliminada.')
    return redirect('editar_actividad', pk=evidencia.actividad.pk)


@login_required
@user_passes_test(es_lider)
def reporte_actividades_sucursal(request):
    # Reporte cronológico de todas las actividades de la sucursal del líder
    sucursal = request.user.sucursal
    actividades = Actividad.objects.filter(colaborador__sucursal=sucursal).order_by('fecha_actividad', 'fecha_creacion')
    # Opción para exportar a CSV o texto plano
    if 'exportar' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="reporte_actividades_{sucursal.nombre}_{timezone.now().date()}.csv"'
        import csv
        writer = csv.writer(response)
        writer.writerow(['Colaborador', 'Título', 'Descripción', 'Fecha actividad', 'Registrado el'])
        for act in actividades:
            writer.writerow([act.colaborador.username, act.titulo, act.descripcion, act.fecha_actividad, act.fecha_creacion])
        return response
    return render(request, 'actividades/reporte_sucursal.html', {'actividades': actividades, 'sucursal': sucursal})

# ================= INCIDENCIAS =================
@login_required
@user_passes_test(es_lider)
def crear_incidencia(request):
    if request.method == 'POST':
        form = IncidenciaForm(request.POST)
        if form.is_valid():
            incidencia = form.save(commit=False)
            incidencia.lider = request.user
            incidencia.save()
            messages.success(request, 'Incidencia creada.')
            return redirect('lista_incidencias')
    else:
        form = IncidenciaForm()
    return render(request, 'incidencias/crear_incidencia.html', {'form': form})

@login_required
@user_passes_test(es_lider)
def lista_incidencias(request):
    incidencias = Incidencia.objects.filter(lider=request.user)
    return render(request, 'incidencias/lista_incidencias.html', {'incidencias': incidencias})

@login_required
@user_passes_test(es_lider)
def editar_incidencia(request, pk):
    incidencia = get_object_or_404(Incidencia, pk=pk, lider=request.user)
    if request.method == 'POST':
        form = IncidenciaForm(request.POST, instance=incidencia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Incidencia actualizada.')
            return redirect('lista_incidencias')
    else:
        form = IncidenciaForm(instance=incidencia)
    return render(request, 'incidencias/editar_incidencia.html', {'form': form, 'incidencia': incidencia})

@login_required
def mis_notificaciones(request):
    notificaciones = Notificacion.objects.filter(destinatario=request.user, leida=False).order_by('-fecha_creacion')
    return render(request, 'notificaciones/lista.html', {'notificaciones': notificaciones})

@login_required
def historial_notificaciones(request):
    notificaciones = Notificacion.objects.filter(destinatario=request.user).order_by('-fecha_creacion')
    return render(request, 'notificaciones/historial.html', {'notificaciones': notificaciones})

@login_required
def marcar_como_leida(request, pk):
    notificacion = get_object_or_404(Notificacion, pk=pk, destinatario=request.user)
    notificacion.leida = True
    notificacion.save()
    messages.success(request, 'Notificación marcada como leída.')
    return redirect('mis_notificaciones')

@login_required
def contar_no_leidas(request):
    count = Notificacion.objects.filter(destinatario=request.user, leida=False).count()
    return JsonResponse({'count': count})
