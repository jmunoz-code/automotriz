from rest_framework.views import APIView
from django.http.response import JsonResponse
from django.http import Http404
from django.contrib.auth.models import User
from http import HTTPStatus
from rest_framework.views import APIView
from utilidades import utilidades
from .models import *
import uuid
#from dotenv import load_dotenv

#load_dotenv()

import os

class Clase1(APIView):

    def post(self, request):

        if request.data.get("nombre") is None or not request.data['nombre']:
            return JsonResponse({"estado": "error", "mensaje": "El campo nombre es obligatorio"},
                                status=HTTPStatus.BAD_REQUEST)

        if request.data.get("correo") is None or not request.data['correo']:
            return JsonResponse({"estado": "error", "mensaje": "El campo correo es obligatorio"},
                                status=HTTPStatus.BAD_REQUEST)

        if request.data.get("password") is None or not request.data['password']:
            return JsonResponse({"estado": "error", "mensaje": "El campo password es obligatorio"},
                                status=HTTPStatus.BAD_REQUEST)

        if User.objects.filter(email=request.data['correo']).exists():
            return JsonResponse({"estado": "error", "mensaje": "El correo ya existe"},
                                status=HTTPStatus.BAD_REQUEST)

        # insertado en cascada
        token = uuid.uuid4()
        url = f"{os.getenv('BASE_URL')}api/v1/seguridad/verificacion/{token}"
        try:
            u = User.objects.create_user(username=request.data['correo'],
                                         email=request.data['correo'],
                                         password=request.data['password'],
                                         first_name=request.data['nombre'],
                                         last_name="",
                                         is_active=0)
            UserMetadata.objects.create(token=token, user_id=u.id)
            html = f"""
                    <h3>Verificacion de Cuenta</h3>
                    Hola {request.data["nombre"]}, te has registrado exitosamente. Para activar 
                    click en el siguientte enlace:</br>
                    <a href="{url}">{url}</a>
                    </br>
                    o copia y pega la siguiente URL en tu navegador en tu navegador favorito
                    {url}
                    """
         
            utilidades.sendMail(html, "verificacion", request.data['correo'])
        except Exception as e:
            print(f"Ocurrió un error inesperado: {e}")
            return JsonResponse({"estado": "error", "mensaje": "ocurrio un error inesperado"},
        status=HTTPStatus.BAD_REQUEST)
        

        return JsonResponse({"estado": "success", "mensaje": "Se ha creado el registro exitosamente. Por favor, revisa tu correo electrónico para verificar tu cuenta."},
 status=HTTPStatus.CREATED)
    

