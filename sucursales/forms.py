from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Sucursal, Actividad, Incidencia

# Widget personalizado para múltiples archivos
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

# Campo personalizado para múltiples archivos
class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={'multiple': True}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        # Si es una lista de archivos, limpiar cada uno
        if isinstance(data, (list, tuple)):
            return [super().clean(d, initial) for d in data]
        return super().clean(data, initial)

# Formulario de registro con código
class RegistroConCodigoForm(UserCreationForm):
    codigo = forms.CharField(max_length=50, help_text="Ingresa el código de líder o colaborador")
    TIPO_REGISTRO = (
        ('lider', 'Registrarme como líder'),
        ('colaborador', 'Registrarme como colaborador'),
    )
    tipo = forms.ChoiceField(choices=TIPO_REGISTRO, widget=forms.RadioSelect)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'tipo', 'codigo')

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        codigo = cleaned_data.get('codigo')
        if not tipo or not codigo:
            return cleaned_data

        try:
            if tipo == 'lider':
                sucursal = Sucursal.objects.get(codigo_lider=codigo)
                if CustomUser.objects.filter(rol='lider', sucursal=sucursal).exists():
                    raise forms.ValidationError("Esta sucursal ya tiene un líder asignado.")
            else:
                sucursal = Sucursal.objects.get(codigo_colaborador=codigo)
        except Sucursal.DoesNotExist:
            raise forms.ValidationError("El código ingresado no es válido.")

        cleaned_data['sucursal'] = sucursal
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = self.cleaned_data['tipo']
        user.sucursal = self.cleaned_data['sucursal']
        if commit:
            user.save()
        return user

# Formulario de Actividad con múltiples imágenes
class ActividadForm(forms.ModelForm):
    imagenes = MultipleFileField(required=False, label="Nuevas evidencias (puede seleccionar varias)")

    class Meta:
        model = Actividad
        fields = ['titulo', 'descripcion', 'fecha_actividad']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la actividad'}),
            'descripcion': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Describe la actividad...'}),
            'fecha_actividad': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

# Formulario de Incidencia con prioridad
class IncidenciaForm(forms.ModelForm):
    class Meta:
        model = Incidencia
        fields = ['titulo', 'descripcion', 'prioridad', 'resuelta']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }
