from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
import re
from collectEmail.models import Email

from collectEmail.utils.Threads import ThreadsStart

# Create your views here.

start = False


def index(request):
    global start

    context = {
        'error': False,
        'success': False,
        'message': '',
    }

    if not start:
        ThreadsStart()
        start = True

    return render(request, 'index.html', context)


def save(request):
    if(request.POST):
        email = request.POST.get('email')
        context = {}
        if(email == ''):
            context = {
                'error': True,
                'success': False,
                'message': 'El correo es requerido'
            }
        elif(isValidEmail(email)):
            Email.objects.all().delete()

            save_mail = Email.objects.create()
            save_mail.email = email
            save_mail.save()

            context = {
                'error': False,
                'success': True,
                'message': 'El correo se guardo correctamente'
            }
        else:
            context = {
                'error': True,
                'success': False,
                'message': 'El correo no es valido'
            }

        return render(request, 'index.html', context)
    else:
        return HttpResponseNotFound()


def isValidEmail(email):
    """ verify is email is valid and contain domain canvia.com in expresion regular"""

    if(re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email)):
        if(re.search(r'canvia.com', email)):
            return True
    return False
