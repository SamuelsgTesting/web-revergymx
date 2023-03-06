

from multiprocessing import context
from django.http import JsonResponse
from http.client import HTTPResponse
import json
from .funciones import *
from datetime import datetime
from contextlib import nullcontext
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from .forms import *
from .templatetags.util import *
from .models import *
from .choises import *
from .datas import *

# Funciones generales del sistema
# @group_required('Postulante','Personal','Administrador')


#----------------------------------------------------------------------------------------------------------------------
#               Funciones del sistema(Usuario, Roles , Perfiles , Cierre de sesion, Registro de usuario)
#----------------------------------------------------------------------------------------------------------------------


#--------------- Home -----------------------------------
@login_required(login_url='/accounts/login/')
def home(request):

    if request.user.is_superuser: return redirect('/admin/') 

    elif request.user.is_personal:

        data_personal = {

            'personal_activo': Personal.objects.filter(estatus='Activo') ,
            'personal_inactivo': Personal.objects.filter(estatus='Inactivo'), 
            'personal': Personal.objects.all(), 
            'analiticas':  Analitica.objects.all(),
            'analiticas_activas': Analitica.objects.all().filter(estatus = 'Activo'),
            'solicitudes_p': Solicitud_vacante.objects.filter(estatus='Pendiente'),
            'solicitudes_r':Solicitud_vacante.objects.filter(estatus='Revisado'),
            'vacantes_activas': Vacante.objects.filter(estatus = 'Activo'),
            'vacantes_inactivas': Vacante.objects.filter(estatus = 'Inactivo'),
            'eventos': Evento.objects.all(),
            'proyectos':Proyecto_cliente.objects.all()
        }
        
        return render(request, 'home/dashboard_admin.html', data_personal)

    elif request.user.is_postulante:

        formaciones = Documento.objects.filter(fk_postulante_id = request.user.id, tipo = "FORMACION")
        experiencias = Documento.objects.filter(fk_postulante_id = request.user.id, tipo = "EXP_LAB")
        solcitudes_check = Solicitud_vacante.objects.filter(fk_postulante_id = request.user.id, estatus = "Revisado")
        solcitudes_send = Solicitud_vacante.objects.filter(fk_postulante_id = request.user.id, estatus = "Pendiente")
        solicitudes_done = Solicitud_vacante.objects.filter(fk_postulante_id = request.user.id).select_related('fk_vacante').values_list('fk_vacante', flat=True),
        eventos = Evento.objects.filter(postulante_id = request.user.id)
        entrevistas = Entrevista.objects.filter(postulante_id=request.user.id)
        

        data = {
                'vacantes_on': Vacante.objects.filter(estatus = 'Activo').select_related('fk_puesto'),
                'solcitudes_check':solcitudes_check,
                'solcitudes_send':solcitudes_send,
                'experiencias':experiencias,'formaciones': formaciones,
                'postulacion':solicitudes_done,
                'entrevistas':entrevistas,
                'eventos':eventos,

                }

        vacantes = Vacante.objects.filter(estatus ='Activo')

        for i in vacantes:

            if i.id_vacante in Solicitud_vacante.objects.filter(fk_postulante_id = request.user.id).values_list('fk_vacante', flat=True):

                print("Vacante: {} seleccionada!".format(i.id_vacante))

            else: print("Vacante: {} Disponible".format(i.id_vacante))

        try: data[ 'info_postulante']= Postulante.objects.get(user_id = request.user.id)
        except Postulante.DoesNotExist:  return redirect("registro_postulante")


    return render(request,'home/dashboard_postulante.html',data)
    
#--------------- Salir (Cierre de sesion) -----------------------------------    
def salir(request): 
    logout(request) 
    return redirect('/')


#--------- Registro de usuarios (Postulantes Modulo 1) ---------------
def user_registro(request):

    data = { 'form_usuario': Usuario() }

    if request.method == 'POST':
        form_usuario = Usuario(request.POST)

        if form_usuario.is_valid():
            form_usuario.save()
            user = authenticate(username = form_usuario.cleaned_data['email'], password = form_usuario.cleaned_data['password1'])
            login(request, user)
            return redirect(to="registro_postulante")
            
        # else: messages.error(request,'Ocurrio un error al guardar los datos')

           
    return render(request,'registration/registro.html', data)


#----------- funcion registro de informacion del postulante -----------
def registro_postulante(request):

    responsable_rrhh = Personal.objects.get(estatus='Activo', fk_puesto__puesto= 'Responsable RRHH')
    print(responsable_rrhh)
    print(responsable_rrhh.clave_personal)
    
    if request.method == 'POST':

        form = form_postulante(request.POST, request.FILES)
    
        if form.is_valid():
            insert = form.save(commit=False)
            insert.user_id = request.user.id
            insert.correo = request.user.email
            insert.save()

            
            #Asignaacion de grupo postulante al usuario
            # group_postulante = Group.objects.get(name='Postulante')
            # group_postulante.user_set.add(request.user.id)

            #Asignacion de entrevista Rh al postulante

            if responsable_rrhh:

                insert_asignacion = Entrevista(
                    estatus='Pendiente',
                    categoria_id=1,
                    responsable_id=responsable_rrhh.clave_personal,
                    postulante_id=request.user.id
                )

                insert_asignacion.save()
                messages.success(request,'Registro Exitoso | Bienvenido al sistema de reclutamiento Revergy S.A. de C.V.!')
                return redirect(to="Inicio")
            else: 
                messages.error(request,'Ocurrio un error al asignar reponsable de entrevista RRHH!')
            
        else: print("Formulario no valido")

    return render(request,'registration/registro_postulante.html', {'form_postulante':form_postulante() })


#-------- Funcion perfil usuario---------------------------------------
@login_required(login_url='/accounts/login/')
def perfil(request):

    usuario = User.objects.get(pk = request.user.id)
    context = {'change_password': change_password(), 'info_usuario': usuario }

   
    if request.user.is_personal:

        try:
            personal = Personal.objects.get(email_empresa = request.user.email)
            context['info_perfil'] = personal

        except Personal.DoesNotExist: context['info_perfil'] = nullcontext

    else:

        try:
            postulante = Postulante.objects.get(correo = request.user.email)
            context['info_perfil'] = postulante
          
        except Postulante.DoesNotExist:  
            messages.ERROR(request, "No se encontraron datos. Por favor! Registr su informacion")
            return redirect("registro_postulante")
            

    
    if request.method == 'GET':  context['form_user'] = edit_usuario(instance = usuario)
   
    elif request.method == 'POST': 

        form = edit_usuario(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Informacion de perfil actualizada correctamente")
            return redirect("perfil")
        else:  
            print("Error al validacion el formulario")
            messages.error(request, "Ocurrio un error al guardar los datos")
   

    return render(request,'registration/perfil.html', context)
   

   # Funcion cambio de foto de perfil del Usuario
def change_photo(request):
    datos = User.objects.get(pk=request.user.id)

    if request.method =='POST':

        formulario = change_foto(request.POST, request.FILES, instance = datos)
        if formulario.is_valid():
            formulario.save()
            print("Formulario no valido")
            messages.success(request, 'Foto de perfil actualizada correctamente!')
            return redirect("perfil")
            
        else: 
            print("Formulario no valido")
            messages.error(request, 'Ocurrio un error al validar los datos. Intentelo nuevamente')

    return render(request, 'home/perfil-usuario/edit_photo.html', {'form_change_photo': change_foto(), 'info_usuario': datos })

# --------------------------- 404: página no encontrada ----------------
def handler404(request, exception):
    return render(request,"error/page-error-404.html")


#-------------------------------------------------------------------------------------------------------------
#                              Funciones para el modulo administrador
#-------------------------------------------------------------------------------------------------------------


#--------------- CRUD analiticas ---------------------

#view analiticas
@login_required(login_url='/accounts/login/')
def analiticas(request):

    consulta = Personal.objects.raw('''SELECT 
    clave_personal,fk_analitica_id, COUNT(fk_analitica_id) 
    AS total 
    FROM  rh_personal WHERE estatus='Activo' GROUP BY fk_analitica_id ORDER BY total DESC ''')

    tops_analiticas = {}

    iterando = 1
    for tops in consulta:
        tops_analiticas['top'+str(iterando)] = tops.fk_analitica_id
        tops_analiticas['cantidad_'+str(iterando)] = tops.total
        iterando+=1



    data = {  
        'analiticas': Analitica.objects.all(),
        'proyectos':Proyecto_cliente.objects.all(),
        'proyectos_activos':Proyecto_cliente.objects.filter(estatus='Activo'),
        'personal': Personal.objects.all().filter(estatus='Activo'), 
        'analiticas_activas': Analitica.objects.all().filter(estatus = 'Activo'),
        'analiticas_inactivas': Analitica.objects.all().filter(estatus = 'Inactivo'),
        'form_alta':form_analitica(),
        'tops_analitica':tops_analiticas
        }

    print(tops_analiticas)

    return render(request, 'temp_personal/analiticas.html', data)


#añadir analiticas
@login_required(login_url='/accounts/login/')
def add_analitica(request):
    
    data = { 'form_analitica': form_analitica() }
    if request.method == 'POST':

        formulario  =  form_analitica(request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Analitica registrada correctamente!')
            return redirect("analiticas")

        else: 
            messages.error(request, 'Ocurrio un error al validar los datos')  

    return render(request, 'temp_personal/crud/add/add_analitica.html', data)


#Modificar analiticas
@login_required(login_url='/accounts/login/')
def edit_analitica(request, id_analitica):

    analiticas = Analitica.objects.get(pk = id_analitica)

    if request.method == 'GET':
        form = form_analitica(instance = analiticas)
    else:
        form = form_analitica(request.POST, instance=analiticas)
        if form.is_valid():
            form.save()
            messages.success(request,'Informacion de la analitica ('+str(analiticas)+') actualizada correctamente')
            return redirect("analiticas")
        else: 
            messages.error(request,"Ocurrio un errror al guaadar los datos")
            return redirect("analiticas")

    return render(request,'temp_personal/crud/edit/edit_analitica.html',{ 'form_analitica': form })


#eliminar analitica
@login_required(login_url='/accounts/login/')
def delete_analitica(request,id_analitica):

    if request.method == 'GET':

        try:
            registro = Analitica.objects.get(id_analitica = id_analitica)
            registro.delete()
            messages.success(request, 'Analitica '+str(registro)+' eliminada correctamente!')
            print("Analitica "+str(registro)+" eliminada correctamente!")

        except: messages.error(request, 'Ocurrio un error al eliminar la analitica!')

    else: print("Error de solicitud")  

    return redirect("analiticas")


#Funciones Asginaciones a proyectos OPERACIO Y MANTENIMIENTO

#view proyectos
@login_required(login_url='/accounts/login/')
def proyectos(request):

    lista_proyectos = Proyecto_cliente.objects.all()
    proyetos_activos = Proyecto_cliente.objects.filter(estatus='Activo')
    personal_Activo = Asignacion_personal.objects.filter(tecnico__estatus='Activo')
    asignaciones_personal = Asignacion_personal.objects.all()
    departamentos = Asignacion_personal.objects.select_related('tecnico').values(
        'tecnico__fk_puesto__fk_departamento__departamento').distinct()
    campo = Asignacion_personal.objects.filter(lugar='CAMPO')
    oficina = Asignacion_personal.objects.filter(lugar='OFICINA')


    context = {
        'proyectos': lista_proyectos,
        'proyetos_activos':proyetos_activos,
        'asignaciones_personal':asignaciones_personal,
        'campo':campo,
        'oficina':oficina,
        'departamentos':departamentos,
        'personal_activo':personal_Activo
    }

    return render(request,'temp_personal/proyectos.html', context)

#add proyecto.
@login_required(login_url='/accounts/login/')
def add_proyecto(request):

    context = {'form_proyecto': form_proyecto_OYM()}

    if request.method =='POST':
        formulario = form_proyecto_OYM(request.POST)
        
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Proyecto Operacion / Mantenimiento Correctamente agregado')
            return redirect("proyectos")
        else: messages.error(request,'Ocurrio un error al guardar los datos')

    

    return render(request,'temp_personal/crud/add/add_proyecto.html', context)


#edit proyecto
@login_required(login_url='/accounts/login/')
def edit_proyecto(request,id):

    proyecto = Proyecto_cliente.objects.get(id_proyecto=id)

    context = {'form_proyecto': form_proyecto_OYM()}

    if request.method =='GET': context['form_proyecto']=form_proyecto_OYM(instance=proyecto)

    else:
        formulario = form_proyecto_OYM(request.POST,instance=proyecto)
        
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'El Proyecto Operacion / Mantenimiento '+str(proyecto)+ ' Correctamente Actualizado')
            return redirect("proyectos")
        else: messages.error(request,'Ocurrio un error al guardar los datos')

    

    return render(request,'temp_personal/crud/edit/edit_proyecto.html', context)



#View Personal Tecnico Asignado a proyecto
@login_required(login_url='/accounts/login/')
def view_personal_proyecto(request,id):

    context = {

        'inf_proyecto': Proyecto_cliente.objects.get(pk=id),
        'personal_asing': Asignacion_personal.objects.filter(proyecto_id = id),
    }
  
    
    return render(request,'temp_personal/crud/view/view_personal_proyecto.html', context)


#add asignacion personal-proyecto
@login_required(login_url='/accounts/login/')
def add_personal_proyecto(request, id):


    context = {
        'form_asignacion_proyecto': form_asignacion_proyecto(departamento_id=2,proyecto_id=id),
        'inf_proyecto': Proyecto_cliente.objects.get(pk=id),
        'personal_asing': Asignacion_personal.objects.filter(proyecto_id = id) 
    }
  
    if request.method =='POST':

        formulario = form_asignacion_proyecto(request.POST)

        print(request.POST['tecnico'])

        
        if formulario.is_valid():
            
            formulario.save()
            messages.success(request, 'Tecnico asignado al proyecto correctamente!')
        else: messages.error(request,'Ocurrio un error al guardar los datos')

    
    return render(request,'temp_personal/crud/add/add_personal_proyecto.html', context)



#eliminacion de tecnico de proyecto 
@login_required(login_url='/accounts/login/')
def delete_personal_proyecto(request, id):

    if request.method == 'GET':

        try:
            registro = Asignacion_personal.objects.get(pk = id)
            registro.delete()
            messages.success(request, 'Tecnico '+registro.tecnico.nombre+ ' fue eliminado correctamente del proyecto ('+registro.proyecto.parque+')')
            print("Proyecto '+registro.parque+' eliminada correctamente!")

        except: messages.error(request, 'Ocurrio un error al eliminar el proyecto!')

    else: print("Error de solicitud")  

    return redirect("/administracion/personal/asignacion/personal/proyecto/"+str(registro.proyecto_id))




#Eliminar registro de proyecto
@login_required(login_url='/accounts/login/')
def delete_proyecto(request,id):

    if request.method == 'GET':

        try:
            registro = Proyecto_cliente.objects.get(id_proyecto = id)
            registro.delete()
            messages.success(request, 'Proyecto '+registro.parque+' eliminada correctamente!')
            print("Proyecto '+registro.parque+' eliminada correctamente!")

        except: messages.error(request, 'Ocurrio un error al eliminar el proyecto!')

    else: print("Error de solicitud")  

    return redirect("proyectos")


#------------------------------- CRUD personal ----------------------------------

#view personal
@login_required(login_url='/accounts/login/')
def personal(request):

    try: 
        listar_personal = Personal.objects.all().select_related('fk_puesto','fk_analitica')
        a = Personal.objects.filter(estatus = 'Activo')
        i = Personal.objects.filter(estatus = 'Inactivo')
        tecnicos = Personal.objects.filter(fk_puesto__fk_departamento__area='OPERACIÓN Y MANTENIMIENTO')
        tecnicos_activos = Personal.objects.filter(fk_analitica__estatus ='Activo').filter(fk_puesto__fk_departamento__area='OPERACIÓN Y MANTENIMIENTO')
        print(Personal.objects.filter(estatus='Activo', fk_puesto__fk_departamento__proceso='APOYO'))
    except Personal.DoesNotExist: return render(request, "error/page-error-404.html")

    return render(request,'temp_personal/personal.html',{ 

        'personal': listar_personal, 
        'activos':a, 'inactivos':i, 
        'tecnicos_proyectos':tecnicos,
        'tecnicos_proyectos_activos': tecnicos_activos,
        'estrategico':Personal.objects.filter(estatus='Activo', fk_puesto__fk_departamento__proceso='ESTRATÉGICO'),
        'operativo':Personal.objects.filter(estatus='Activo', fk_puesto__fk_departamento__proceso='OPERATIVO'),
        'apoyo':Personal.objects.filter(estatus='Activo', fk_puesto__fk_departamento__proceso='APOYO')
    })

    
         
#agregar personal
@login_required(login_url='/accounts/login/')
def add_personal(request):

    if request.method == 'POST':

        formulario = form_personal(request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(request,'Personal añadido correctamente')
            return redirect("personal")

        else:  messages.error(request, 'Ocurrio un error al guardar los datos')

        # datos_personal = Personal.objects.get(user_id=request.user.id)
        # formulario = form_edit_personal(instance = datos_personal)

    return render(request, 'temp_personal/crud/add/add_personal.html',{ 'form_personal': form_personal()})


#editar personal
@login_required(login_url='/accounts/login/')
def edit_personal(request, id_personal):

    personal = Personal.objects.get(pk = id_personal)

    if request.method == 'GET':
        form = form_edit_personal(instance = personal)
    else:
        form = form_edit_personal(request.POST, instance=personal)
        if form.is_valid():
            form.save()
            messages.success(request,'Informacion de ('+str(personal)+') actualizado correctamente')
            return redirect("personal")
        else: 
            messages.error(request,"Ocurrio un errror al guardar los datos")
            return redirect("personal")

    return render(request,'temp_personal/crud/edit/edit_personal.html',{ 'form_personal': form })


#------------ CRUD Vacantes --------------------------------------------------------

# ----------------- view -----------------------------------------------------------
@login_required(login_url='/accounts/login/')
def vacantes(request):

    lista_vacantes = Vacante.objects.all().select_related('fk_puesto').values(
        'id_vacante', 'perfil','tarjeta', 'descripcion', 'estatus',
        'fecha_creacion','fk_puesto__puesto','fk_puesto__fk_departamento__area')

    return render(request, 'temp_personal/rh/vacantes.html', { 'ofertas': lista_vacantes})



def upload_tarjeta(id_puesto):

    qs = Vacante.objects.filter(fk_puesto_id =id_puesto).select_related('fk_puesto').values_list('fk_puesto__fk_departamento__proceso')
    proceso = list(qs[1:])
    print(proceso)
 
    if proceso: 
        print(proceso)
        print(proceso[0])
        return 'cards/oferta/procesos/%s.png' % (str(proceso[0]).lower())
    return 'cards/oferta/procesos/default.png'
    

#agregar vacante
@login_required(login_url='/accounts/login/')
def add_vacante(request):

    data = { 'form_vacante': form_vacante()}
    formulario = form_vacante(request.POST, request.FILES)

    if request.method == 'POST':
    
        if formulario.is_valid():

            add = formulario.save(commit=False)
            add.tarjeta = upload_tarjeta(request.POST['fk_puesto'])
            add.save()
            messages.success(request, 'Se ha agregado una nueva oferta')
            return redirect('vacantes')
        else: 
            messages.error(request, 'Ocurrio un erro al guardar los datos')
            return redirect('vacantes')
    
    else: return render(request,'temp_personal/crud/add/add_vacante.html', data)


#Modificar vacante
@login_required(login_url='/accounts/login/')
def edit_vacante(request, id_vacante):

    vacante = Vacante.objects.get(pk = id_vacante)

    if request.method == 'GET':

        form = form_edit_vacante(instance = vacante)
    else:
        form = form_edit_vacante(request.POST, instance=vacante)
        if form.is_valid():
            form.save()
            messages.success(request,'Informacion de la vacante ('+str(vacante)+') actualizado correctamente')
            return redirect("vacantes")
        else: 
            messages.error(request,"Ocurrio un errror al guardar los datos")
            # return redirect("edit_vacante")

    return render(request,'temp_personal/crud/edit/edit_vacante.html',{ 'form_vacante': form })

#Eliminar Vacante
def delete_vacante(request, id_vacante):
  
    if request.method == 'GET':

        try:
            registro = Vacante.objects.get(pk = id_vacante)
            registro.delete()
            messages.success(request, 'Vacante eliminada correctamente!')
            print("Record deleted successfully!")

        except: messages.error(request, 'Ocurrio un error al eliminar el la vacante!')

    else: print("Error de solicitud")  

    return redirect("vacantes")


#------------ CRUD Departamentos/puestos --------------------------------------------------------

# ----------------- view general ----------------------------------------------------------------
@login_required(login_url='/accounts/login/')
def organizacion(request):


    consulta_first = Personal.objects.raw('''
        SELECT 
        clave_personal,fk_puesto_id, COUNT(fk_puesto_id) 
        AS total 
        FROM  rh_personal WHERE estatus='Activo' GROUP BY fk_puesto_id ORDER BY total DESC LIMIT 1''')

    consulta_last = Personal.objects.raw('''
        SELECT 
        clave_personal,fk_puesto_id, COUNT(fk_puesto_id) 
        AS total 
        FROM  rh_personal WHERE estatus='Activo' GROUP BY fk_puesto_id ORDER BY total ASC LIMIT 1''')



    data = {
        'departamentos':Departamento.objects.all(),
        'puestos': Puesto.objects.all(),
        'estrategico':Personal.objects.filter(estatus='Activo', fk_puesto__fk_departamento__proceso='ESTRATÉGICO'),
        'operativo':Personal.objects.filter(estatus='Activo', fk_puesto__fk_departamento__proceso='OPERATIVO'),
        'apoyo':Personal.objects.filter(estatus='Activo', fk_puesto__fk_departamento__proceso='APOYO'),
        'consulta_first': consulta_first,
        'consulta_last': consulta_last
    }

    return render(request, 'temp_personal/rh/organizacion.html', data)

#-------------------- Añadir departamento --------------------------------------------------------

@login_required(login_url='/accounts/login/')
def add_departamento(request):

    data = { 'form_departamento': form_departamento()}

    if request.method == 'POST':

        formulario = form_departamento(request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Se ha agregado un nuevo departamento al sistema')
            return redirect("organizacion")
        else: 
            messages.error(request, 'Ocurrio un error al guardar los datos')

    return render(request,'temp_personal/crud/add/add_departamento.html', data)

#------------------ Modificar Deparmento ---------------------------------------------------------

@login_required(login_url='/accounts/login/')
def edit_departamento(request, id_departamento):

    departamento = Departamento.objects.get(pk = id_departamento)

    if request.method == 'GET':
         formulario = form_departamento(instance= departamento)

    else:
        formulario = form_departamento(request.POST,instance= departamento)
        if formulario.is_valid():
            formulario.save()
            messages.success(request,'Datos actualizados correctamente')
            return redirect("organizacion")
        else:
            messages.error(request,'Ocurrio un error al guardar los datos')
    
    return render(request, 'temp_personal/crud/edit/edit_departamento.html', { 'form_departamento': formulario  })


#------------------ Eliminar departamento ---------------------------

def delete_departamento(request, id_departamento):
    if request.method == 'GET':

        try:
            registro = Vacante.objects.get(pk = id_departamento)
            registro.delete()
            messages.success(request, 'Departamento eliminada correctamente!')
            
        except: messages.error(request, 'Ocurrio un error al eliminar el departamento!')

    else: messages.success(request, 'Error de peticion!')

    return redirect("organizacion")


#------------Agregar Puesto -----------------------------------------

@login_required(login_url='/accounts/login/')
def add_puesto(request):

    data = { 'form_puesto': form_puesto()}

    if request.method == 'POST':

        formulario = form_puesto(request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Se ha agregado un nuevo puesto al sistema')
            return redirect("organizacion")
        else: 
            messages.error(request, 'Ocurrio un error al guardar los datos')

    return render(request,'temp_personal/crud/add/add_puesto.html', data)


# ----------------- Modificar puesto ----------------------------------------------------------------
@login_required(login_url='/accounts/login/')
def edit_puesto(request, id_puesto):

    departamento = Puesto.objects.get(pk = id_puesto)

    if request.method == 'GET':
         formulario = form_puesto(instance= departamento)

    else:
        formulario = form_puesto(request.POST,instance= departamento)
        if formulario.is_valid():
            formulario.save()
            messages.success(request,'Datos actualizados correctamente')
            return redirect("organizacion")
        else:
            messages.error(request,'Ocurrio un error al guardar los datos')
    
    return render(request, 'temp_personal/crud/edit/edit_puesto.html', { 'form_puesto': formulario  })


#------------------ Eliminar puesto ---------------------------------------------------------------

def delete_puesto(request, id_puesto):
    if request.method == 'GET':

        try:
            registro = Puesto.objects.get(pk = id_puesto)
            registro.delete()
            messages.success(request, 'Puesto eliminado correctamente!')
            
        except: messages.error(request, 'Ocurrio un error al eliminar el departamento!')

    else: messages.success(request, 'Error de peticion!')

    return redirect("organizacion")

#--------------- CRUD  de Solicitudes -> Postulantes ----------------------------------------------


# Lista de solicitudes (View)
@login_required(login_url='/accounts/login/')
def solicitudes_postulante(request):

    solicitudes = Solicitud_vacante.objects.filter(fk_postulante_id = request.user.id).select_related('fk_postulante','fk_vacante')
    en_revision = Solicitud_vacante.objects.filter(fk_postulante_id = request.user.id, estatus='En Revision').select_related('fk_postulante','fk_vacante')



    return render(request,"temp_postulante/crud/view/view_solicitudes.html",{ 'solicitudes':solicitudes, 'en_revision': en_revision})


@login_required(login_url='/accounts/login/')
def solicitudes_vacantes(request):

    lista =  Solicitud_vacante.objects.select_related().values(
        'clv_solicitud',
        'fk_postulante__nombre',
        'fk_postulante_id',
        'fk_postulante__apellidos',
        'fk_postulante__perfil',
        'fk_postulante__user__foto',
        'fk_postulante__user_id',
        'fk_vacante__fk_puesto__puesto',
        'fk_vacante__fk_puesto_id__fk_departamento__area',
        'fk_postulante__cv',
        'fecha',
        'estatus'
        )

 


    # lista2 = Solicitud_vacante.objects.prefetch_related('postulacion')
    # print(lista2)
  

    data = { 'solicitudes': lista }
    return render(request, 'temp_personal/rh/solicitudes.html',data)

#Eliminar Solicitud
@login_required(login_url='/accounts/login/')
def delete_solicitud(request, id_solicitud):

    if request.method == 'GET':

        try:
            registro = Solicitud_vacante.objects.get(pk = id_solicitud)
            registro.delete()
            messages.success(request, 'Solcitud Eliminada correctamente del sistema!')

        except: messages.error(request, 'Error al eliminar el documento!, El documento no existe')

    else: print("Error de solicitud")  

    return redirect("solicitudes")

    
# View Informacion completa de postulante (View)
@login_required(login_url='/accounts/login/')
def view_cv(request, id_postulante):
    
    if request.method == 'GET':
        
        postulante = Postulante.objects.select_related('user').get(pk = id_postulante)
        docs_postulante = Documento.objects.filter(fk_postulante_id = id_postulante)
        entrevistas = Entrevista.objects.filter(postulante_id=id_postulante)

        entrevista_rrhh = Entrevista.objects.get(postulante_id=id_postulante, categoria__nombre='Generalidades RR.HH.')
        entrevista_tecnica = Entrevista.objects.filter(postulante_id=id_postulante, categoria__nombre='Técnica')
        entrevista_psicologica = Entrevista.objects.filter(postulante_id=id_postulante, categoria__nombre='Psicológica')

        
        data = { 
                    'info_perfil': postulante, 
                    'documentos':docs_postulante,
                    'entrevistas':entrevistas,
                    'entrevista_rrhh':entrevista_rrhh,
                    'entrevista_tecnica':entrevista_tecnica,
                    'entrevista_psicologica':entrevista_psicologica,
                    
                }

    else:
        print("Error de peticion")

    return render(request, 'temp_personal/rh/curriculum_postulante.html', data)


# View oferta responsable
@login_required(login_url='/accounts/login/')
def view_oferta_admin(request, id_oferta):

    datos = Vacante.objects.get(pk=id_oferta)
    lista_pendientes = Solicitud_vacante.objects.filter(fk_vacante = id_oferta , estatus= 'Pendiente')
    lista_solicitudes = Solicitud_vacante.objects.filter(fk_vacante= id_oferta).select_related(
        'fk_postulante','fk_vacante'
        ).values(
    'clv_solicitud',
    'fk_postulante__nombre',
    'fk_postulante_id',
    'fk_postulante__apellidos',
    'fk_postulante__perfil',
    'fk_postulante__cv',
    'estatus'

    )

    context = { 'inf_oferta':datos, 'postulaciones': lista_solicitudes,'pendientes':lista_pendientes}

    return render(request, 'temp_personal/crud/view/view_oferta.html', context)

#Funciones Gestion de entrevistas

#view detalles entrevistas
@login_required(login_url='/accounts/login/')
def gestion_entrevistas(request):

    lista_entrevistas= Entrevista.objects.all()
    generalrh = Entrevista.objects.filter(categoria__nombre='Generales RH')
    tecnicas = Entrevista.objects.filter(categoria__nombre='Técnica')
    psicologicas = Entrevista.objects.filter(categoria__nombre='Psicológica')
    pendientes = Entrevista.objects.filter(estatus='Pendiente')
    contestadas = Entrevista.objects.filter(estatus='Contestado')


    context = { 

        'entrevistas': lista_entrevistas, 
        'generales_rh':generalrh, 
        'tecnicas':tecnicas, 
        'psicologicas':psicologicas, 
        'pendientes':pendientes,
        'enviadas':contestadas

    }

    return render(request,'temp_personal/rh/detalles_entrevistas.html', context)


#Vista evaluar entrevista
@login_required(login_url='/accounts/login/')
def view_entrevista(request,id):
    
    datos = Question_rh.objects.get(entrevista_id=id)
    print(datos)

    context = {'datos_entrevista':datos, 'form_entrevista': form_entrevista_rh(instance=datos) }

    return render(request, 'temp_personal/rh/evaluar_entrevista.html', context)





    


#Vista evento seleccionado por administrador
@login_required(login_url='/accounts/login/')
def view_evento_admin(request,id):

    inf_evento = Evento.objects.get(even_id=id)

    return render(request,'temp_personal/crud/view/view_evento.html',{'inf_evento':inf_evento})




## Aun  en programacion
@login_required(login_url='/accounts/login/')
def asignar_entrevista_psicologica(request, id_postulante):
    
    if request.method == 'GET':
        validar_solicitud = Entrevista.objects.filter(postulante_id = id_postulante, categoria_id=3)
        print(validar_solicitud)

        if not validar_solicitud:

            add = Entrevista.objects.create(
                postulante_id=id_postulante, 
                categoria_id = 3,
                 responsable_id = 12, 
                 estatus='Pendiente')
            add.save()
            messages.success(request,"La Entrevista 'Psicologica' fue asignado correctamente!")

        else:
            messages.error(request, 'Ya se ha Asignado esta entrevista. Para mas detalles dirigase ala seccion "Entrevistas"')


    return redirect("")
#-------------------------------------------------------------------------------------------------------------
#                              Funciones para el modulo Postulante
#-------------------------------------------------------------------------------------------------------------

    
@login_required(login_url='/accounts/login/')
def curriculum(request):

    usuario = User.objects.get(pk = request.user.id)

    postulante = Postulante.objects.get(user_id = request.user.id)
    documentos = Documento.objects.filter(fk_postulante_id = request.user.id)

    return render(request,'temp_postulante/cv.html', {
        'info_usuario': usuario,
        'info_perfil': postulante,
        'documentos': documentos


    })


@login_required(login_url='/accounts/login/')
def view_oferta(request, id_vacante):

    try: 
        oferta = Vacante.objects.get(pk=id_vacante)
        
    except Vacante.DoesNotExist: return render(request, "error/page-error-404.html")

    return render(request, 'temp_postulante/crud/view/view_oferta.html', {'inf_oferta': oferta})


@login_required(login_url='/accounts/login/')
def solicitar_vacante(request,id_vacante):

    if request.method == 'GET':
        validar_solicitud = Solicitud_vacante.objects.filter(fk_postulante_id = request.user.id, fk_vacante_id=id_vacante)
        print(validar_solicitud)

        if not validar_solicitud:
            add = Solicitud_vacante.objects.create(fk_postulante_id= request.user.id, fk_vacante_id = id_vacante)
            add.save()
            messages.success(request,"Solicitud Enviada correctamente! Espere la notificacion del resposanble RRHH")
            messages.info(request,'Para un mejor proceso de seleccion, es recomendable cargar su documentacion e informacion requerida')
        else:
            messages.error(request, 'Usted ya ha solicitado esta vacante. Para mas detalles dirigase ala seccion "Solicitudes"')
           
    return redirect("Inicio")


@login_required(login_url='/accounts/login/')
def documentacion(request):

    context =  {
        'documentacion': Documento.objects.all(),
        'form_documento': form_documento(),
        'formaciones':Documento.objects.filter(tipo='FORMACION'),
        'experiencias':Documento.objects.filter(tipo='EXP_LAB'),
        'personales':Postulante.objects.all(),
        'curp':Documento.objects.filter(tipo='CURP'),
        'rfc':Documento.objects.filter(tipo='RFC'),
        'anexos':Documento.objects.filter(tipo='ANEX'),
    }

    if request.method == 'POST':

        postulante = Postulante.objects.get(fk_usuario_id = request.user.id)
        add = Documento(fk_postulante_id = postulante.id_postulante, tipo = request.POST['tipo'], archivo = request.POST['archivo'])
        add.save()

        if add.save():
            messages.success(request, "Guardado correctamente")
            return redirect(to='documentacion')
        else: messages.error(request, "Ocurrio un error al tratar de guardar el archivo")
            

    return render(request, 'temp_personal/documentacion.html', context)


@login_required(login_url='/accounts/login/')
def detalles_evspt(request):

    asignadas = Entrevista.objects.filter(postulante_id= request.user.id)
    realizadas = Entrevista.objects.filter(postulante_id=request.user.id, estatus='Realizado')
    pendientes = Entrevista.objects.filter(postulante_id=request.user.id, estatus='Pendiente')

    context = {'asignadas':asignadas, 'realizadas':realizadas,'pendientes':pendientes }
  

    return render(request, 'temp_postulante/detalles_entrevistas.html', context)


#Funcion realizacion de entrevista Generalidades RR.HH
@login_required(login_url='/accounts/login/')
def realiza_entrevista_rh(request, id):

    try:
        
        inf_entrevista =  Entrevista.objects.get(id_entrevista=id)
        print(inf_entrevista)

    except Entrevista.DoesNotExist: 
        messages.error(request,'Ocurrio en error al validar la entrevista asignada. Por favor actualize la pagina')

    # print(informacion_entrevistas)

    if request.method == 'POST':

        formulario = form_entrevista_rh(request.POST)

        if formulario.is_valid():
            
            add = formulario.save(commit=False)
            add.entrevista_id = inf_entrevista.id_entrevista
            add.save()

            #Cambio de estatus de la entrevista a Realizado
            
            update_estatus = form_entrevista(instance=inf_entrevista)
            update = update_estatus.save(commit=False)
            update.estatus = 'Realizado'
            update.save()

            messages.success(request,'Entrevista correctamente guardada')
            messages.info(request,'Gracias por contestar la entrevista Generalidades RH. Tus respuestas seran evaluadas por el responsable.')
            return redirect("datails_entrevistas")
        else: 
            messages.error(request, 'Ocurrio un error al guardar los datos')

    
    return render(request, 'temp_postulante/questions_grh.html', {'formulario_entrevista': form_entrevista_rh()})



#Funcion realizacion de entrevista Psicologica
@login_required(login_url='/accounts/login/')
def realiza_entrevista_psicologica(request):

    try:
        inf_entrevista =  Entrevista.objects.get(postulante_id = request.user.id, categoria__nombre='Psicológica')

    except Entrevista.DoesNotExist: 
        messages.error(request,'Ocurrio en error al validar la entrevista asignada. Por favor actualize la pagina')

    if request.method == 'POST':

        formulario = form_entrevista_psicologica(request.POST)

        if formulario.is_valid():
            
            add = formulario.save(commit=False)
            add.entrevista_id = inf_entrevista.id_entrevista
            add.save()

            #Cambio de estatus de la entrevista a Realizado
            
            update_estatus = form_entrevista(instance=inf_entrevista)
            update = update_estatus.save(commit=False)
            update.estatus = 'Realizado'
            update.save()

            messages.success(request,'Entrevista correctamente guardada')
            messages.info(request,'Gracias por contestar la entrevista Psicologica | Revergy. Tus respuestas seran evaluadas por el responsable.')
            return redirect("datails_entrevistas")
        else: 
            messages.error(request, 'Ocurrio un error al guardar los datos')

    
    return render(request, 'temp_postulante/questions_psicologicas.html', {'formulario_entrevista': form_entrevista_psicologica()})




# CRUD para modulo postulante

#Agregar documento
@login_required(login_url='/accounts/login/')
def add_doc(request):

    postulante = Postulante.objects.get(pk = request.user.id)
    form = form_documento(request.POST, request.FILES)

    if request.method == 'POST':

        if form.is_valid():
            save = form.save(commit=False)
            save.fk_postulante_id = postulante.user_id
            save.save()
            print("Documento guardado correctamente")
            messages.success(request, "Documento guardado correctamente")
            return redirect(to='cv')

        else:
            print("Ocurrio un error al evaluar los datos del formulario!")
            messages.error(request, "Ocurrio un error al evaluar los datos del formulario!")
 
    else: print("No es metodo POST")

    return render(request,'temp_postulante/crud/add/add_documento.html',{
        'info_perfil':postulante,
        'form_doc': form_documento() })


# Eliminar documento
def delete_doc(request, id):

    if request.method == 'GET':

        try:
            registro = Documento.objects.get(pk = id)
            registro.delete()
            messages.success(request, 'Documento eliminado correctamente!')
            print("Record deleted successfully!")

        except: messages.error(request, 'Error al eliminar el documento!','El documento no existe')

    else: print("Error de solicitud")  
    return redirect("cv")


#Cambio de CV 
@login_required(login_url='/accounts/login/')
def change_cv(request):
    
    datos = Postulante.objects.get(pk = request.user.id)
    form_instance = form_change_cv(request.POST, request.FILES, instance = datos)

    if request.method == 'POST':

        if form_instance.is_valid():
            form_instance.save()
            print("CV Actualizado correctamente!")
            messages.success(request, 'CV actualizado correctamente!')
            return redirect('cv')
        else: 
            messages.error(request, 'Ocurrio un error al guardar los datos!')
            print("Formulario invalido")

    return render(request, 'temp_postulante/crud/edit/edit_documento.html', { 'form_cv': form_instance, 'info_usuario': datos })


@login_required(login_url='/accounts/login/')
def doc_ine(request):

    context = { 'form_ine': form_ine() }
    datos = Postulante.objects.get(pk = request.user.id)
 
    if request.method =='GET':
        context['form_ine'] = form_ine(instance= datos)
    
    else:

        formulario = form_ine(request.POST,request.FILES, instance=datos)

        if formulario.is_valid():
            formulario.save()
            messages.success(request,'Documento INE correctamente Agregado/Actualizado!')
            return redirect("cv")
            
        else: 
            messages.error(request, 'Ocurrio un  error al guardar los datos')
    
    return render(request,'temp_postulante/crud/add/add_ine.html', context)


@login_required(login_url='/accounts/login/')
def doc_licencia(request):

    data = { 'form_licencia': form_licencia() }

    licencia = Postulante.objects.get(pk = request.user.id)
    
    if request.method =='GET':
        data['form_licencia'] = form_licencia(instance=licencia)
    
    elif request.method =='POST':
        formulario = form_licencia(request.POST,request.FILES, instance=licencia)
        if formulario.is_valid():
            formulario.save()
            messages.success(request,'Licencia correctamente Agregado/Actualizado!')
            return redirect("cv")
        else: messages.error(request, 'Ocurrio un  error al guardar los datos')
    
    return render(request,'temp_postulante/crud/add/add_licencia.html', data)



@login_required(login_url='/accounts/login/')
def edit_postulante(request):

    datos = Postulante.objects.get(pk = request.user.id)
    if request.method == 'GET':

        form = form_edit_postulante(instance=datos)
    else:
        
        form = form_edit_postulante(request.POST, request.FILES, instance=datos)
        
        if form.is_valid():
            form.save()
            print(form)
            messages.success(request, 'Informacion personal actualizada correctamente!')
            return redirect("cv")
        else: 
            messages.error(request, 'Ocurrio un error al guardar los datos!')
    return render(request,'temp_postulante/crud/edit/edit_postulante.html',
    { 
        'form_postulante': form,
        'info_usuario': datos 
    })




# -----------------------------------------------------------------------------
#                              Implementacion del calendario y enventos
# -----------------------------------------------------------------------------

#POSTULANTE (CALENDARIO)


@login_required(login_url='/accounts/login/')
def calendario_postulante(request):
     
    all_events = Evento.objects.filter(postulante_id = request.user.id)
    get_event_types = Evento.objects.only('event_type')

    for i in all_events:
        print(i.event_type)
  

    if request.GET:  

        event_arr = []
        if request.GET.get('event_type') == "all":
            all_events = Evento.objects.all()
        else:   
            all_events = Evento.objects.filter(event_type__icontains=request.GET.get('event_type'))

        for i in all_events:
            event_sub_arr = event_sub_arr['title'] = i.event_name
            start_date = datetime.datetime.strptime(str(i.start_date.date()), "%Y-%m-%d").strftime("%Y-%m-%d")
            end_date = datetime.datetime.strptime(str(i.end_date.date()), "%Y-%m-%d").strftime("%Y-%m-%d")
            event_sub_arr['start'] = start_date
            event_sub_arr['end'] = end_date
            event_arr.append(event_sub_arr)
        
        return HTTPResponse(json.dumps(event_arr))

    context =  {"events":all_events, "get_event_types":get_event_types}

    return render(request,'temp_postulante/calendario.html',context)
    

 #### Lista de eventos del administrador(RR.HH)



#View desde calenadario postulante
@login_required(login_url='/accounts/login/')
def view_evento_postulante(request,id_postulante):

    evento = Evento.objects.get(postulante_id=id_postulante, event_type ='Entrevista Técnica')

    return render(request,'temp_postulante/crud/view/view_evento.html', {'inf_evento': evento})


@login_required(login_url='/accounts/login/')
def view_evento(request,id_evento):

    evento = Evento.objects.get(pk=id_evento)

    return render(request,'temp_postulante/crud/view/view_evento.html', {'inf_evento': evento})


#Administrador CRUD eventos

#view eventos
@login_required(login_url='/accounts/login/')
def eventos_admin(request):

    lista_eventos = Evento.objects.all()

    context = {'eventos':lista_eventos }

    return render(request,'temp_personal/rh/eventos.html', context)


#add evento
@login_required(login_url='/accounts/login/')
def add_evento(request ):

    context = {'form_evento': form_eventos()}

    if request.method == 'POST':
        print(request.POST)
        
        formulario = form_eventos(request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(request,"Evento Correctamente creado!")
            return redirect("Inicio")
        messages.error(request,"Ocurrio un error al guardar los datos")
        print("Formualrio no valdio")
    return render(request, 'temp_personal/crud/add/add_evento.html' , context)


#edit evento
def edit_evento(request, id):

    context = {'form_evento': form_eventos() }

    evento = Evento.objects.get(pk=id)

    if request.method=='GET':
        context['form_evento']= form_eventos(instance=evento)

    elif request.method =='POST':

        formulario = form_eventos(request.POST, instance=evento)
        
        if formulario.is_valid():
            formulario.save()
            messages.success(request,'Evento correctamento guardado/actualizado!')
            return redirect("eventos")

        else:  messages.error(request,'Ocurrio un error al guardar los datos, Intentelo de nuevo!')
    
    return render(request, 'temp_personal/crud/edit/edit_evento.html' , context)




