# views.py
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from .models import Vendedores
from .serializers import VendedoresSerializer
from django.contrib.auth.hashers import check_password # Importa esto para verificar contraseñas

# ---
## Clase1: Gestión de Vendedores (GET all, POST)
# ---
class Clase1(APIView):

    def get(self, request):
        """
        Obtiene todos los vendedores ordenados por ID de forma descendente.
        """
        data = Vendedores.objects.order_by('-id').all()
        serializer = VendedoresSerializer(data, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Crea un nuevo vendedor.
        Normaliza campos como nombres, apellidos y usuario a mayúsculas.
        El hashing de la clave ahora se maneja en el serializador.
        """
        modified_data = request.data.copy()

        if 'nombres' in modified_data and modified_data['nombres']:
            modified_data['nombres'] = modified_data['nombres'].upper()

        if 'apellidos' in modified_data and modified_data['apellidos']:
            modified_data['apellidos'] = modified_data['apellidos'].upper()

        if 'usuario' in modified_data and modified_data['usuario']:
            modified_data['usuario'] = modified_data['usuario'].upper()

        serializer = VendedoresSerializer(data=modified_data)

        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {"estado": "ok", "mensaje": "Se crea el registro exitosamente"},
                status=status.HTTP_201_CREATED
            )
        except ValidationError:
            return Response(
                {"estado": "error", "mensaje": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

# ---
## Clase2: Gestión de Vendedores (GET by RUT, DELETE, PUT)
# ---
class Clase2(APIView):

    def get(self, request, rut):
        """
        Obtiene un vendedor específico por su RUT.
        """
        try:
            vendedor = Vendedores.objects.get(rut=rut)
            serializer = VendedoresSerializer(vendedor)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Vendedor no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error inesperado en la vista GET de Vendedores: {e}")
            return Response(
                {"error": "Ocurrió un error inesperado."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, rut):
        """
        Elimina un vendedor específico por su RUT.
        """
        try:
            vendedor = Vendedores.objects.get(rut=rut)
            vendedor.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response(
                {"error": f"No se encontró ningún cliente con el RUT: {rut}"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error inesperado al eliminar vendedor: {e}")
            return Response(
                {"error": f"Ocurrió un error inesperado al eliminar: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, rut):
        """
        Actualiza los datos de un vendedor específico por su RUT.
        Normaliza campos como nombres, apellidos y usuario a mayúsculas.
        El hashing de la clave ahora se maneja en el serializador.
        """
        modified_data = request.data.copy()

        if 'nombres' in modified_data and modified_data['nombres']:
            modified_data['nombres'] = modified_data['nombres'].upper()

        if 'apellidos' in modified_data and modified_data['apellidos']:
            modified_data['apellidos'] = modified_data['apellidos'].upper()

        if 'usuario' in modified_data and modified_data['usuario']:
            modified_data['usuario'] = modified_data['usuario'].upper()

        try:
            vendedor_existente = Vendedores.objects.get(rut=rut)
            serializer = VendedoresSerializer(vendedor_existente, data=modified_data, partial=True)

            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    {"data": serializer.data, "message": "Vendedor modificado exitosamente"},
                    status=status.HTTP_200_OK
                )

        except ObjectDoesNotExist:
            return Response(
                {"error": "Vendedor no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Error inesperado al modificar vendedor: {e}")
            return Response(
                {"error": f"Ocurrió un error inesperado al modificar: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ---
## Clase Login: Autenticación de Vendedores
# ---
class LoginVendedores(APIView):
    def post(self, request):
        """
        Maneja el inicio de sesión de vendedores.
        Recibe 'usuario' y 'clave', verifica credenciales y devuelve un mensaje de éxito/error.
        """
        usuario_ingresado = request.data.get('usuario')
        clave_ingresada = request.data.get('clave')

        print(f"Intento de login - Usuario: '{usuario_ingresado}', Clave recibida: '{clave_ingresada}'") # <- Añade esta línea
# ...

        if not usuario_ingresado or not clave_ingresada:
            return Response(
                {"error": "Se requieren usuario y clave."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Buscar el vendedor por el usuario (normalizado a mayúsculas)
            vendedor = Vendedores.objects.get(usuario=usuario_ingresado.upper())

            # Verificar la clave hasheada
            if check_password(clave_ingresada, vendedor.clave):
                # Autenticación exitosa
                # Aquí puedes generar un token JWT o de sesión si estás usando DRF Token/JWT Authentication
                # Por ahora, solo retornamos un mensaje de éxito.
                return Response(
                    {"mensaje": "Inicio de sesión exitoso", "data": VendedoresSerializer(vendedor).data},
                    status=status.HTTP_200_OK
                )
            else:
                # Clave incorrecta
                return Response(
                    {"error": "Credenciales inválidas."},
                    status=status.HTTP_401_UNAUTHORIZED # 401 para credenciales no autorizadas
                )
        except ObjectDoesNotExist:
            # Usuario no encontrado
            return Response(
                {"error": "Credenciales inválidas."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            print(f"Error inesperado en el login: {e}")
            return Response(
                {"error": "Ocurrió un error inesperado al intentar iniciar sesión."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )