from django.shortcuts import *

def inicio(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/profile/')
    else:
        return render_to_response('Index/index.html', {'variable': ""}, context_instance=RequestContext(request))
