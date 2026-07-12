"""
QUANTUM WEB SEARCH - SERVIDOR COMPLETO
RUTA: C:/Users/elpel/OneDrive/Desktop/QuantumWebSearch/app.py
"""

import socket
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from quantum_web_search import QuantumWebSearch
from cerebro_cuantico import CerebroCuantico
from database import Database
from exportador import Exportador
from auth_jwt import AuthJWT
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_muy_segura_cambiala'
CORS(app)

# Configurar WebSockets
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Puerto automático
PUERTO = 5000
for p in range(5000, 5010):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('127.0.0.1', p)) != 0:
            PUERTO = p
            break

# Inicializar módulos
buscador = QuantumWebSearch()
cerebro = CerebroCuantico()
db = Database()
exportador = Exportador()
auth = AuthJWT()

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
    max_resultados = data.get('max_resultados', 100)
    resultados_web = data.get('resultados_web', 50)
    
    if not query:
        return jsonify({"error": "Escribe una consulta"})
    
    try:
        resultado = buscador.buscar(query, max_resultados_web=resultados_web, max_resultados_final=max_resultados)
        
        db.guardar_busqueda(
            query=query,
            algoritmo="Grover",
            resultados=len(resultado['resultados']),
            tiempo=resultado['tiempo']
        )
        
        socketio.emit('busqueda_completada', {
            'query': query,
            'resultados': len(resultado['resultados'])
        })
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/cerebro', methods=['POST'])
def cerebro_endpoint():
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({"error": "Escribe una consulta"})
    
    try:
        resultado = cerebro.procesar_consulta(query)
        db.guardar_busqueda(query=query, algoritmo="Cerebro", resultados=1, tiempo=0)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)})

# ================================================================
# RUTAS DE HISTORIAL Y ESTADÍSTICAS
# ================================================================

@app.route('/api/historial', methods=['GET'])
def historial():
    try:
        historial = db.obtener_historial(50)
        return jsonify([{
            "id": h[0],
            "query": h[1],
            "algoritmo": h[2],
            "resultados": h[3],
            "tiempo": h[4],
            "fecha": h[5]
        } for h in historial])
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/estadisticas_db', methods=['GET'])
def estadisticas_db():
    try:
        stats = db.obtener_estadisticas()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)})

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
        nombre_base = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if formato == 'json':
            archivo = exportador.exportar_json(resultados, f"{nombre_base}.json")
        elif formato == 'csv':
            archivo = exportador.exportar_csv(resultados, f"{nombre_base}.csv")
        elif formato == 'pdf':
            archivo = exportador.exportar_pdf(resultados, "Resultados de búsqueda", f"{nombre_base}.pdf")
        else:
            return jsonify({"error": "Formato no soportado"})
        
        return send_file(archivo, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)})

# ================================================================
# RUTAS DE FEEDBACK
# ================================================================

@app.route('/api/feedback', methods=['POST'])
def feedback():
    data = request.json
    query = data.get('query', '')
    url = data.get('url', '')
    relevancia = data.get('relevancia', 0)
    
    try:
        with open("feedback_usuarios.json", "a", encoding='utf-8') as f:
            json.dump({
                "fecha": datetime.now().isoformat(),
                "query": query,
                "url": url,
                "relevancia": relevancia
            }, f)
            f.write("\n")
        return jsonify({"mensaje": "Feedback registrado"})
    except:
        return jsonify({"error": "Error al registrar feedback"})

# ================================================================
# RUTAS DE AUTENTICACIÓN JWT
# ================================================================

@app.route('/api/registrar', methods=['POST'])
def registrar():
    data = request.json
    email = data.get('email', '')
    password = data.get('password', '')
    nombre = data.get('nombre', '')
    
    if not email or not password or not nombre:
        return jsonify({"error": "Todos los campos son obligatorios"})
    
    resultado = auth.registrar(email, password, nombre)
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

@app.route('/api/verificar', methods=['GET'])
def verificar():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    usuario = auth.verificar_token(token)
    if usuario:
        return jsonify({"valido": True, "usuario": usuario})
    return jsonify({"valido": False})

# ================================================================
# WEBSOCKET EVENTOS
# ================================================================

@socketio.on('connect')
def handle_connect():
    print('🔗 Cliente conectado')
    emit('mensaje', {'data': 'Conectado al servidor WebSocket'})

@socketio.on('disconnect')
def handle_disconnect():
    print('🔗 Cliente desconectado')

@socketio.on('buscar_tiempo_real')
def handle_buscar_tiempo_real(data):
    """Búsqueda en tiempo real con WebSockets"""
    query = data.get('query', '')
    if not query or len(query) < 3:
        emit('resultados_tiempo_real', {'resultados': []})
        return
    
    try:
        resultado = buscador.buscar(query, max_resultados_web=10, max_resultados_final=5)
        emit('resultados_tiempo_real', {
            'query': query,
            'resultados': resultado['resultados'],
            'total': len(resultado['resultados'])
        })
    except Exception as e:
        emit('error', {'mensaje': str(e)})

@app.route('/api/buscar_multi', methods=['POST'])
def buscar_multi():
    data = request.json
    query = data.get('query', '')
    max_resultados = data.get('max_resultados', 20)
    
    if not query:
        return jsonify({"error": "Escribe una consulta"})
    
    try:
        resultado = buscador.buscar_multi_fuente(query, max_resultados)
        
        db.guardar_busqueda(
            query=query,
            algoritmo="MultiFuente",
            resultados=len(resultado),
            tiempo=0
        )
        
        return jsonify({
            "resultados": resultado,
            "total": len(resultado),
            "fuentes": ["Google", "Wikipedia", "YouTube", "News"]
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/shor', methods=['POST'])
def shor_endpoint():
    data = request.json
    numero = data.get('numero', 0)
    
    if numero < 2:
        return jsonify({"error": "El número debe ser mayor que 1"})
    
    try:
        from shor_algorithm import ShorAlgorithm
        shor = ShorAlgorithm()
        factores = shor.factorizar(numero)
        
        return jsonify({
            "numero": numero,
            "factores": factores,
            "factorizacion": f"{numero} = {factores[0]} × {factores[1]}"
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/qaoa', methods=['POST'])
def qaoa_endpoint():
    data = request.json
    problema = data.get('problema', 'qaoa')
    
    try:
        from qaoa_algorithm import QAOAAlgorithm
        qaoa = QAOAAlgorithm()
        
        if problema == 'mochila':
            pesos = data.get('pesos', [2, 3, 4, 5])
            valores = data.get('valores', [3, 4, 5, 6])
            capacidad = data.get('capacidad', 8)
            resultado = qaoa.problema_mochila(pesos, valores, capacidad)
        else:
            n_qubits = data.get('n_qubits', 4)
            p = data.get('p', 1)
            iteraciones = data.get('iteraciones', 20)
            resultado = qaoa.optimizar(n_qubits, p, iteraciones)
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)})
# ================================================================
# INICIO
# ================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("QUANTUM WEB SEARCH - SERVIDOR COMPLETO")
    print("="*70)
    print(f"\nURL: http://localhost:{PUERTO}")
    print("Endpoints:")
    print("  GET  /")
    print("  POST /api/buscar")
    print("  POST /api/cerebro")
    print("  GET  /api/historial")
    print("  GET  /api/estadisticas_db")
    print("  POST /api/exportar")
    print("  POST /api/feedback")
    print("  POST /api/registrar")
    print("  POST /api/login")
    print("  GET  /api/verificar")
    print("  WS   /socket.io")
    print("="*70)
    socketio.run(app, host='0.0.0.0', port=PUERTO, debug=True)