from django.shortcuts import render
from django.http import HttpResponseNotFound, JsonResponse
from collectEmail.models import Email, UltimateVerification
from collectEmail.utils.Threads import ThreadsStart, MainProcessCollect
from django.utils import timezone
from openpyxl import load_workbook
from automationDataProtector import settings
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
    for file in files:
        os.remove('temp/%s' % file)

    for file in os.listdir(settings.BASE_DIR):
        if file.startswith('PBI_'):
            if re.match(r'^PBI_\d{8}\.xlsx', file) != None:
                os.remove(file)
                MainProcessCollect.saveFirstFile('PBI_.xlsx')

    list_files = request.FILES.getlist('files')

    if not os.path.exists('temp'):
        os.makedirs('temp')

    for file in list_files:
        with open('temp/%s' % file.name, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

    stack = {}
    files = os.listdir('temp')

    updateTimeForceSendMail()
    MainProcessCollect.Normall = True
    mainProcessCollect = MainProcessCollect()

    for _file in files:
        [vcenter, type, fileExtension] = getTypeFile(_file)

        if fileExtension != 'html':
            if _file.startswith('PBI_'):
                mainProcessCollect.process_pbi_files(
                    load_workbook('temp/%s' % _file), _file)
            else:
                mainProcessCollect.process_veem_files(
                    load_workbook('temp/%s' % _file), vcenter)
        else:
            """ open file and read all lines """
            file = open('temp/%s' % _file, 'r')
            html = file.read().splitlines()
            file.close()

            """ concat all string split in array to one string """
            html = ''.join(html)

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

    mainProcessCollect.wait_more_emails(stack)
    MainProcessCollect.Normall = None

    for file in files:
        os.remove('temp/%s' % file)

    return JsonResponse({'status': 'complete'})


def getTypeFile(filename):
    _name = str(filename).split('.')[0]
    fileExtension = str(filename).split('.')[-1]
    vcenter = _name.split(' ')[-1]
    type = 'schedule' if 'schedule' in _name.lower() else 'link'
    return [vcenter, type, fileExtension]


def updateTimeForceSendMail():
    time = UltimateVerification.objects.all().first()
    if not time:
        time = UltimateVerification.objects.create()
    time.comprovate = timezone.now() - timezone.timedelta(hours=4)
    time.save()
