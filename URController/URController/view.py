import time

from django.shortcuts import render
from django.http import HttpResponse

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

    scale = 1.5
    modbus.REGISTER[101] = int(min(x, 100) * scale)
    modbus.REGISTER[102] = int(min(y, 100) * scale)

    return HttpResponse('Success, {}'.format(values))
