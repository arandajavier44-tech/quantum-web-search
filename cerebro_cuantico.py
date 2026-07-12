"""
CEREBRO CUÁNTICO INTEGRADO
RUTA: C:/Users/elpel/OneDrive/Desktop/QuantumWebSearch/cerebro_cuantico.py
"""

import json
from quantum_bridge import QuantumBridge

class CerebroCuantico:
    def __init__(self):
        self.bridge = QuantumBridge()
        self.historial = []
    
    def procesar_consulta(self, query):
        resultados = {
            "query": query,
            "id": self._generar_id_cuantico(),
            "resultados_busqueda": self._buscar(query),
            "seguridad": self._verificar_seguridad(),
            "tendencias": self._detectar_tendencias(query),
            "optimizacion": self._optimizar_palabras(query)
        }
        self.historial.append(resultados)
        return resultados
    
    def _generar_id_cuantico(self):
        resultado = self.bridge.conectar("genera 8 números aleatorios")
        numeros = [n["valor"] for n in resultado["resultado"]["numeros"]]
        return ''.join(str(n) for n in numeros[:8])
    
    def _buscar(self, query):
        resultado = self.bridge.conectar(f"busca {query} en internet")
        return resultado["resultado"]
    
    def _verificar_seguridad(self):
        resultado = self.bridge.conectar("crea un estado entrelazado")
        return {"encriptada": True, "fidelidad": resultado["resultado"]["fidelidad"]}
    
    def _detectar_tendencias(self, query):
        historial = ["python", "quantum", "ia", "python", "quantum", "web"]
        cadena = ''.join('1' if q in query.lower() else '0' for q in historial)
        resultado = self.bridge.conectar(f"descubre el patrón en {cadena}")
        return resultado["resultado"]
    
    def _optimizar_palabras(self, query):
        palabras = query.split()
        resultados = []
        for p in palabras[:5]:
            res = self.bridge.conectar(f"simula la energía de {p}")
            resultados.append({"palabra": p, "energia": res["resultado"]["energia"]})
        return resultados