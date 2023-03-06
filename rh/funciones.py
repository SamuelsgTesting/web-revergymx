

def obtener_tiempo_transcurrido(segundos):
    dias = int(segundos / 60 / 60 / 24)
    segundos -= dias * 60 * 60 * 24
    horas = int(segundos / 60 / 60)
    segundos -= horas*60*60
    minutos = int(segundos/60)
    segundos -= minutos*60

    if dias > 0 and horas > 1 and minutos > 0: return f"Hace {dias} día(s), {horas} hora(s), {minutos} minuto(s)"
    elif dias < 1 and horas > 0 and minutos > 0: return f"Hace {horas} hora(s), {minutos} minuto(s)"
    elif horas < 1 and minutos > 0: return f"Hace {minutos} minuto(s)"
    elif dias < 1 and minutos < 1 and segundos > 1: return f"Justo Ahora"
    elif horas == 0 and minutos == 0 and segundos >=0 : return f"Hace {dias} dia(s)"
    else: return  f"Hace {dias} día(s), {horas} hora(s), {minutos} minuto(s)"
