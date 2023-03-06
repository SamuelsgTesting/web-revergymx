from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import *

#Modelo de usuarios


class UserCreationForm(forms.ModelForm):

    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmacion de contraseña', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username','email')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden, Ingrese la misma contraseña")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        # fields = ('full_name', 'email','password', 'is_active', 'is_admin')
        fields = ('username','email','is_active', 'last_login')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.


    list_display = ('username', 'email')
    list_filter = ('is_personal','is_postulante','is_admin')

    fieldsets = (
        (None, {'fields': ('password','is_active')}),
        ('Informacion del usuario', {'fields': ('username','email', 'last_login')}),
        ('Roles', {'fields': ('is_admin','is_superuser','is_postulante','is_personal')}),
    )




    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')}
        ),
    )
    search_fields = ('email','is_admin','is_postulante','is_personal')
    ordering = ('is_admin','email')
    filter_horizontal = ()



# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.

# def desactivar_usuarios(modeladmin, request, queryset):
#     queryset.update(is_active=False)

# desactivar_usuarios.short_description = 'Desactivar Personal'

@admin.register(Analitica)
class analiticasAdmin(admin.ModelAdmin):
    search_fields = ('id_analitica', 'estatus')
    list_display = ('id_analitica','proyecto','cliente','descripcion','estatus')
    list_editable = ('estatus',)
    list_filter = ('estatus',)
    list_display_links = ('proyecto','id_analitica')

    # list_per_page = 50

# @admin.register(Gestion_parque)
# class gestionAnaliticaAdmin(admin.ModelAdmin):
#     list_display = ('id_parque','nombre_parque','fk_analitica','actividad')
#     list_filter = ('fk_analitica',)
#     list_display_links = ('fk_analitica',)
    
@admin.register(Departamento)
class departamentosAdmin(admin.ModelAdmin):
    list_display_links= ('departamento',)
    search_fields = ('departamento', 'responsable')
    list_display = ('codigo','departamento','proceso','area','responsable')

@admin.register(Puesto)
class puestoAdmin(admin.ModelAdmin):
    list_display = ('id_puesto','puesto','descripcion','fk_departamento')
    list_display_links = ('puesto',)
    list_filter = ('fk_departamento',)

@admin.register(Personal)
class personalAdmin(admin.ModelAdmin):
    search_fields = ['nombre','clave_personal', 'fk_puesto']
    list_display_links = ['nombre']
    list_editable = ['estatus']
    list_filter = ['estatus','fk_puesto']
    list_display = [
        'clave_personal',
        'nombre',
        'fk_analitica',
        'fk_puesto', 
        'alta_imss',
        'RFC',
        'NSS',
        'CURP',
        'email_personal', 
        'email_empresa', 
        'telefono_personal',
        'telefono_empresa',
        'estado_civil',
        'case_emergency',
        'contact_emergency',
        'tipo_sangre',
        'domicilio',
        'tipo_contrato',
        'duracion_contrato',
        'estatus'
        ]
    
    @admin.register(Postulante)
    class postulanteAdmin(admin.ModelAdmin):
        list_display = [ 'perfil', 'sexo','estado_civil','edad', 'telefono']
    
    @admin.register(Documento)
    class documentosAdmin(admin.ModelAdmin):
        list_display = ['clv_doc','fk_postulante','tipo','archivo','fecha_subida']