from django.shortcuts import *

def inicio(request):
    variable = "Hello Sunday!"
    return render_to_response('Index/index.html', {'variable': variable}, context_instance=RequestContext(request))
