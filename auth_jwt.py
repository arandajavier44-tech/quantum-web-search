"""
AUTENTICACIÓN JWT
RUTA: C:/Users/elpel/OneDrive/Desktop/QuantumWebSearch/auth_jwt.py
"""

import jwt
import bcrypt
import json
from datetime import datetime, timedelta

SECRET_KEY = "tu_clave_secreta_muy_segura_cambiala"

class AuthJWT:
    def __init__(self, archivo_usuarios="usuarios.json"):
        self.archivo_usuarios = archivo_usuarios
        self.usuarios = self._cargar_usuarios()
    
    def _cargar_usuarios(self):
        try:
            with open(self.archivo_usuarios, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _guardar_usuarios(self):
        with open(self.archivo_usuarios, 'w', encoding='utf-8') as f:
            json.dump(self.usuarios, f, indent=2, ensure_ascii=False)
    
    def registrar(self, email, password, nombre):
        if email in self.usuarios:
            return {"error": "El usuario ya existe"}
        
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        self.usuarios[email] = {
            "nombre": nombre,
            "email": email,
            "password": hashed.decode(),
            "fecha_registro": datetime.now().isoformat()
        }
        self._guardar_usuarios()
        return {"mensaje": "Usuario registrado correctamente"}
    
    def login(self, email, password):
        if email not in self.usuarios:
            return {"error": "Usuario no encontrado"}
        
        usuario = self.usuarios[email]
        if not bcrypt.checkpw(password.encode(), usuario["password"].encode()):
            return {"error": "Contraseña incorrecta"}
        
        token = jwt.encode({
            "email": email,
            "nombre": usuario["nombre"],
            "exp": datetime.utcnow() + timedelta(days=7)
        }, SECRET_KEY, algorithm="HS256")
        
        return {"token": token, "usuario": {"nombre": usuario["nombre"], "email": email}}
    
    def verificar_token(self, token):
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return None