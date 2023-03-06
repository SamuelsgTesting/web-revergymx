from django.urls import path
import rh.views as vista


urlpatterns = [

    #Links generales del sistema

    path('', vista.home, name='Inicio'),
    path('salir/', vista.salir, name= 'Salir'),
    path('accounts/user/registro', vista.user_registro, name='sign_in'),
    path('accounts/user/postulante/register', vista.registro_postulante, name='registro_postulante'),
    path('perfil/', vista.perfil, name='perfil'),
    path('perfil/informacion/_change_photo/', view = vista.change_photo, name='change_photo'),


    #Links para modulo administradores (nivel3)
    path('administracion/personal/',view = vista.personal, name ='personal'),
    path('administracion/personal/agregar/',view=vista.add_personal, name='add_personal'),
    path('administracion/personal/editar/<id_personal>/',view=vista.edit_personal, name='edit_personal'),
    path('administracion/personal/asignacion/proyecto/<id>/', view = vista.add_personal_proyecto, name='add_personal_proyecto'),
    path('administracion/personal/asignacion/personal/proyecto/<id>/', view = vista.view_personal_proyecto, name='view_personal_proyecto'),
    path('administracion/personal/asignacion/personal/eliminar/<id>', view = vista.delete_personal_proyecto, name='delete_personal_proyecto'),

    

    path('administracion/analiticas/', view =vista.analiticas, name='analiticas'),
    path('administracion/analiticas/agregar', view =vista.add_analitica, name='add_analitica'),
    path('administracion/analiticas/editar/<id_analitica>/', view = vista.edit_analitica, name='editar_analitica'),
    path('administracion/analiticas/eliminar/<id_analitica>/', view = vista.delete_analitica, name='del_analitica'),

    path('administracion/analitica/proyectos/', view = vista.proyectos, name='proyectos'),
    path('administracion/analitica/proyectos/add/', view = vista.add_proyecto, name='add_proyecto'),
    path('administracion/analitica/proyectos/edit/<id>', view = vista.edit_proyecto, name='edit_proyecto'),
    path('administracion/analitica/proyectos/eliminar/<id>', view = vista.delete_proyecto, name='del_proyecto'),

    path('administracion/gestion/vacantes/', view = vista.vacantes,  name ='vacantes'),
    path('administracion/gestion/vacantes/agregar/', view = vista.add_vacante,  name ='add_vacante'),
    path('administracion/gestion/vacantes/view/<id_oferta>', view = vista.view_oferta_admin,  name ='view_oferta_res'),
    path('administracion/gestion/vacantes/editar/<id_vacante>', view = vista.edit_vacante,  name ='edit_vacante'),
    path('administracion/gestion/vacantes/eliminar/<id_vacante>', view = vista.delete_vacante,  name ='del_vacante'),

    
    path('reclutamiento/entrevistas/', view = vista.gestion_entrevistas,  name ='gestion_entrevistas'),
    path('reclutamiento/entrevistas/postulante/evaluar/<id>', view = vista.view_entrevista,  name ='view_entrevista'),
    path('reclutamiento/entrevistas/eventos/', view = vista.eventos_admin,  name ='eventos_admin'),
    path('reclutamiento/entrevistas/evento/informacion/<id>', view = vista.view_evento_admin,  name ='detalles_evento'),
    path('reclutamiento/entrevistas/evento/agregar/', view = vista.add_evento,  name ='add_evento'),
    path('reclutamiento/entrevistas/evento/editar/<id>', view = vista.edit_evento,  name ='edit_evento'),
    path('reclutamiento/entrevistas/evento/eliminar/<id>', view = vista.view_evento_admin,  name ='delete_evento'),


    path('administracion/gestion/organizacion/', view = vista.organizacion, name='organizacion'),
    path('administracion/gestion/organizacion/departamento/agregar/', view = vista.add_departamento, name='add_departamento'),
    path('administracion/gestion/organizacion/departamento/editar/<id_departamento>/', view = vista.edit_departamento, name='edit_departamento'),
    path('administracion/gestion/organizacion/departamento/eliminar/<id_departamento>', view = vista.delete_departamento, name='del_departamento'),

    path('administracion/gestion/organizacion/puesto/agregar/', view = vista.add_puesto, name='add_puesto'),
    path('administracion/gestion/organizacion/puesto/editar/<id_puesto>', view = vista.edit_puesto, name='edit_puesto'),
    path('administracion/gestion/organizacion/puesto/eliminar/<id_puesto>', view = vista.delete_puesto, name='del_puesto'),


    path('reclutamiento/postulantes/solicitudes/', view = vista.solicitudes_vacantes, name = 'solicitudes'),
    path('reclutamiento/postulantes/solicitudes/eliminar/<id_solicitud>/', view = vista.delete_solicitud, name = 'delete_solicitud'),
    path('reclutamiento/postulantes/informacion/<id_postulante>/', view = vista.view_cv, name = 'view_cv'),
     path('postulante/entrevistas/generales/psicologica/asignar/<id_postulante>/', view = vista.asignar_entrevista_psicologica, name='asignar_entrevsitaPsi'),
    path('reclutamiento/postulantes/documentos/', view = vista.documentacion, name= 'documentacion'),

   
    #Urls para modulo postulante
    path('postulante/informacion/curriculum/', view = vista.curriculum, name='cv'),
    path('postulante/informacion/editar/', view = vista.edit_postulante, name='editar_postulante'),
    path('postulante/informacion/curriculum/actualizar/', view = vista.change_cv, name='change_cv'),
    path('postulante/informacion/ine/add_view/', view = vista.doc_ine, name='doc_ine'),
    path('postulante/informacion/licencia/add_view/', view = vista.doc_licencia, name='doc_licencia'),
    path('postulante/documentos/agregar/', view = vista.add_doc, name='add_doc'),
    path('postulante/documentos/eliminar/<id>', view = vista.delete_doc, name='delete_doc'),
    path('postulante/vacante/detalles/<id_vacante>', view = vista.view_oferta, name='detalles_oferta'),
    path('postulante/vacante/solicitud/<id_vacante>/', view = vista.solicitar_vacante, name='postulacion'),
    path('postulante/solicitudes/sends/', view = vista.solicitudes_postulante, name='solicitudes_ready'),
    path('postulante/entrevistas/informacion/', view = vista.detalles_evspt, name='datails_entrevistas'),
    path('postulante/agenda/calendario/', view = vista.calendario_postulante, name='calendario'),
    path('postulante/entrevistas/generales/rh/<id>', view = vista.realiza_entrevista_rh, name='entrevista_rh'),
    path('postulante/entrevistas/generales/psicologica/', view = vista.realiza_entrevista_psicologica, name='entrevista_psicologica'),
   

    path('postulante/agenda/calendario/evento/informacion/<id_evento>', view = vista.view_evento, name='view_evento'),
    path('postulante/agenda/calendario/evento/informacion/<id_postulante>', view = vista.view_evento_postulante, name='view_evento_postulante'),

 ]

