from django.shortcuts import render
from django.http import HttpResponseNotFound, JsonResponse
from collectEmail.models import Email, UltimateVerification
from collectEmail.utils.Threads import ThreadsStart, MainProcessCollect
from django.utils import timezone
import re
import os

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
    if (request.POST):
        email = request.POST.get('email')
        context = {}
        if (email == ''):
            context = {
                'error': True,
                'success': False,
                'message': 'El correo es requerido'
            }
        elif (isValidEmail(email)):
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

    if (re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email)):
        if (re.search(r'canvia.com', email)):
            return True
    return False


def processFiles(request):
    list_files = request.FILES.getlist('files')

    if not os.path.exists('temp'):
        os.makedirs('temp')

    for file in list_files:
        with open('temp/%s' % file.name, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

    stack = {}
    files = os.listdir('temp')
    for file in files:
        html_file = open('temp/%s' % file, 'r')
        html = html_file.read().splitlines()
        html_file.close()

        """ concat all string split in array to one string """
        html = ''.join(html)

        [vcenter, type] = getTypeFile(file)
        if vcenter in stack:
            stack[vcenter] = {
                'schedule': html if type == 'schedule' else stack[vcenter]['schedule'],
                'link': html if type == 'link' else stack[vcenter]['link']
            }
        else:
            stack[vcenter] = {
                'schedule': html if type == 'schedule' else None,
                'link': html if type == 'link' else None
            }

    updateTimeForceSendMail()
    MainProcessCollect.Normall = True
    mainProcessCollect = MainProcessCollect()
    mainProcessCollect.wait_more_emails(stack)

    for file in files:
        os.remove('temp/%s' % file)

    return JsonResponse({'success': True})


def getTypeFile(filename):
    _name = str(filename).split('.')[0]
    vcenter = _name.split(' ')[-1]
    type = 'schedule' if 'schedule' in _name.lower() else 'link'
    return [vcenter, type]


def updateTimeForceSendMail():
    time = UltimateVerification.objects.all().first()
    if not time:
        time = UltimateVerification.objects.create()
    time.comprovate = timezone.now() - timezone.timedelta(hours=4)
    time.save()
