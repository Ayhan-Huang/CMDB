from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt,csrf_protect


@csrf_exempt
def server(request):
    data = request.POST
    print('data---------',data)
    return HttpResponse(data)