def globales(request):

     entrevistas = Entrevista.objects.filter(postulante_id=request.user.id)
	
    return {'entrevistas': entrevistas }