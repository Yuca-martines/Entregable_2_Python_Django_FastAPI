import requests
from django.shortcuts import render


def lista_productos(request):

    respuesta = requests.get(
        "http://127.0.0.1:8000/productos"
    )

    productos = respuesta.json()

    return render(
        request,
        "productos/lista.html",
        {
            "productos": productos
        }
    )