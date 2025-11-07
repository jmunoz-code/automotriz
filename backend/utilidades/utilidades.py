import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import os
from dotenv import load_dotenv
load_dotenv() # Asegúrate de que esta línea esté aquí

def sendMail(html, asunto, para):
  msg = MIMEMultipart('alternative') # Usamos 'alternative'
  msg['Subject'] = str(asunto) # Aseguramos que asunto sea una cadena
  msg['From'] = str(os.getenv("SMTP_USER")) # Aseguramos que From sea una cadena
  msg['To'] = str(para) # Aseguramos que To sea una cadena

  msg.attach(MIMEText(html, 'html'))

  smtp_server = os.getenv("SMTP_SERVER")
  smtp_port_str = os.getenv("SMTP_PORT")
  smtp_user = os.getenv("SMTP_USER")
  smtp_password = os.getenv("SMTP_PASSWORD")

  try:
    port = int(smtp_port_str)
  except (ValueError, TypeError):
    print("Error: El puerto SMTP no es un entero válido.")
    return # O maneja el error de otra manera

  try:
    server = smtplib.SMTP(smtp_server, port)
    server.login(smtp_user, smtp_password)
    server.sendmail(smtp_user, para, msg.as_string()) # Llamamos a msg.as_string()
    server.quit()
  except smtplib.SMTPResponseException as e:
    print(f"Error al enviar el correo: {e}")