# -*- encoding: utf-8 -*-
from django.shortcuts import *
from django.contrib.auth.forms import *
from django.contrib import auth
from django.contrib.auth.hashers import *
from Core.forms import *
from datetime import date,datetime
from django.db.models import Count
from django.core import exceptions
from django.core import serializers
import json
from Core.utils import *

#*****************************************************************************************************
# VISTAS DEL ADMINISTRADOR
#*****************************************************************************************************




#*****************************************************************************************************
# VISTAS DEL PERFIL
#*****************************************************************************************************

def perfil_usuario(request, id_usuario):
    user = User.objects.get(id=id_usuario)
    perfil = Perfil.objects.get(user=user)
    return render_to_response('usuarios/profile_user.html', {'perfil':perfil}, context_instance=RequestContext(request))



#****************************************************************************************************
#FUNCIONES AJAX
#****************************************************************************************************


#***************************************************************************************
#FUNCIONES AUXILIARES
#***************************************************************************************


