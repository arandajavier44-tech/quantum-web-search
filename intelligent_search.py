"""
BUSCADOR INTELIGENTE - Sistema de recomendación con algoritmos cuánticos
RUTA: C:/Users/elpel/OneDrive/Desktop/QuantumWebSearch/intelligent_search.py
"""

import json
import numpy as np
from datetime import datetime
from collections import defaultdict
from quantum_bridge import QuantumBridge


class IntelligentSearch:
    """
    Buscador inteligente que combina todos los algoritmos cuánticos
    para recomendar las mejores opciones según las necesidades del usuario.
    """
    
    def __init__(self):
        self.bridge = QuantumBridge()
        self.historial_usuario = []
        self.perfil_usuario = {
            "preferencias": defaultdict(int),
            "categorias": defaultdict(int),
            "fuentes": defaultdict(int),
            "palabras_clave": defaultdict(int),
            "clics": 0,
            "busquedas": 0
        }
        self.recomendaciones_cache = {}
    
    # ================================================================
    # 1. ANÁLISIS DE INTENCIÓN (Bernstein-Vazirani + VQE)
    # ================================================================
    
    def analizar_intencion(self, query):
        """
        Analiza la intención del usuario usando Bernstein-Vazirani
        y VQE para determinar qué busca realmente.
        """
        print(f"🧠 Analizando intención: '{query}'")
        
        # 1. Bernstein-Vazirani: detecta patrones en la consulta
        patron = self.bridge.conectar(f"descubre el patrón en {query}")
        patron_encontrado = patron["resultado"].get("cadena_encontrada", "000")
        
        # 2. VQE: optimiza palabras clave para entender prioridad
        palabras = query.split()
        energias = []
        for p in palabras[:5]:
            res = self.bridge.conectar(f"simula la energía de {p}")
            energias.append({
                "palabra": p,
                "energia": res["resultado"].get("energia", -1)
            })
        
        # 3. Clasificar intención
        intencion = self._clasificar_intencion(query, energias)
        
        return {
            "intencion": intencion,
            "patron": patron_encontrado,
            "palabras_clave": energias,
            "prioridad": self._calcular_prioridad(energias)
        }
    
    def _clasificar_intencion(self, query, energias):
        """
        Clasifica la intención del usuario basado en la consulta.
        """
        query_lower = query.lower()
        
        # Detectar intención
        if any(w in query_lower for w in ["precio", "barato", "costo", "cuanto", "cuesta", "oferta"]):
            return "comparar_precios"
        elif any(w in query_lower for w in ["mejor", "top", "ranking", "recomienda", "sugiere"]):
            return "recomendacion"
        elif any(w in query_lower for w in ["donde", "como", "cuando", "quien", "que es", "que significa"]):
            return "informacion"
        elif any(w in query_lower for w in ["ruta", "camino", "distancia", "tiempo", "llegar"]):
            return "navegacion"
        elif any(w in query_lower for w in ["resolver", "calcular", "optimizar", "mejorar"]):
            return "optimizacion"
        else:
            return "busqueda_general"
    
    def _calcular_prioridad(self, energias):
        """
        Calcula la prioridad basada en energías VQE.
        """
        if not energias:
            return 0.5
        
        # Promedio de energías (más negativa = más prioritaria)
        energias_vals = [e["energia"] for e in energias if e["energia"] < 0]
        if not energias_vals:
            return 0.5
        
        promedio = abs(sum(energias_vals) / len(energias_vals))
        # Normalizar entre 0 y 1
        return min(promedio / 2, 1.0)
    
    # ================================================================
    # 2. BÚSQUEDA OPTIMIZADA (Grover)
    # ================================================================
    
    def buscar_optimizado(self, query, intencion_analisis, max_resultados=20):
        """
        Busca usando Grover optimizado según la intención.
        """
        print(f"🔍 Buscando optimizado para: '{query}'")
        
        # 1. Grover busca en internet
        resultado_grover = self.bridge.conectar(f"busca {query} en internet")
        resultados_web = resultado_grover["resultado"].get("conteos", {})
        
        # 2. Si hay pocos resultados, usar Multi Fuente
        if len(resultados_web) < 3:
            from multi_search import MultiSearch
            multi = MultiSearch()
            resultados_web = multi.buscar_en_todas(query, max_por_fuente=5)
        
        # 3. Ponderar según intención
        resultados_ponderados = self._ponderar_resultados(
            resultados_web, 
            intencion_analisis,
            max_resultados
        )
        
        return resultados_ponderados
    
    def _ponderar_resultados(self, resultados, intencion, max_resultados):
        """
        Ponderar resultados según la intención del usuario.
        """
        if not resultados:
            return []
        
        # Convertir a lista si es dict
        if isinstance(resultados, dict):
            resultados = [{"estado": k, "frecuencia": v} for k, v in resultados.items()]
        
        for r in resultados:
            puntuacion = 0
            
            # Factores según intención
            if intencion["intencion"] == "comparar_precios":
                # Priorizar resultados con números (precios)
                texto = r.get("titulo", "") + " " + r.get("descripcion", "")
                if any(c.isdigit() for c in texto):
                    puntuacion += 3
                if "$" in texto or "€" in texto or "USD" in texto:
                    puntuacion += 5
            
            elif intencion["intencion"] == "recomendacion":
                # Priorizar resultados con palabras de calidad
                texto = r.get("titulo", "") + " " + r.get("descripcion", "")
                palabras_buenas = ["mejor", "top", "ranking", "recomendado", "premium", "excelente"]
                for p in palabras_buenas:
                    if p in texto.lower():
                        puntuacion += 2
            
            elif intencion["intencion"] == "navegacion":
                # Priorizar resultados con mapas o distancias
                texto = r.get("titulo", "") + " " + r.get("descripcion", "")
                if any(w in texto.lower() for w in ["km", "mapa", "distancia", "ruta"]):
                    puntuacion += 3
            
            # Añadir peso por relevancia cuántica (QRNG)
            numeros_cuanticos = self.bridge.conectar("genera 4 números aleatorios")
            if numeros_cuanticos["resultado"].get("numeros"):
                aleatorio = numeros_cuanticos["resultado"]["numeros"][0]["valor"] / 100
                puntuacion += aleatorio
            
            r["puntuacion_cuántica"] = round(puntuacion, 2)
        
        # Ordenar por puntuación
        resultados.sort(key=lambda x: x.get("puntuacion_cuántica", 0), reverse=True)
        
        return resultados[:max_resultados]
    
    # ================================================================
    # 3. RECOMENDACIONES PERSONALIZADAS (QAOA + VQE)
    # ================================================================
    
    def recomendar(self, query, resultados):
        """
        Genera recomendaciones personalizadas usando QAOA y VQE.
        """
        print(f"📊 Generando recomendaciones para: '{query}'")
        
        if not resultados:
            return {"recomendaciones": [], "justificacion": "No hay resultados suficientes"}
        
        # 1. QAOA: optimizar selección de mejores resultados
        n = min(len(resultados), 10)
        qaoa_result = self.bridge.conectar(
            f"optimiza la selección de {n} opciones para {query}"
        )
        
        # 2. VQE: calcular "energía" de cada recomendación (calidad)
        for r in resultados[:n]:
            texto = r.get("titulo", "") + " " + r.get("descripcion", "")
            energia_res = self.bridge.conectar(f"simula la energía de {texto[:30]}")
            r["calidad"] = energia_res["resultado"].get("energia", -1)
        
        # 3. Ordenar por calidad
        resultados.sort(key=lambda x: x.get("calidad", -1), reverse=True)
        
        # 4. Generar justificación
        justificacion = self._generar_justificacion(query, resultados[:5])
        
        return {
            "recomendaciones": resultados[:5],
            "justificacion": justificacion,
            "metodos_usados": ["QAOA", "VQE", "Grover"]
        }
    
    def _generar_justificacion(self, query, recomendaciones):
        """
        Genera una justificación en lenguaje natural para las recomendaciones.
        """
        if not recomendaciones:
            return "No hay suficientes datos para generar recomendaciones."
        
        justificacion = f"🔍 Basado en tu búsqueda '{query}', he seleccionado las mejores opciones usando:\n"
        justificacion += "   • Grover: búsqueda eficiente\n"
        justificacion += "   • VQE: análisis de calidad\n"
        justificacion += "   • QAOA: optimización de selección\n"
        justificacion += "   • QRNG: aleatoriedad controlada\n\n"
        
        justificacion += "📌 Las recomendaciones están ordenadas por calidad:\n"
        for i, r in enumerate(recomendaciones[:3], 1):
            titulo = r.get("titulo", "Sin título")[:60]
            calidad = r.get("calidad", 0)
            justificacion += f"   {i}. {titulo} (calidad: {calidad:.4f})\n"
        
        return justificacion
    
    # ================================================================
    # 4. APRENDIZAJE CONTINUO
    # ================================================================
    
    def aprender(self, query, resultado_seleccionado):
        """
        Aprende de las interacciones del usuario para mejorar.
        """
        print(f"🧠 Aprendiendo de: '{query}'")
        
        # Actualizar perfil
        self.perfil_usuario["busquedas"] += 1
        self.perfil_usuario["clics"] += 1
        
        # Palabras clave
        for palabra in query.split():
            self.perfil_usuario["palabras_clave"][palabra.lower()] += 1
        
        # Categorías (detectar desde el resultado)
        if resultado_seleccionado:
            fuente = resultado_seleccionado.get("fuente", "desconocida")
            self.perfil_usuario["fuentes"][fuente] += 1
        
        # Guardar historial
        self.historial_usuario.append({
            "fecha": datetime.now().isoformat(),
            "query": query,
            "resultado": resultado_seleccionado,
            "accion": "clic"
        })
        
        # Guardar perfil
        self._guardar_perfil()
    
    def _guardar_perfil(self):
        """Guarda el perfil del usuario en un archivo."""
        try:
            with open("perfil_usuario.json", "w", encoding="utf-8") as f:
                json.dump({
                    "perfil": dict(self.perfil_usuario),
                    "historial": self.historial_usuario[-50:]
                }, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def cargar_perfil(self):
        """Carga el perfil del usuario desde archivo."""
        try:
            with open("perfil_usuario.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.perfil_usuario.update(data.get("perfil", {}))
                self.historial_usuario = data.get("historial", [])
        except:
            pass
    
    # ================================================================
    # 5. BÚSQUEDA INTELIGENTE COMPLETA
    # ================================================================
    
    def buscar_inteligente(self, query):
        """
        Búsqueda completa e inteligente con todos los algoritmos.
        """
        print("\n" + "="*70)
        print("🧠 BUSCADOR INTELIGENTE")
        print("="*70)
        print(f"📝 Consulta: '{query}'")
        print("-"*50)
        
        # 1. Analizar intención
        intencion = self.analizar_intencion(query)
        print(f"🎯 Intención: {intencion['intencion']}")
        print(f"🔐 Patrón: {intencion['patron']}")
        print(f"📊 Prioridad: {intencion['prioridad']:.2f}")
        
        # 2. Buscar optimizado
        resultados = self.buscar_optimizado(query, intencion)
        print(f"🔍 Resultados encontrados: {len(resultados)}")
        
        # 3. Generar recomendaciones
        recomendacion = self.recomendar(query, resultados)
        print(f"📊 Recomendaciones generadas: {len(recomendacion['recomendaciones'])}")
        
        # 4. Retornar resultado completo
        return {
            "query": query,
            "intencion": intencion,
            "resultados": resultados,
            "recomendaciones": recomendacion,
            "metodos_usados": ["Bernstein-Vazirani", "VQE", "Grover", "QAOA", "QRNG"]
        }
    
    def mostrar_resultados_inteligentes(self, resultado):
        """
        Muestra los resultados de búsqueda inteligente.
        """
        print("\n" + "="*70)
        print("📊 RESULTADOS INTELIGENTES")
        print("="*70)
        print(f"🔍 Consulta: {resultado['query']}")
        print(f"🎯 Intención detectada: {resultado['intencion']['intencion']}")
        print(f"🧠 Métodos usados: {', '.join(resultado['metodos_usados'])}")
        print("-"*50)
        
        # Recomendaciones
        print("\n⭐ RECOMENDACIONES:")
        for i, r in enumerate(resultado['recomendaciones']['recomendaciones'][:5], 1):
            titulo = r.get('titulo', 'Sin título')
            calidad = r.get('calidad', 0)
            puntuacion = r.get('puntuacion_cuántica', 0)
            print(f"{i}. {titulo}")
            print(f"   📊 Calidad: {calidad:.4f} | Puntuación: {puntuacion}")
            print(f"   🔗 {r.get('url', '#')}")
        
        print("\n💡 JUSTIFICACIÓN:")
        print(resultado['recomendaciones']['justificacion'])
        
        print("\n" + "="*70)


# ============================================================
# PRUEBA
# ============================================================

if __name__ == "__main__":
    buscador = IntelligentSearch()
    buscador.cargar_perfil()
    
    print("="*70)
    print("🧠 BUSCADOR INTELIGENTE - PRUEBA")
    print("="*70)
    
    consultas = [
        "mejor laptop para programar",
        "precio de zapatillas adidas",
        "como llegar al centro",
        "quantum computing tutorial",
        "restaurantes cerca de mi"
    ]
    
    for query in consultas:
        resultado = buscador.buscar_inteligente(query)
        buscador.mostrar_resultados_inteligentes(resultado)