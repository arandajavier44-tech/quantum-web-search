"""
QUANTUM WEB SEARCH - SERVIDOR WEB (VERSIÓN COMPLETA)
RUTA: C:\Users\elpel\OneDrive\Desktop\QuantumWebSearch\app.py
"""

import socket
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from quantum_web_search import QuantumWebSearch
from auth import AuthSystem
from dashboard import Dashboard
from exportador import Exportador

app = Flask(__name__)
CORS(app)

# Configuración
PUERTO = 5000
for p in range(5000, 5010):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('127.0.0.1', p)) != 0:
            PUERTO = p
            break

# Inicializar módulos
buscador = QuantumWebSearch()
auth = AuthSystem()
dashboard = Dashboard()
exportador = Exportador()

# ================================================================
# RUTAS PRINCIPALES
# ================================================================

@app.route('/')
def index():
    return render_template('quantum_web.html')

# ================================================================
# RUTAS DE BÚSQUEDA
# ================================================================

@app.route('/api/buscar', methods=['POST'])
def buscar():
    data = request.json
    query = data.get('query', '')
    max_resultados = data.get('max_resultados', 10)
    token = data.get('token', '')
    
    if not query:
        return jsonify({"error": "Escribe una consulta"})
    
    try:
        resultado = buscador.buscar(query, max_resultados_final=max_resultados)
        
        # Guardar historial del usuario si está autenticado
        if token:
            auth.guardar_historial(token, query)
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)})

# ================================================================
# RUTAS DE AUTENTICACIÓN
# ================================================================

@app.route('/api/registrar', methods=['POST'])
def registrar():
    data = request.json
    email = data.get('email', '')
    nombre = data.get('nombre', '')
    password = data.get('password', '')
    
    if not email or not nombre or not password:
        return jsonify({"error": "Todos los campos son obligatorios"})
    
    resultado = auth.registrar_usuario(email, nombre, password)
    return jsonify(resultado)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email', '')
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({"error": "Email y contraseña son obligatorios"})
    
    resultado = auth.login(email, password)
    return jsonify(resultado)

@app.route('/api/usuario', methods=['GET'])
def usuario():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    usuario = auth.obtener_usuario(token)
    
    if not usuario:
        return jsonify({"error": "Sesión inválida"})
    
    return jsonify({
        "nombre": usuario["nombre"],
        "email": usuario["email"],
        "preferencias": usuario["preferencias"],
        "estadisticas": usuario["estadisticas"],
        "historial": usuario["historial"][-10:]
    })

@app.route('/api/preferencia', methods=['POST'])
def preferencia():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    data = request.json
    clave = data.get('clave', '')
    valor = data.get('valor', '')
    
    resultado = auth.guardar_preferencia(token, clave, valor)
    return jsonify(resultado)

# ================================================================
# RUTAS DE DASHBOARD
# ================================================================

@app.route('/api/estadisticas', methods=['GET'])
def estadisticas():
    stats = dashboard.obtener_estadisticas()
    return jsonify(stats)

@app.route('/api/grafico_tendencia', methods=['GET'])
def grafico_tendencia():
    img = dashboard.generar_grafico_tendencia()
    if img:
        return jsonify({"imagen": img})
    return jsonify({"error": "No hay datos suficientes"})

@app.route('/api/grafico_top', methods=['GET'])
def grafico_top():
    img = dashboard.generar_grafico_top()
    if img:
        return jsonify({"imagen": img})
    return jsonify({"error": "No hay datos suficientes"})

# ================================================================
# RUTAS DE EXPORTACIÓN
# ================================================================

@app.route('/api/exportar', methods=['POST'])
def exportar():
    data = request.json
    formato = data.get('formato', 'json')
    resultados = data.get('resultados', [])
    
    if not resultados:
        return jsonify({"error": "No hay datos para exportar"})
    
    try:
        if formato == 'json':
            archivo = exportador.exportar_json(resultados, f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        elif formato == 'csv':
            archivo = exportador.exportar_csv(resultados, f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        elif formato == 'pdf':
            archivo = exportador.exportar_pdf(resultados, "Resultados de búsqueda", f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        else:
            return jsonify({"error": "Formato no soportado"})
        
        return send_file(archivo, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)})

# ================================================================
# RUTAS DE LIMPIEZA
# ================================================================

@app.route('/api/limpiar_cache', methods=['POST'])
def limpiar_cache():
    try:
        with open("cache_cuantico.json", "w", encoding='utf-8') as f:
            json.dump({}, f)
        return jsonify({"mensaje": "Caché limpiado"})
    except:
        return jsonify({"error": "No se pudo limpiar caché"})


from multi_search import MultiSearch

def buscar_multi_fuente(self, query, max_resultados=20):
    """Busca en múltiples fuentes y combina resultados."""
    multi = MultiSearch()
    resultados = multi.buscar_en_todas(query, max_por_fuente=5)
    
    # Filtrar con Grover
    return self.filtrar_con_grover(resultados, query, max_resultados)

# ================================================================
# INICIO
# ================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🌐 QUANTUM WEB SEARCH - VERSIÓN COMPLETA")
    print("="*70)
    print(f"\n📌 URL: http://localhost:{PUERTO}")
    print("📌 Características:")
    print("   🔐 Autenticación de usuarios")
    print("   📊 Dashboard en tiempo real")
    print("   📤 Exportación (JSON, CSV, PDF)")
    print("   ⚡ Grover adaptativo")
    print("   💾 Caché cuántico")
    print("="*70)
    app.run(host='0.0.0.0', port=PUERTO, debug=True)