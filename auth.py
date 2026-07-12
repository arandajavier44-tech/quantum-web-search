"""
SISTEMA DE AUTENTICACION - Usuarios y preferencias
"""

import json
import hashlib
import secrets
from datetime import datetime
from collections import defaultdict

class AuthSystem:
    def __init__(self, archivo_usuarios="usuarios.json"):
        self.archivo_usuarios = archivo_usuarios
        self.usuarios = self._cargar_usuarios()
        self.sesiones = {}
        self.preferencias = defaultdict(dict)
    
    def _cargar_usuarios(self):
        try:
            with open(self.archivo_usuarios, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _guardar_usuarios(self):
        with open(self.archivo_usuarios, 'w', encoding='utf-8') as f:
            json.dump(self.usuarios, f, indent=2, ensure_ascii=False)
    
    def registrar_usuario(self, email, nombre, password):
        if email in self.usuarios:
            return {"error": "El email ya esta registrado"}
        
        salt = secrets.token_hex(16)
        hash_password = hashlib.sha256((password + salt).encode()).hexdigest()
        
        self.usuarios[email] = {
            "nombre": nombre,
            "email": email,
            "password_hash": hash_password,
            "salt": salt,
            "fecha_registro": datetime.now().isoformat(),
            "preferencias": {
                "max_resultados": 10,
                "fuentes_prioritarias": ["google", "wikipedia"],
                "modo_oscuro": False,
                "idioma": "es"
            },
            "historial": [],
            "estadisticas": {
                "total_busquedas": 0,
                "clics": 0,
                "feedback": 0
            }
        }
        
        self._guardar_usuarios()
        return {"exito": True, "mensaje": "Usuario registrado correctamente"}
    
    def login(self, email, password):
        if email not in self.usuarios:
            return {"error": "Usuario no encontrado"}
        
        usuario = self.usuarios[email]
        hash_password = hashlib.sha256((password + usuario["salt"]).encode()).hexdigest()
        
        if hash_password != usuario["password_hash"]:
            return {"error": "Contraseña incorrecta"}
        
        token = secrets.token_urlsafe(32)
        self.sesiones[token] = {
            "email": email,
            "fecha": datetime.now().isoformat()
        }
        
        return {
            "exito": True,
            "token": token,
            "usuario": {
                "nombre": usuario["nombre"],
                "email": usuario["email"],
                "preferencias": usuario["preferencias"]
            }
        }
    
    def obtener_usuario(self, token):
        if token not in self.sesiones:
            return None
        
        email = self.sesiones[token]["email"]
        return self.usuarios.get(email)
    
    def guardar_preferencia(self, token, clave, valor):
        email = self.sesiones.get(token, {}).get("email")
        if not email or email not in self.usuarios:
            return {"error": "Sesion invalida"}
        
        self.usuarios[email]["preferencias"][clave] = valor
        self._guardar_usuarios()
        return {"exito": True}
    
    def guardar_historial(self, token, busqueda):
        email = self.sesiones.get(token, {}).get("email")
        if not email or email not in self.usuarios:
            return
        
        self.usuarios[email]["historial"].append({
            "fecha": datetime.now().isoformat(),
            "query": busqueda
        })
        self.usuarios[email]["estadisticas"]["total_busquedas"] += 1
        self._guardar_usuarios()
    
    def cerrar_sesion(self, token):
        if token in self.sesiones:
            del self.sesiones[token]
            return {"exito": True}
        return {"error": "Sesion no encontrada"}