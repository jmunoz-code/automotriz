# mi_app/utils/utilidades.py

from django.core.mail import send_mail
from django.conf import settings

def sendMail(html_content, subject, recipient_email):
    """
    Función para enviar correos electrónicos HTML.

    Args:
        html_content (str): El contenido HTML del correo electrónico.
        subject (str): El asunto del correo electrónico.
        recipient_email (str): La dirección de correo electrónico del destinatario.
    """
    if not settings.EMAIL_HOST:
        print("Error: Las configuraciones de correo electrónico no están establecidas en settings.py")
        return

    try:
        send_mail(
            subject,
            '',  # Cuerpo del mensaje en texto plano (opcional)
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            html_message=html_content,
            fail_silently=False,  # Si es False, levanta una excepción en caso de error
        )
        print(f"Correo electrónico enviado exitosamente a {recipient_email}")
    except Exception as e:
        print(f"Error al enviar el correo electrónico a {recipient_email}: {e}")