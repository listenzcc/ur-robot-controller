import time

from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

from .modbusTCP import ModbusTCP

modbus = ModbusTCP()


def index(request):
    print(request)

    kwargs = dict(
        load_on_time=time.ctime()
    )

    return render(request, 'index.html', kwargs)


def upload(request):
    print(request)

    values = dict()
    for e in request.GET:
        values[e] = request.GET[e]

    print(values)

    x = int(values.get('x', 0))
    y = int(values.get('y', 0))

    scale = 1
    modbus.REGISTER[200] = int(min(x, 100) * scale)
    modbus.REGISTER[201] = int(min(y, 100) * scale)

    # return HttpResponse('Success, {}'.format(values))
    return JsonResponse(dict(
        success='success',
        x=x,
        y=y
    ))


def query(request):
    print(request)

    z = modbus.REGISTER[100]
    x = modbus.REGISTER[101]
    y = modbus.REGISTER[102]
    r = 0.1 * 1000

    return JsonResponse(dict(
        success='success',
        x=x,
        y=y,
        z=z,
        r=r,
    ))
