from random import choices
from secrets import choice
from django import forms
from django.forms import ModelChoiceField
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import NumberInput


class Usuario(UserCreationForm):

    class Meta:
        model = User
        fields = ('username','email')
        widgets = {
            'email': forms.EmailInput(attrs={"label": 'Ingrese el correo electronico'}),
         }

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(Usuario, self).__init__(*args, **kwargs)
 
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            forms.ValidationError('El nombre de usuario ya existe')
        return username
 
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Correo electronico ya registrado!')
        return email
 

    def clean_password2(self):

        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden, Ingrese la misma contraseña")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_postulante = True
        if commit:
            user.save()
        return user

        
class change_foto(forms.ModelForm):
    class Meta:
        model = User
        fields = ['foto',]
        

class form_analitica(forms.ModelForm):
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'rows':3}))
    
    class Meta:
        model = Analitica
        fields = ('id_analitica','proyecto','cliente','descripcion','estatus')

        
    # def __init__(self, *args, **kwargs):
    #         super().__init__(*args, **kwargs)
    #         existe = Analitica.objects.filter()
    #         if self.instance.pk:
    #             self.fields['estatus'].widget.attrs.update({'disabled': true})




class form_personal(forms.ModelForm):
    domicilio = forms.CharField(widget=forms.Textarea(attrs={'rows':3}))
    alta_imss = forms.DateField(widget=NumberInput(attrs={'type': 'date'}))

    class Meta:

        model =  Personal
        fields = ('clave_personal', 'nombre',
        'fk_analitica','fk_puesto','alta_imss',
        'RFC','NSS','CURP','email_personal','email_empresa','telefono_personal','telefono_empresa',
        'estado_civil','case_emergency','contact_emergency','tipo_sangre','domicilio',
        'tipo_contrato','duracion_contrato')

        widgets = {
            'alta_imss': forms.DateInput(attrs={'class': 'form-control'}), 
            'email_personal': forms.EmailInput(attrs={"label": 'Ingrese el correo electronico'}),
            'email_empresa': forms.EmailInput(attrs={"label": 'Ingrese el correo electronico'}),
        
        
        }
    
        

class form_edit_personal(forms.ModelForm):

    domicilio = forms.CharField(widget=forms.Textarea(attrs={'rows':3}))
    alta_imss = forms.DateField(widget=NumberInput(attrs={'type': 'date'}))
    
    class Meta:
        model = Personal
        fields = '__all__'
        widgets = {
            'email_personal': forms.EmailInput(attrs={"label": 'Ingrese el correo electronico'}),
            'email_empresa': forms.EmailInput(attrs={"label": 'Ingrese el correo electronico'}),
         
         }
        # widgets = {'alta_imss': forms.DateInput(attrs={"class": 'form-control'}) }

        

class form_postulante(forms.ModelForm):

    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if self.instance.pk:
                self.fields['correo'].widget = forms.EmailInput()

    class Meta:
        model = Postulante
        fields = '__all__'
        exclude = ('user','ine','licencia','correo','nivel')

     
    
        
#Formulario para cambiar la foto de  perfil        
class form_change_cv(forms.ModelForm):
    class Meta:
        model = Postulante
        fields = ('cv',)


class form_ine(forms.ModelForm):
    class Meta:
        model = Postulante
        fields = ('ine',)


class form_licencia(forms.ModelForm):
    class Meta:
        model = Postulante
        fields = ('licencia',)


class form_edit_postulante(forms.ModelForm):
    
    class Meta:
        model = Postulante
        fields = ('nombre','apellidos','perfil','sexo','estado_civil','edad','telefono')

  

class form_departamento(forms.ModelForm):
    class Meta:
        model = Departamento
        fields = ['area','proceso', 'departamento', 'responsable']



class form_puesto(forms.ModelForm):
    class Meta:
        model = Puesto
        fields = ['puesto','descripcion','fk_departamento']



class form_documento(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ('tipo', 'descripcion', 'archivo')
        readonly_fields = ('fk_postulante',)
        

class form_editar_oferta(forms.ModelForm):
    class Meta:
        model = Vacante
        fields = '__all__'



class form_vacante(forms.ModelForm):
    class Meta:
        model = Vacante
        fields = ('perfil', 'descripcion', 'fk_puesto','formacion','experiencia','salario','jornada','is_prioridad')

    def __init__(self, *args, **kwargs):
        super(form_vacante, self).__init__(*args, **kwargs)
        # Agregar el atributo 'required' al campo name
        print(self.instance.perfil)



class form_edit_vacante(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(form_edit_vacante, self).__init__(*args, **kwargs)

        # Agregar el atributo 'required' al campo name
        # if self.instance.is_postulante:

        #     self.fields['perfil'].widget.attrs['disabled'] = True
        # else: self.fields['perfil'].widget.attrs['disabled'] = False

           
        

    class Meta:
        model = Vacante
        fields = ('perfil', 'descripcion', 'fk_puesto','formacion','experiencia','salario','jornada','is_prioridad','estatus')
    

class form_asignacion_proyecto(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        proyecto_id = kwargs.pop('proyecto_id', None)
        departamento_id = kwargs.pop('departamento_id', None)
        super(form_asignacion_proyecto, self).__init__(*args, **kwargs)

        if departamento_id:
            self.fields['tecnico'].queryset = Personal.objects.filter(estatus='Activo',fk_puesto__fk_departamento_id=departamento_id)
            self.fields['proyecto'].initial = Proyecto_cliente.objects.get(pk=proyecto_id)
         
    
    class Meta:
        model = Asignacion_personal
        fields= ('proyecto','tecnico','lugar')
        widgets = {
        'proyecto': forms.HiddenInput(
                attrs={
                    'readonly': False
          })
        }


class form_entrevista(forms.ModelForm):

    class Meta:
        model = Entrevista
        fields = '__all__'



class form_entrevista_rh(forms.ModelForm):
    q16 = forms.ChoiceField(choices= Departamento.objects.values_list('area','area').distinct(), label="Seleccione area a postularse")



    def __init__(self, *args, **kwargs):
    
        super(form_entrevista_rh, self).__init__(*args, **kwargs)
        if self.instance.pk and self.instance.aceptar_terminos:
                print("hola")
       

    class Meta:
        model = Question_rh
        fields = '__all__'
        exclude = ('entrevista',)


class form_entrevista_psicologica(forms.ModelForm):

    class Meta:
        model = Question_psicologico
        fields = '__all__'
        exclude = ('entrevista',)

    
class form_proyecto_OYM(forms.ModelForm):
 
    fecha_inicio = forms.DateField(widget=NumberInput(attrs={'type': 'date'}), label= 'Fecha Inicio de Proyecto')
    fecha_fin = forms.DateField(widget=NumberInput(attrs={'type': 'date'}), label= 'Fecha Fin de Proyecto')

    def __init__(self, *args, **kwargs):
        super(form_proyecto_OYM, self).__init__(*args, **kwargs)

        self.fields['departamento'].queryset = Departamento.objects.filter(area='OPERACION Y MANTENIMIENTO')
        self.fields['analitica'].queryset = Analitica.objects.filter(estatus ='Activo')
        self.fields['cliente'].queryset = Analitica.objects.filter(estatus ='Activo').values_list('cliente','cliente').distinct()


    class Meta:
        model = Proyecto_cliente
        fields = '__all__'
        exclude = ('estatus',)



class form_eventos(forms.ModelForm):

    event_name = models.CharField(max_length=255,null=True,blank=True, verbose_name='Nombre del evento')
    start_date = forms.DateTimeField(widget=NumberInput(attrs={'type': 'datetime-local'}), label= 'Inicio Evento')
    end_date = forms.DateTimeField(widget=NumberInput(attrs={'type': 'datetime-local'}), label='Fin Evento', 
    help_text='*Si el evento se realizara en un solo dia OMITA este campo')
    description = forms.CharField(widget=forms.Textarea(attrs={'rows':3}), label= 'Descripcion')

    class Meta:
        model = Evento
        fields = '__all__'
  
        

class form_oferta(forms.ModelForm):
    class Meta:
        Model = Vacante
        fields = ['perfil','fk_puesto','descripcion']

class edit_usuario(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','email']


class change_password(UserCreationForm):
    class Meta:
        model = User
        fields =  ('password1', 'password2')
