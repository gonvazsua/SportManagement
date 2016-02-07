##################################################################
#--------------- Funciones auxiliares para plantillas ------------
##################################################################

from django import template

register = template.Library()

@register.simple_tag
def incrementa(num):
    res = num + 1
    return res

@register.filter
def hash(h, key):
    return h[key]

@register.filter
def keyvalue(dict, key):
    return dict[key]

@register.filter(name='contenido')
def contenido(user, benefit_id):
    b_id = int(benefit_id)
    return user.benefits.filter(id=b_id).count() > 0

@register.simple_tag
def separa_guiones(cadena):
    res = ""
    split_cadena = cadena.split(" ")
    for index, s in enumerate(split_cadena):
        res += s
        if index != split_cadena.length():
            res += "-"

    return res
