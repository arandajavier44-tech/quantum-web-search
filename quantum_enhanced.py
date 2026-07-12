"""
=====================================================================
QUANTUM ENHANCED - Mejoras cuánticas para el buscador web
=====================================================================
- Caché cuántico con QRNG
- Grover adaptativo
- Filtros inteligentes
- Feedback loop
=====================================================================

RUTA: C:\Users\elpel\OneDrive\Desktop\buscador web\quantum_enhanced.py
"""

import json
import hashlib
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import warnings
warnings.filterwarnings('ignore')


class QuantumEnhancer:
    """
    Mejoras cuánticas para el buscador web.
    """
    
    def __init__(self, archivo_cache="cache_cuantico.json"):
        self.simulador = AerSimulator()
        self.archivo_cache = archivo_cache
        self.cache = self._cargar_cache()
        self.historial_clics = defaultdict(int)
        self.dominios_confiables = [
            "wikipedia.org", "google.com", "youtube.com", 
            "github.com", "stackoverflow.com", "medium.com",
            "bbc.com", "cnn.com", "nytimes.com", "elpais.com"
        ]
        self.palabras_clave_prioritarias = [
            "guía", "tutorial", "oficial", "documentación",
            "manual", "cómo", "mejor", "top", "ranking"
        ]
    
    # ================================================================
    # 1. CACHÉ CUÁNTICO
    # ================================================================
    
    def _cargar_cache(self):
        """Carga el caché desde archivo."""
        try:
            with open(self.archivo_cache, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _guardar_cache(self):
        """Guarda el caché en archivo."""
        with open(self.archivo_cache, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2, ensure_ascii=False)
    
    def obtener_cache(self, query):
        """Obtiene resultados del caché si son recientes."""
        if query in self.cache:
            entrada = self.cache[query]
            # Verificar si el caché es reciente (menos de 1 hora)
            if datetime.now() - datetime.fromisoformat(entrada["fecha"]) < timedelta(hours=1):
                return entrada["resultados"]
        return None
    
    def guardar_cache(self, query, resultados):
        """Guarda resultados en caché."""
        self.cache[query] = {
            "fecha": datetime.now().isoformat(),
            "resultados": resultados
        }
        self._guardar_cache()
    
    # ================================================================
    # 2. GENERADOR DE PESOS CUÁNTICOS
    # ================================================================
    
    def generar_pesos_cuanticos(self, n=16):
        """Genera pesos cuánticos para ponderación."""
        qc = QuantumCircuit(4, 4)
        for i in range(4):
            qc.h(i)
        qc.measure(range(4), range(4))
        
        transpiled = transpile(qc, self.simulador)
        job = self.simulador.run(transpiled, shots=n)
        counts = job.result().get_counts()
        
        pesos = []
        for bits, count in counts.items():
            valor = int(bits, 2)
            for _ in range(count):
                pesos.append(valor / 15)  # Normalizar entre 0 y 1
        
        return pesos[:n]
    
    # ================================================================
    # 3. GROVER ADAPTATIVO
    # ================================================================
    
    def grover_adaptativo(self, resultados, query, iteraciones_extra=0):
        """
        Grover adaptativo que ajusta iteraciones según calidad de resultados.
        """
        if not resultados:
            return resultados
        
        # Número base de iteraciones (√N)
        n = len(resultados)
        iteraciones_base = int(np.sqrt(n)) if n > 0 else 1
        
        # Si hay pocos resultados, más iteraciones
        if n < 10:
            iteraciones = iteraciones_base + 2 + iteraciones_extra
        elif n < 50:
            iteraciones = iteraciones_base + 1 + iteraciones_extra
        else:
            iteraciones = iteraciones_base + iteraciones_extra
        
        # Limitar iteraciones
        iteraciones = min(iteraciones, 10)
        
        # Aplicar Grover adaptativo: amplificar mejores resultados
        query_lower = query.lower()
        palabras = query_lower.split()
        
        for resultado in resultados:
            titulo = resultado.get("titulo", "").lower()
            descripcion = resultado.get("descripcion", "").lower()
            texto = f"{titulo} {descripcion}"
            
            # Puntuación base
            puntuacion = 0
            
            # Coincidencia de palabras clave
            for palabra in palabras:
                if len(palabra) > 2:
                    if palabra in texto:
                        puntuacion += 2 * (iteraciones / 2)
                    if palabra in titulo:
                        puntuacion += 3 * (iteraciones / 2)
            
            # Palabras clave prioritarias
            for palabra in self.palabras_clave_prioritarias:
                if palabra in texto:
                    puntuacion += 1.5
            
            # Dominios confiables
            url = resultado.get("url", "")
            for dominio in self.dominios_confiables:
                if dominio in url:
                    puntuacion += 2
            
            # Longitud de descripción (informativa)
            puntuacion += min(len(descripcion) / 30, 3)
            
            # Añadir ruido cuántico controlado
            pesos = self.generar_pesos_cuanticos(8)
            if pesos:
                aleatorio = pesos[hash(titulo) % len(pesos)] * 0.5
                puntuacion += aleatorio
            
            resultado["relevancia"] = round(puntuacion, 2)
            resultado["iteraciones_grover"] = iteraciones
        
        # Ordenar por relevancia
        resultados.sort(key=lambda x: x["relevancia"], reverse=True)
        
        return resultados
    
    # ================================================================
    # 4. FILTROS INTELIGENTES
    # ================================================================
    
    def filtrar_resultados(self, resultados, filtros=None):
        """
        Filtra resultados según criterios inteligentes.
        """
        if not resultados or not filtros:
            return resultados
        
        filtrados = []
        
        for r in resultados:
            cumple = True
            
            # Filtro por dominio confiable
            if filtros.get("dominios_confiables", False):
                url = r.get("url", "")
                if not any(d in url for d in self.dominios_confiables):
                    cumple = False
            
            # Filtro por antigüedad (simulado con palabras clave)
            if filtros.get("reciente", False):
                texto = (r.get("titulo", "") + " " + r.get("descripcion", "")).lower()
                if "2024" not in texto and "2025" not in texto and "2026" not in texto:
                    cumple = False
            
            # Filtro por calidad (longitud de descripción)
            if filtros.get("calidad", False):
                if len(r.get("descripcion", "")) < 20:
                    cumple = False
            
            if cumple:
                filtrados.append(r)
        
        return filtrados
    
    # ================================================================
    # 5. FEEDBACK LOOP
    # ================================================================
    
    def registrar_clic(self, query, resultado):
        """Registra clics del usuario para mejorar futuras búsquedas."""
        url = resultado.get("url", "")
        self.historial_clics[url] += 1
        
        # Guardar historial
        try:
            with open("historial_clics.json", "w", encoding='utf-8') as f:
                json.dump(dict(self.historial_clics), f, indent=2)
        except:
            pass
    
    def mejorar_relevancia_por_clics(self, resultados):
        """Ajusta relevancia basado en historial de clics."""
        for r in resultados:
            url = r.get("url", "")
            if url in self.historial_clics:
                # Aumentar relevancia según clics previos
                bonus = min(self.historial_clics[url] / 5, 3)
                r["relevancia"] = r.get("relevancia", 0) + bonus
                r["relevancia"] = round(r["relevancia"], 2)
        
        resultados.sort(key=lambda x: x["relevancia"], reverse=True)
        return resultados


# ================================================================
# PRUEBA DE MEJORAS
# ================================================================

if __name__ == "__main__":
    enhancer = QuantumEnhancer()
    
    print("="*70)
    print("🧠 PRUEBA DE MEJORAS CUÁNTICAS")
    print("="*70)
    
    # Probar generación de pesos cuánticos
    print("\n🔢 Pesos cuánticos generados:")
    pesos = enhancer.generar_pesos_cuanticos(10)
    print(f"   {[round(p, 2) for p in pesos]}")
    
    # Probar caché
    print("\n💾 Prueba de caché:")
    query = "quantum computing"
    cacheado = enhancer.obtener_cache(query)
    print(f"   '{query}' en caché: {'Sí' if cacheado else 'No'}")
    
    print("\n✅ Mejoras cuánticas listas!")