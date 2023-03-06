from datetime import datetime
from pickle import FALSE, TRUE
from pyexpat import model
from django.db import models
from django.contrib.auth.models import Group
from time import *
from time import strftime, localtime
from .choises import *
from django.contrib.auth.models import AbstractBaseUser ,BaseUserManager

#Clases creacion de usuarios del sistema

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):

        if not email:
            raise ValueError('Los usuarios deben tener una dirección de correo electrónico')
        user = self.model( email=self.normalize_email(email), username = username) 
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_admin(self, email, username, password):

        user = self.create_user(email,  username = username, password=password,)
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):

    username = models.CharField(max_length = 200, null = FALSE, verbose_name= 'Nombre de usuario')
    email = models.EmailField(verbose_name = 'Correo', max_length = 225, unique = True)
    is_active = models.BooleanField(default = True, verbose_name= 'Activo?')
    is_superuser = models.BooleanField(default=False, verbose_name= 'Superusuario')
    is_admin = models.BooleanField(default = False, verbose_name= 'Administrador')
    is_personal = models.BooleanField(default = False, verbose_name= 'Personal')
    is_postulante = models.BooleanField(default= False, verbose_name= 'Postulante')
    foto = models.ImageField(upload_to='uploads/perfiles/update/', default='uploads/perfiles/log/personal.png', null= TRUE, verbose_name= 'Foto de perfil')
    objects = UserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ['username',]

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = ' Usuarios'


    def __str__(self):
        return str(self.username)

    def has_perm (self, perm, obj = None):
        # "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        # Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property   
    def is_staff(self): 
        return self.is_admin

@property   
def create_admin(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user
    

class Analitica(models.Model):
    id_analitica = models.CharField(primary_key=TRUE,max_length=30, verbose_name='Analitica', 
    help_text='Es el codigo homologado enviado por Revergy España')
    proyecto = models.CharField(max_length=70, verbose_name= 'Proyecto', null= False, help_text= 'Nombre del lugar donde reside el proyecto')
    cliente = models.CharField(max_length=30, help_text= 'Nombre del cliente a realizar los servicios')
    descripcion = models.TextField(max_length=100, default='')
    estatus = models.CharField(choices=ESTATUS, default='Activo',max_length=15, help_text='Estado actual del proyecto, si es alta omitir este campo')
    
    class Meta:
        verbose_name = 'Analitica'
        verbose_name_plural = ' Analiticas'

    def analiticas_activas(self):
        return "{}".format(self.id_analitica)
    def __str__(self):
        return self.analiticas_activas()

    
class Departamento(models.Model):
    codigo = models.AutoField(primary_key=TRUE, verbose_name= 'Codigo departamento')
    area = models.CharField(max_length=50, verbose_name='Area', choices=AREAS, null= False, default= 'OPERACIÓN Y MANTENIMIENTO')
    proceso = models.CharField(max_length=60, choices = PROCESO, verbose_name='Proceso', default= 'OPERATIVO')
    departamento = models.CharField(max_length=60)
    responsable = models.CharField(max_length=30)

    def nombre_departamento(self):
       return "{}".format(self.departamento)
    def __str__(self):
        return self.nombre_departamento()


class Puesto(models.Model):
   id_puesto = models.AutoField(primary_key=TRUE)
   puesto = models.CharField(max_length =30, null= TRUE)
   descripcion = models.CharField(max_length =30, null= TRUE)
   fk_departamento = models.ForeignKey(Departamento,on_delete=models.CASCADE, verbose_name='Departamento')
   fecha_registro = models.DateField(auto_now=TRUE,)

   def nombre_puesto(self):
       return "{}".format(self.puesto)

   def __str__(self):
       return self.nombre_puesto()

class Personal(models.Model):

    clave_personal = models.CharField(primary_key=True, max_length=30)
    nombre = models.CharField(max_length=100, verbose_name= 'Nombre Completo')
    fk_analitica = models.ForeignKey(Analitica,on_delete=models.CASCADE, verbose_name='Analitica')
    fk_puesto = models.ForeignKey(Puesto, on_delete= models.CASCADE, verbose_name='Puesto', null= False)
    alta_imss = models.DateField(null=TRUE, verbose_name='Fecha de alta IMSS')
    RFC = models.CharField(max_length=30, null= TRUE)
    NSS = models.CharField(max_length=30, null = TRUE)
    CURP = models.CharField(max_length=30, null= TRUE)
    email_personal = models.EmailField(max_length=50, verbose_name= 'Email personal', blank=TRUE, null= TRUE)
    email_empresa = models.EmailField(max_length=50, verbose_name= 'Email empresa', blank=TRUE, null= TRUE)
    telefono_personal = models.CharField(max_length=15, blank=TRUE, null= TRUE)
    telefono_empresa = models.CharField(max_length=15, blank=TRUE, null= TRUE)
    estado_civil = models.CharField(max_length=50, choices= ESTADOS_CIVILES, default= 'Soltero(a)', verbose_name= 'Estado civil',null= TRUE)
    case_emergency = models.CharField(max_length=100, verbose_name= 'En caso de emergencia', null= TRUE)
    contact_emergency = models.CharField(max_length=15,verbose_name= 'Contacto de emergencia', null= TRUE)
    tipo_sangre = models.CharField(max_length=50, choices=TIPOS_SANGRE, default= 'A positivo (A +)', verbose_name= 'Tipo de sangre', null= TRUE)
    domicilio = models.TextField(max_length=150, null= TRUE, verbose_name='Domicilio')
    tipo_contrato = models.CharField(max_length=30, verbose_name='Tipo de contrato', null= TRUE, blank=TRUE)
    duracion_contrato = models.CharField(max_length=15, verbose_name= 'Tiempo de contrato', null= TRUE, blank=TRUE)
    estatus = models.CharField(max_length=15, choices=ESTATUS, verbose_name= 'Estatus', default= 'Activo')

    def codigo_personal(self):
       return "{}_{}".format(self.clave_personal, self.nombre)

    def __str__(self):
        return self.codigo_personal()

    class Meta:
        verbose_name = 'Personal'
        verbose_name_plural = ' Personal'
        ordering=["estatus"]
    
    

class  Vacante(models.Model):
    id_vacante = models.AutoField(primary_key=True)
    perfil = models.CharField(max_length=100, null= False, default= '')
    fk_puesto = models.ForeignKey(Puesto, on_delete= models.CASCADE, verbose_name= 'Puesto')
    tarjeta = models.ImageField(upload_to='cards/ofertas/procesos/', max_length=255, null= False, default='cards/ofertas/procesos/operativo.png')
    is_new = models.BooleanField(default=True, null= False)
    is_prioridad = models.BooleanField(default=False, null= False, verbose_name='Es prioridad ?')
    is_top = models.BooleanField(verbose_name='Desea destacar esta oferta?', null= False, default= False)
    descripcion = models.TextField(null= False, help_text= 'Breve descipcion de las funciones, obligacions, y fundamentos de la oferta')
    formacion = models.TextField(null= True, default='', help_text= 'Informacion academica requerida (Titulos, Certificados, Cursos, etc)')
    experiencia = models.TextField(null= True, default='',
    help_text= 'Experiencia laboral requerida (Conocimientos Tecnicos, antecendetes en algun trabajo o empresa, etc)')
    salario = models.CharField(max_length=100, default= '', null= True, verbose_name= 'Salario bruto')
    jornada = models.CharField(max_length=100, default='Tiempo completo',  verbose_name= 'Tipo de jornada laboral')
    tipo_contrato = models.CharField(max_length=100, default='', null= True, verbose_name= 'Tipo de contrato')
    estatus = models.CharField(max_length=30,choices= ESTATUS, default='Activo')
    fecha_creacion = models.DateTimeField(auto_now=TRUE,)

    def vacante_config(self):
       return "{}".format(self.fk_puesto)

    def __str__(self):
        return self.vacante_config()

def upload_cv(instance,fielname):
    return 'uploads/documentos/CV/CV.%s.pdf' % (instance.user)

def upload_ine(instance,fielname):
    return 'uploads/documentos/INE/INE.%s.pdf' % (instance.user)

def upload_licencia(instance,fielname):
    return 'uploads/documentos/LICENCIA/LICENCIA.%s.pdf' % (instance.user)


class Postulante(models.Model):

    user = models.OneToOneField(User,on_delete= models.CASCADE, primary_key=True)
    nombre = models.CharField(max_length=60, null= False , verbose_name= 'Nombre(s)')
    apellidos = models.CharField(max_length=80, null= False, verbose_name= 'Apellidos')
    perfil = models.CharField(max_length=60, null= False, verbose_name= 'Perfil profesional', help_text='Ingrese su perfil de especializacion')
    correo = models.EmailField(max_length=60, null= False, verbose_name= 'Correo de contacto')
    cv = models.FileField(upload_to=upload_cv, verbose_name="CV", help_text="Adjunte su Curruculum")
    ine = models.FileField(upload_to=upload_ine, verbose_name="INE",null=True, help_text="Adjunte su Identificacion personal(INE)")
    licencia = models.FileField(upload_to=upload_licencia, null=True,verbose_name="LICENCIA DE CONDUCIR", help_text="Adjunte su Licencia de manejo")
    sexo = models.CharField(max_length= 15, choices= SEXO, verbose_name='Sexo')
    estado_civil = models.CharField(max_length=20, choices= ESTADOS_CIVILES, verbose_name='Estado civil')
    edad = models.IntegerField(null= False, default= 18, verbose_name= 'Edad')
    nivel = models.IntegerField(default=1, verbose_name= 'Nivel')
    telefono = models.CharField(max_length=15,null= False, blank= False, verbose_name= 'Telefono personal')

    def postulante_config(self):
       return "{} {}".format(self.nombre, self.apellidos)


    def __str__(self):
        return self.postulante_config()
    class Meta:
        verbose_name = 'Postulante'
        verbose_name_plural = ' Postulantes'




# Subclase para edicion de documentos

def upload_to(instance, fielname):
    sub = fielname.split('.')[-1]
    t = strftime('%Y%m%d%H%M%S', localtime())
    return 'uploads/documentos/%s/%s.%s.%s.%s' % (instance.tipo,instance.fk_postulante_id,instance.tipo,t,sub)


class Documento(models.Model):

    clv_doc = models.AutoField(primary_key=True)
    fk_postulante = models.ForeignKey(Postulante, on_delete= models.CASCADE, verbose_name='Postulante', default= '')
    tipo = models.CharField(max_length=30, null=False, choices= TIPO_DOCUMENTO)
    descripcion = models.CharField(max_length=120, null= False, verbose_name= 'Descripcion', default='', help_text= 'Breve informacion acerca del reconocimiento abquirido')
    archivo = models.FileField(upload_to = upload_to, max_length=255,null= TRUE, help_text = 'Solo puede seleccionar archivos pdf', verbose_name = 'Archivo', )
    fecha_subida = models.DateField(auto_now=TRUE,)

    def doc_config(self):
        filename = self.archivo.name.split("/")[-1]
        return "{}".format(filename)

    def __str__(self):
        return self.doc_config()
    

class Solicitud_vacante(models.Model):
    clv_solicitud = models.AutoField(primary_key= True)
    fk_postulante = models.ForeignKey(Postulante, on_delete= models.CASCADE, verbose_name='Postulante')
    fk_vacante = models.ForeignKey(Vacante, on_delete= models.CASCADE, verbose_name='Vacante', default= '')
    fecha = models.DateField(auto_now=TRUE,)
    estatus = models.CharField(max_length=30, null=False, default= 'Pendiente')


    class meta:
        db_table = 'postulante_postula_vacantes'
        verbose_name = 'Solcitud Postulante'
        verbose_name_plural = 'Solicitudes Postulantes'
    
    def __str__(self):
        return "{}({})".format(self.fk_postulante,self.fk_vacante)


class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=80, verbose_name= 'Nombre categoria')
    

    def __str__(self):
        return "{}".format(self.nombre)


class Entrevista(models.Model):
    id_entrevista = models.AutoField(primary_key=True)
    categoria = models.ForeignKey(Categoria, on_delete= models.CASCADE, null= False, default=2)
    postulante = models.ForeignKey(Postulante, on_delete= models.CASCADE, null= False, default=2)
    responsable = models.ForeignKey(Personal, on_delete=models.CASCADE,null= False ,default=12)
    fecha_asignacion = models.DateField(auto_now=TRUE,)
    estatus  = models.CharField(max_length=30, null=False, default= 'Asignado')

     
    def __str__(self):
        return "{}({})".format(self.postulante,self.categoria)


        
class Question_rh(models.Model):
    id_question = models.AutoField(primary_key=True)
    entrevista = models.OneToOneField(Entrevista, on_delete= models.CASCADE, null= False, default=1)
    q1  = models.CharField(max_length=80, null=False, verbose_name='¿Por qué te interesa trabajar en esta empresa?', default='')
    q2  = models.CharField(max_length=200, null=False, verbose_name='¿Qué sabes de nuestra empresa?', default='')
    q3  = models.CharField(max_length=200, null=False, verbose_name='¿Cuál es tu meta personal?', default='')
    q4  = models.CharField(max_length=200, null=False, verbose_name='¿Cuál es tu meta laboral?', default='')
    q5  = models.CharField(max_length=80, null=False, verbose_name='¿Cuál fue su última percepción neto mensual?', default='')
    q6  = models.CharField(max_length=200, null=False, verbose_name='Describe tus fortalezas o aptitudes', default='')
    q7  = models.CharField(max_length=200, null=False, verbose_name='Cuales considera que sean sus debilidades', default='')
    q8  = models.CharField(max_length=200, null=False,  verbose_name='¿Qué te gusta hacer en tu tiempo libre?', default='')
    q9  = models.CharField(max_length=20, null=False, verbose_name='¿Actualmente trabajas?', default='')
    q10 = models.CharField(max_length=200, null=False, verbose_name='¿Qué funciones y responsabilidades has tenido en tus trabajos?', default='')
    q11 = models.CharField(max_length=80, null=False, verbose_name='¿Qué tipo de informes has realizado?', default='')
    q12 = models.CharField(max_length=10, choices=SELECT_1_10, null=False, verbose_name='Del 1 al 10 ¿tu habilidad en Excel es?', default='')
    q13 = models.CharField(max_length=10, choices=SELECT_BINARIA, null=False, verbose_name='¿Has realizado control de costes?', default='')
    q14 = models.CharField(max_length=10, choices=SELECT_BINARIA, null=False, verbose_name='¿Sabes realizar Informes semanales y Mensuales?', default='')
    q15 = models.CharField(max_length=80, null=False, verbose_name='¿Has trabajado en el extranjero? ¿En dónde?', default='')
    q16 = models.CharField(max_length=80, null=False, verbose_name='¿Cuál es el área o departamento al que deseas postular?', default='')
    aceptar_terminos = models.BooleanField(verbose_name='Aceptar Terminos Condiciones y privacidad de informacion', 
    null= False, default=True, help_text='. Acepte los terminos y condiciones establecidas en la declaracion de Revergy Mexico para el tratamiento de todo la informacion proporcionada.')
    fecha = models.DateField(auto_now_add=True,null=True)
    
    class meta:
        db_table = 'Pregunta_RRHH'
        verbose_name = 'Pregunta_RRHH'
        verbose_name_plural = 'Preguntas_RRHH'
    
    def __str__(self):
        return "Respuestas({})".format(self.entrevista.categoria)


class Question_psicologico(models.Model):
    id_question = models.AutoField(primary_key=True)
    entrevista = models.OneToOneField(Entrevista, on_delete= models.CASCADE, null= False, default=1)
    q1 = models.CharField(max_length=100, null= False, default='', verbose_name='Mencione algunos datos personales tales como sus intereses en su adolescencia, la profesión o empleo de sus padres y qué influencia tuvieron sus experiencias familiares en su desarrollo')
    q2 = models.CharField(max_length=100, null= False, default='', verbose_name='¿Qué influencia tuvo su niñez en la clase de persona que es hoy?')
    q3 = models.CharField(max_length=100, null= False, default='', verbose_name='¿A qué edad tuvo su primer trabajo? ¿ Cuándo se volvió económicamente independiente?')
    q4 = models.CharField(max_length=100, null= False, default='', verbose_name='¿En que tipo de actividades le gusta tomar parte cuando no está trabajando? ¿Es usted miembro o líder de algún grupo?')
    q5 = models.CharField(max_length=100, null= False, default='', verbose_name='¿Qué tipo de lectura relacionada con el trabajo o recreativa le gusta?')
    q6 = models.CharField(max_length=100, null= False, default='', verbose_name='¿Prefiere usted trabajar sola o en grupos?')
    q7 = models.CharField(max_length=100, null= False, default='', verbose_name='¿Qué tipos de presiones de trabajo le gustan o le disgustan mas?')
    q8 = models.CharField(max_length=100, null= False, default='', verbose_name='¿En que formas es usted más eficaz trabajando con otros? ¿Menos eficaz?')
    q9 = models.CharField(max_length=100, null= False, default='', verbose_name='¿Que mejoras o nuevas ideas han sugerido en trabajos anteriores? ')
    q10 = models.CharField(max_length=100, null= False, default='', verbose_name='¿Cómo cree que lo describirían sus compañeros o sus subordinados?')
    q11 = models.CharField(max_length=100, null= False, default='', verbose_name='¿En que trabajo ha estado mas contento y por que? ¿Más descontento y porque?')
    q12 = models.CharField(max_length=100, null= False, default='', verbose_name='¿Qué cualidades le gusta mas en un superior? ¿Menos?')
    q13 = models.CharField(max_length=100, null= False, default='', verbose_name='¿Por qué asistió (o no) a la universidad? ')
    q14 = models.CharField(max_length=100, null= False, default='', verbose_name='Si tuviera la oportunidad de volver a cursar sus estudios, ¿qué haría diferente? ¿Por que?')
    q15 = models.CharField(max_length=100, null= False, default='', verbose_name='¿Cómo es similar y como es diferente a sus padres?')
    q16 = models.CharField(max_length=100, null= False, default='', verbose_name='¿Ha tenido de acumular una reserva financiera (ahorros, seguro de vida, etc.)?')
    aceptar_condiciones = models.BooleanField(verbose_name='Aceptar Terminos Condiciones y privacidad de informacion', 
    null= False, default=False, help_text='. Acepte los terminos y condiciones establecidas en la declaracion de Revergy Mexico para el tratamiento de todo la informacion proporcionada.')
    fecha = models.DateField(auto_now_add=TRUE,)
    

class Evento(models.Model):
    even_id = models.AutoField(primary_key=True)
    postulante = models.ForeignKey(Postulante, on_delete= models.CASCADE, null= False, default=2)
    event_name = models.CharField(max_length=255,null=True,blank=True, verbose_name='Nombre del Evento')
    start_date = models.DateTimeField(null=True, default=datetime.now)
    end_date = models.DateTimeField(null=True)
    description = models.TextField(max_length=200, null=True, default= '', verbose_name='Descripcion')
    event_type = models.CharField(max_length=50,choices=CATEGORIAS_EVENTO ,null=False, default='ENTREVISTA', verbose_name='Tipo de evento')

    def __str__(self):
        return self.event_name


class Proyecto_cliente(models.Model):
    id_proyecto = models.AutoField(primary_key=True)
    analitica = models.ForeignKey(Analitica, on_delete= models.CASCADE, null= False, default=2)
    parque = models.CharField(max_length=100 ,null=False)
    cliente = models.CharField(max_length=80 ,null=False, default='')
    departamento = models.ForeignKey(Departamento, on_delete= models.CASCADE, null=True )
    actividad = models.CharField(max_length=80 ,null=False, default='Operacion y Mantenimiento', choices=ACTIVIDADES)
    fecha_inicio = models.DateField(null=True)
    fecha_fin =  models.DateField(null=True)
    estatus = models.CharField(max_length=15 ,null=False, default='Activo', choices= ESTATUS)

    def __str__(self):
        return "{}_{}".format(self.analitica, self.parque)


class Asignacion_personal(models.Model):
    id = models.AutoField(primary_key=True,)
    tecnico = models.ForeignKey(Personal, on_delete= models.CASCADE, null=True)
    proyecto = models.ForeignKey(Proyecto_cliente, on_delete= models.CASCADE, null=True)
    lugar = models.CharField(max_length=15 ,null=False, choices=LUGAR)


    def __str__(self):

        return "{}_{}".format(self.tecnico,self.proyecto)



# class Valoracion(models.Model):
#     id_valoracion = models.AutoField(primary_key=True,)
#     entrevista = models.ForeignKey(Entrevista, on_delete= models.CASCADE)
#     valoracion = models.CharField(max_length=30, choices= SELECT_1_10, null= False, default= 1, verbose_name= 'Puntaje 1-10')
# # class Actividad(models.Model):
#     # id_actividad = models.AutoField(primary_key=True,)
#     # tipo_actividad = 
#     # descripcion = 

# class Reporte_OTS(models.Model):
#     id = models.AutoField(primary_key=True)



