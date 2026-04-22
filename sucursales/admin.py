from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Sucursal, Incidencia

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'rol', 'sucursal', 'is_staff')
    list_filter = ('rol', 'sucursal', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {'fields': ('rol', 'sucursal')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información adicional', {'fields': ('rol', 'sucursal')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

class SucursalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo_lider', 'codigo_colaborador')
    readonly_fields = ('codigo_lider', 'codigo_colaborador')
    search_fields = ('nombre',)
    actions = ['regenerar_codigos']

    def regenerar_codigos(self, request, queryset):
        for sucursal in queryset:
            sucursal.regenerar_codigo_lider()
            # Si quieres también regenerar el de colaborador, agrega un método
        self.message_user(request, "Códigos de líder regenerados para las sucursales seleccionadas.")
    regenerar_codigos.short_description = "Regenerar código de líder"

admin.site.register(Sucursal, SucursalAdmin)

class IncidenciaAdmin(admin.ModelAdmin):
    list_display = ('lider', 'titulo', 'fecha_creacion', 'resuelta')
    search_fields = ('lider',)

admin.site.register(Incidencia, IncidenciaAdmin)
