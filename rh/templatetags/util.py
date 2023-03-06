import datetime
from optparse import Values
from django import template
from django.contrib.auth.models import Group 
from django.contrib.auth.decorators import user_passes_test
import re

register = template.Library()

@register.filter(name='has_group') 
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

def group_required(*group_names):
    """ Grupos, checar si pertenece a grupo """

    def check(user):
        if user.groups.filter(name__in=group_names).exists():
            return True
        else:
            return False
    # Si no se pertenece al grupo, redirigir a /prohibido/
    return user_passes_test(check, login_url='/')

@register.filter
def name_archivo(value):
    if not value:
        return ""
    else:
        return re.split("/", str(value))[3]



    
@register.filter
def recuento_dias(value):
    print(value)
    fecha = datetime.date(value)
    fecha_hoy = datetime.now().date()
    transcurrido = fecha_hoy - fecha
    return f"{transcurrido.days}, dia(s)"

    #fecha_hoy = datetime.now().strftime("%A, %d de %B de %Y alas %I:%M %p")
