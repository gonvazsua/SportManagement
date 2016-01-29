# -*- encoding: utf-8 -*-
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
import json
import logging
from django.core.mail import EmailMultiAlternatives

#Instancia del log
logger = logging.getLogger(__name__)

def send_email(request):
    subject = request.POST.get('subject', '')
    message = request.POST.get('message', '')
    from_email = request.POST.get('from_email', '')
    error = ""
    if subject and message and from_email:
        try:
            texto = "<h5>Email enviado desde Sport Click:</h5> \n"
            texto += "<h5>De: </h5>" + from_email + "\n"
            texto += "<h5>Titulo: </h5>" + subject + "\n"
            texto += "<h5>Cuerpo: </h5>" + message + "\n"
            #send_mail(subject, texto, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])
            msg = EmailMultiAlternatives(subject,'' , settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])
            msg.attach_alternative(texto, "text/html")
            msg.send()
        except BadHeaderError, e:
            logger.debug("util/views - Método send_email." + e)
            error = "Ha habido un error en el proceso. Disculpe las molestias"
        except Exception, e:
            logger.debug("util/views - Método send_email." + e)
            error = "Ha habido un error en el proceso. Disculpe las molestias"
    else:
        error = "Rellene correctamente todos los campos"
    data = {'error':error}
    return HttpResponse(json.dumps(data))
