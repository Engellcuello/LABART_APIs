from flask import request
from flask_restful import Resource
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
from flask import session
import secrets
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash


from API.modelos.modelos import Usuario

class EmailSender(Resource):
    def __init__(self):
        self.remitente = "engellcuellovegamz@gmail.com"
        self.contraseña = "fjdp ipbf ejfq knpo"  # Contraseña de aplicación
        self.servidor_smtp = "smtp.gmail.com"
        self.puerto = 587
        self.asunto = "Tu código de verificación OTP"

    def generar_otp(self):
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])

    def generar_html(self, otp):
        return f"""
        <!DOCTYPE html>
        <html>
        <body style="margin:0; padding:0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
            <table width="100%" bgcolor="#f4f4f4" cellpadding="0" cellspacing="0">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; padding: 40px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1);">
                            <tr>
                                <td align="center" style="padding-bottom: 20px;">
                                    <h1 style="color: #333333;">Verificación de Seguridad</h1>
                                </td>
                            </tr>
                            <tr>
                                <td style="color: #555555; font-size: 16px; line-height: 24px;">
                                    <p>Hola,</p>
                                    <p>Tu código de verificación es:</p>
                                </td>
                            </tr>
                            <tr>
                                <td align="center" style="padding: 30px 0;">
                                    <div style="font-size: 36px; font-weight: bold; letter-spacing: 10px; color: #007BFF;">
                                        {otp}
                                    </div>
                                </td>
                            </tr>
                            <tr>
                                <td style="color: #555555; font-size: 14px; line-height: 22px;">
                                    <p>Este código es válido por 10 minutos. No lo compartas con nadie.</p>
                                    <p>Si no solicitaste este código, puedes ignorar este mensaje.</p>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding-top: 30px; font-size: 12px; color: #999999;" align="center">
                                    <p>© 2025 Labart. Todos los derechos reservados.</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

    def post(self):
        datos = request.get_json()
        destinatario = datos.get("destinatario")

        if not destinatario:
            return {"error": "Falta el campo 'destinatario'"}, 400

        otp = self.generar_otp()
        html = self.generar_html(otp)

        mensaje = MIMEMultipart()
        mensaje["From"] = self.remitente
        mensaje["To"] = destinatario
        mensaje["Subject"] = self.asunto
        mensaje.attach(MIMEText(html, "html"))

        try:
            servidor = smtplib.SMTP(self.servidor_smtp, self.puerto)
            servidor.starttls()
            servidor.login(self.remitente, self.contraseña)
            servidor.sendmail(self.remitente, destinatario, mensaje.as_string())
            servidor.quit()
            return {"mensaje": "Correo enviado correctamente", "OTP": otp}, 200
        except Exception as e:
            return {"error": f"No se pudo enviar el correo: {str(e)}"}, 500
        
        
        
        
        
        
        
        
        
        
        

from flask import request
from flask_restful import Resource
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
from flask import session
import secrets
from datetime import datetime, timedelta

from API.modelos.modelos import db,Usuario


class EmailSender(Resource):
    def __init__(self):        
        self.remitente = "engellcuellovegamz@gmail.com"
        self.contraseña = "fjdp ipbf ejfq knpo"  # Contraseña de aplicación
        self.servidor_smtp = "smtp.gmail.com"
        self.puerto = 587
        self.asunto = "Tu código de verificación OTP"

    def generar_otp(self):
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])

    def generar_html(self, otp):
        return f"""
        <!DOCTYPE html>
        <html>
        <body style="margin:0; padding:0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
            <table width="100%" bgcolor="#f4f4f4" cellpadding="0" cellspacing="0">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; padding: 40px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1);">
                            <tr>
                                <td align="center" style="padding-bottom: 20px;">
                                    <h1 style="color: #333333;">Verificación de Seguridad</h1>
                                </td>
                            </tr>
                            <tr>
                                <td style="color: #555555; font-size: 16px; line-height: 24px;">
                                    <p>Hola,</p>
                                    <p>Tu código de verificación es:</p>
                                </td>
                            </tr>
                            <tr>
                                <td align="center" style="padding: 30px 0;">
                                    <div style="font-size: 36px; font-weight: bold; letter-spacing: 10px; color: #007BFF;">
                                        {otp}
                                    </div>
                                </td>
                            </tr>
                            <tr>
                                <td style="color: #555555; font-size: 14px; line-height: 22px;">
                                    <p>Este código es válido por 10 minutos. No lo compartas con nadie.</p>
                                    <p>Si no solicitaste este código, puedes ignorar este mensaje.</p>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding-top: 30px; font-size: 12px; color: #999999;" align="center">
                                    <p>© 2025 Labart. Todos los derechos reservados.</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

    def post(self):
        datos = request.get_json()
        destinatario = datos.get("destinatario")

        if not destinatario:
            return {"error": "Falta el campo 'destinatario'"}, 400

        # Verificar si el correo ya está registrado
        if Usuario.query.filter_by(correo_usuario=destinatario).first():
            return {"error": "El correo ya está registrado en la base de datos"}, 409

        otp = self.generar_otp()
        html = self.generar_html(otp)

        mensaje = MIMEMultipart()
        mensaje["From"] = self.remitente
        mensaje["To"] = destinatario
        mensaje["Subject"] = self.asunto
        mensaje.attach(MIMEText(html, "html"))

        try:
            servidor = smtplib.SMTP(self.servidor_smtp, self.puerto)
            servidor.starttls()
            servidor.login(self.remitente, self.contraseña)
            servidor.sendmail(self.remitente, destinatario, mensaje.as_string())
            servidor.quit()
            return {"mensaje": "Correo enviado correctamente", "OTP": otp}, 200
        except Exception as e:
            return {"error": f"No se pudo enviar el correo: {str(e)}"}, 500
        
        
    def enviar_otp(self, destinatario, otp):
        try:
            mensaje = MIMEMultipart()
            mensaje["From"] = self.remitente
            mensaje["To"] = destinatario
            mensaje["Subject"] = self.asunto
            
            html = self.generar_html(otp)
            mensaje.attach(MIMEText(html, "html"))

            with smtplib.SMTP(self.servidor_smtp, self.puerto) as servidor:
                servidor.starttls()
                servidor.login(self.remitente, self.contraseña)
                servidor.send_message(mensaje)
            
            return True
        except Exception as e:
            print(f"Error enviando email: {str(e)}")
            return False



# Diccionario temporal para almacenar OTPs (en producción usa Redis)
otp_storage = {}

class PasswordResetInit(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return {"error": "El email es requerido"}, 400
        
        usuario = Usuario.query.filter_by(correo_usuario=email).first()
        if not usuario:
            return {"error": "Email no registrado"}, 404
        
        # Generar OTP
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Almacenar temporalmente asociado al usuario
        otp_storage[usuario.ID_usuario] = {
            'otp': otp,
            'expiry': datetime.now() + timedelta(minutes=15),
            'verified': False
        }
        
        # Enviar email
        sender = EmailSender()
        if not sender.enviar_otp(email, otp):
            return {"error": "Error al enviar el código de verificación"}, 500
        
        return {
            "message": "Código de verificación enviado al email", 
            "user_id": usuario.ID_usuario
        }, 200

class PasswordResetVerify(Resource):
    def post(self):
        data = request.get_json()
        user_id = data.get('user_id')
        otp = data.get('otp')
        
        if not all([user_id, otp]):
            return {"error": "User ID y OTP son requeridos"}, 400
        
        # Verificar en almacenamiento temporal
        otp_data = otp_storage.get(user_id)
        if not otp_data or datetime.now() > otp_data['expiry']:
            return {"error": "OTP inválido o expirado"}, 401
            
        if otp != otp_data['otp']:
            return {"error": "OTP incorrecto"}, 401
        
        # Marcar como verificado
        otp_storage[user_id]['verified'] = True
        
        return {"message": "OTP verificado correctamente"}, 200

class PasswordResetComplete(Resource):
    def post(self):
        data = request.get_json()
        user_id = data.get('user_id')
        new_password = data.get('new_password')
        
        if not all([user_id, new_password]):
            return {"error": "User ID y nueva contraseña son requeridos"}, 400
        
        # Verificar en almacenamiento
        otp_data = otp_storage.get(user_id)
        if not otp_data or not otp_data.get('verified'):
            return {"error": "OTP no verificado o inválido"}, 401
            
        # Cambiar contraseña
        usuario = Usuario.query.get(user_id)
        usuario.contrasena = new_password
        db.session.commit()
        
        # Limpiar el OTP
        del otp_storage[user_id]
        
        return {"message": "Contraseña actualizada exitosamente"}, 200
    

class VerifyCurrentPassword(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        current_password = data.get('current_password')
        user_id = data.get('user_id')  # <- lo agregamos

        if not all([email, current_password, user_id]):
            return {"error": "Email, contraseña actual y user_id son requeridos"}, 400

        usuario = Usuario.query.get(user_id)

        if not usuario:
            return {"error": "Usuario no encontrado"}, 404

        if usuario.correo_usuario != email:
            return {"error": "El correo no corresponde a tu cuenta"}, 400

        if not usuario.verify_password(current_password):
            return {"error": "Contraseña actual incorrecta"}, 400

        return {"message": "Contraseña verificada", "user_id": usuario.ID_usuario}, 200


class PasswordResetCompleteNoOTP(Resource):
    def post(self):
        data = request.get_json()
        user_id = data.get('user_id')
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not all([user_id, current_password, new_password]):
            return {"error": "Todos los campos son requeridos"}, 400
        
        usuario = Usuario.query.get(user_id)
        if not usuario:
            return {"error": "Usuario no encontrado"}, 404
            
        # Verificar que la contraseña actual sea correcta
        if not usuario.verify_password(current_password):
            return {"error": "Contraseña actual incorrecta"}, 400
            
        # Verificar que la nueva contraseña no sea igual a la actual
        if usuario.verify_password(new_password):
            return {"error": "La nueva contraseña no puede ser igual a la actual"}, 400
            
        # Cambiar contraseña usando el setter (esto genera el hash)
        usuario.contrasena = new_password
        db.session.commit()
        
        return {"message": "Contraseña actualizada exitosamente"}, 200



class CambioContrasena(Resource):
    def post(self):
        data = request.get_json()
        user_id = data.get('user_id')
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        # Validaciones básicas
        if not all([user_id, current_password, new_password, confirm_password]):
            return {"error": "Todos los campos son requeridos"}, 400
            
        if new_password != confirm_password:
            return {"error": "Las contraseñas nuevas no coinciden"}, 400
            
        if len(new_password) < 8 or not any(c.isalpha() for c in new_password) or not any(c.isdigit() for c in new_password):
            return {"error": "La nueva contraseña debe tener al menos 8 caracteres, incluyendo letras y números"}, 400
        
        # Obtener usuario
        usuario = Usuario.query.get(user_id)
        if not usuario:
            return {"error": "Usuario no encontrado"}, 404
            
        # Verificar contraseña actual
        if not usuario.verify_password(current_password):
            return {"error": "Contraseña actual incorrecta"}, 401
            
        # Cambiar contraseña
        usuario.contrasena = new_password
        db.session.commit()
        
        return {"message": "Contraseña actualizada exitosamente"}, 200