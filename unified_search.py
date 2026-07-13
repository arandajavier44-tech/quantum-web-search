"""
BUSCADOR UNIFICADO - Detecta automáticamente el algoritmo adecuado
RUTA: C:/Users/elpel/OneDrive/Desktop/QuantumWebSearch/unified_search.py
"""

import re
from datetime import datetime
from quantum_bridge import QuantumBridge
import warnings
warnings.filterwarnings('ignore')


class UnifiedSearch:
    """
    Buscador que detecta automáticamente qué algoritmo usar.
    """
    
    def __init__(self):
        self.bridge = QuantumBridge()
        self.historial = []
        
        # Palabras clave por categoría
        self.palabras = {
            "compra": [
                "comprar", "precio", "oferta", "descuento", "costo", "cuanto",
                "donde", "tienda", "mercadolibre", "amazon", "local",
                "termica", "bipolar", "amp", "laptop", "zapatillas",
                "producto", "barato", "caro", "vale", "cuesta",
                "quiero", "necesito", "busco", "conseguir", "adquirir",
                "para mi", "casa", "hogar", "compra"
            ],
            "shor": [
                "factorizar", "factores", "primo", "divisor",
                "dividir", "factor", "descomponer"
            ],
            "inteligente": [
                "qué es", "como", "cuando", "donde", "quien", "por qué",
                "significa", "definición", "explica", "ayuda",
                "sugiere", "recomienda", "mejor", "top", "ranking"
            ],
            "grover": [
                "buscar", "encuentra", "búsqueda", "información",
                "noticias", "artículo", "documento", "pdf", "descargar"
            ],
            "cerebro": [
                "todos los algoritmos", "todo", "completo", "integral"
            ],
            "multi": [
                "varias fuentes", "multi", "google", "wikipedia", "youtube"
            ],
            "qaoa": [
                "optimizar", "mochila", "asignar", "rutas", "distribuir",
                "recursos", "logística", "mejor combinación"
            ]
        }
        
        # Patrones para detectar números (Shor)
        self.patron_numero = re.compile(r'^\s*\d+\s*$')
    
    # ================================================================
    # 1. DETECTOR DE INTENCIÓN
    # ================================================================
    
    def detectar_intencion(self, query):
        """
        Detecta la intención del usuario y devuelve el algoritmo adecuado.
        """
        query_lower = query.lower()
        query_limpia = query_lower.strip()
        
        # 1. Si es un número → Shor
        if self.patron_numero.match(query_limpia) and int(query_limpia) > 1:
            return "shor", "Número detectado. Factorizando..."
        
        # 2. Si contiene palabras de compra → Compras
        if any(p in query_lower for p in self.palabras["compra"]):
            return "compras", "🛒 Intención de compra detectada. Buscando opciones..."
        
        # 3. Si contiene palabras de optimización → QAOA
        if any(p in query_lower for p in self.palabras["qaoa"]):
            return "qaoa", "📊 Optimización detectada. Buscando la mejor solución..."
        
        # 4. Si contiene palabras de factorización → Shor
        if any(p in query_lower for p in self.palabras["shor"]):
            return "shor", "🔬 Factorización detectada. Calculando factores primos..."
        
        # 5. Si contiene palabras de búsqueda general → Grover
        if any(p in query_lower for p in self.palabras["grover"]):
            return "grover", "🔍 Búsqueda general detectada. Buscando información..."
        
        # 6. Si contiene palabras de pregunta → Inteligente
        if any(p in query_lower for p in self.palabras["inteligente"]):
            return "inteligente", "🧠 Pregunta detectada. Analizando con inteligencia..."
        
        # 7. Si contiene palabras de cerebro → Cerebro
        if any(p in query_lower for p in self.palabras["cerebro"]):
            return "cerebro", "🧠 Modo cerebro activado. Usando todos los algoritmos..."
        
        # 8. Si contiene palabras de multi-fuente → Multi
        if any(p in query_lower for p in self.palabras["multi"]):
            return "multi", "🌐 Búsqueda en múltiples fuentes..."
        
        # 9. Por defecto → Inteligente (el más completo)
        return "inteligente", "🧠 Analizando tu consulta con inteligencia cuántica..."
    
    # ================================================================
    # 2. EJECUTOR DE ALGORITMOS
    # ================================================================
    
    def buscar(self, query):
        """
        Ejecuta la búsqueda completa con detección automática.
        """
        print("\n" + "="*70)
        print("🚀 BUSCADOR UNIFICADO")
        print("="*70)
        print(f"📝 Consulta: '{query}'")
        print("-"*50)
        
        # 1. Detectar intención
        algoritmo, explicacion = self.detectar_intencion(query)
        print(f"🎯 Algoritmo: {algoritmo.upper()}")
        print(f"📖 {explicacion}")
        print("-"*50)
        
        # 2. Ejecutar algoritmo
        resultado = self._ejecutar_algoritmo(algoritmo, query)
        
        # 3. Guardar historial
        self.historial.append({
            "fecha": datetime.now().isoformat(),
            "query": query,
            "algoritmo": algoritmo,
            "resultado": resultado
        })
        
        return {
            "query": query,
            "algoritmo": algoritmo,
            "explicacion": explicacion,
            "resultado": resultado,
            "timestamp": datetime.now().isoformat()
        }
    
    def _ejecutar_algoritmo(self, algoritmo, query):
        """
        Ejecuta el algoritmo correspondiente.
        """
        if algoritmo == "compras":
            return self._ejecutar_compras(query)
        elif algoritmo == "shor":
            return self._ejecutar_shor(query)
        elif algoritmo == "inteligente":
            return self._ejecutar_inteligente(query)
        elif algoritmo == "grover":
            return self._ejecutar_grover(query)
        elif algoritmo == "cerebro":
            return self._ejecutar_cerebro(query)
        elif algoritmo == "multi":
            return self._ejecutar_multi(query)
        elif algoritmo == "qaoa":
            return self._ejecutar_qaoa(query)
        else:
            return {"error": "Algoritmo no reconocido"}
    
    # ================================================================
    # 3. ALGORITMOS INDIVIDUALES
    # ================================================================
    
    def _ejecutar_compras(self, query):
        """
        Ejecuta el asistente de compras.
        """
        try:
            from shopping_assistant import ShoppingAssistant
            asistente = ShoppingAssistant()
            resultado = asistente.recomendar(query)
            return resultado
        except Exception as e:
            return {"error": f"Error en compras: {e}"}
    
    def _ejecutar_shor(self, query):
        """
        Ejecuta Shor para factorización.
        """
        try:
            numero = int(query.strip())
            from shor_algorithm import ShorAlgorithm
            shor = ShorAlgorithm()
            factores = shor.factorizar(numero)
            return {
                "numero": numero,
                "factores": factores,
                "factorizacion": f"{numero} = {factores[0]} × {factores[1]}"
            }
        except Exception as e:
            return {"error": f"Error en Shor: {e}"}
    
    def _ejecutar_inteligente(self, query):
        """
        Ejecuta el buscador inteligente.
        """
        try:
            from intelligent_search import IntelligentSearch
            buscador = IntelligentSearch()
            resultado = buscador.buscar_inteligente(query)
            return resultado
        except Exception as e:
            return {"error": f"Error en inteligente: {e}"}
    
    def _ejecutar_grover(self, query):
        """
        Ejecuta Grover para búsqueda general.
        """
        try:
            from quantum_web_search import QuantumWebSearch
            buscador = QuantumWebSearch()
            resultado = buscador.buscar(query, max_resultados_final=10)
            return resultado
        except Exception as e:
            return {"error": f"Error en Grover: {e}"}
    
    def _ejecutar_cerebro(self, query):
        """
        Ejecuta el cerebro cuántico.
        """
        try:
            from cerebro_cuantico import CerebroCuantico
            cerebro = CerebroCuantico()
            resultado = cerebro.procesar_consulta(query)
            return resultado
        except Exception as e:
            return {"error": f"Error en Cerebro: {e}"}
    
    def _ejecutar_multi(self, query):
        """
        Ejecuta búsqueda multi-fuente.
        """
        try:
            from quantum_web_search import QuantumWebSearch
            buscador = QuantumWebSearch()
            resultado = buscador.buscar_multi_fuente(query, max_resultados=20)
            return {
                "resultados": resultado,
                "fuentes": ["Google", "Wikipedia", "YouTube", "News", "GitHub"],
                "total": len(resultado)
            }
        except Exception as e:
            return {"error": f"Error en Multi Fuente: {e}"}
    
    def _ejecutar_qaoa(self, query):
        """
        Ejecuta QAOA para optimización.
        """
        try:
            from qaoa_algorithm import QAOAAlgorithm
            qaoa = QAOAAlgorithm()
            
            # Detectar si es mochila
            if "mochila" in query.lower():
                partes = query.split()
                capacidad = 8
                for p in partes:
                    if p.isdigit():
                        capacidad = int(p)
                        break
                resultado = qaoa.problema_mochila(
                    pesos=[2, 3, 4, 5],
                    valores=[3, 4, 5, 6],
                    capacidad=capacidad
                )
            else:
                resultado = qaoa.optimizar(n_qubits=4, p=1, iteraciones=20)
            
            return resultado
        except Exception as e:
            return {"error": f"Error en QAOA: {e}"}
    
    # ================================================================
    # 4. MOSTRAR RESULTADOS
    # ================================================================
    
    def mostrar_resultado(self, resultado_busqueda):
        """
        Muestra el resultado de forma bonita.
        """
        print("\n" + "="*70)
        print("📊 RESULTADO DEL BUSCADOR UNIFICADO")
        print("="*70)
        print(f"📝 Consulta: {resultado_busqueda['query']}")
        print(f"🎯 Algoritmo usado: {resultado_busqueda['algoritmo'].upper()}")
        print(f"📖 {resultado_busqueda['explicacion']}")
        print("-"*50)
        
        resultado = resultado_busqueda["resultado"]
        
        if "error" in resultado:
            print(f"❌ {resultado['error']}")
            return
        
        # Mostrar según algoritmo
        algoritmo = resultado_busqueda["algoritmo"]
        
        if algoritmo == "compras":
            self._mostrar_compras(resultado)
        elif algoritmo == "shor":
            self._mostrar_shor(resultado)
        elif algoritmo == "inteligente":
            self._mostrar_inteligente(resultado)
        elif algoritmo == "grover":
            self._mostrar_grover(resultado)
        elif algoritmo == "cerebro":
            self._mostrar_cerebro(resultado)
        elif algoritmo == "multi":
            self._mostrar_multi(resultado)
        elif algoritmo == "qaoa":
            self._mostrar_qaoa(resultado)
        else:
            print(f"📊 {resultado}")
        
        print("\n" + "="*70)
    
    def _mostrar_compras(self, resultado):
        """Muestra resultados de compras."""
        if resultado.get("recomendaciones") and resultado["recomendaciones"].get("mejor_opcion"):
            mejor = resultado["recomendaciones"]["mejor_opcion"]
            print(f"⭐ MEJOR OPCIÓN:")
            print(f"   📦 Producto: {mejor['nombre']}")
            print(f"   💰 Precio: ${mejor['precio']:,.0f}")
            print(f"   ⭐ Calificación: {mejor['calificacion']}/5")
            print(f"   🏷️ Tienda: {mejor['tienda']}")
        
        if resultado.get("recomendaciones"):
            rec = resultado["recomendaciones"]
            print(f"\n📊 PRECIOS:")
            print(f"   💰 Mínimo: ${rec.get('precio_minimo', 0):,.0f}")
            print(f"   💰 Máximo: ${rec.get('precio_maximo', 0):,.0f}")
            print(f"   💰 Promedio: ${rec.get('precio_promedio', 0):,.0f}")
    
    def _mostrar_shor(self, resultado):
        """Muestra resultados de Shor."""
        print(f"🔢 Número: {resultado.get('numero', 'N/A')}")
        print(f"📐 Factorización: {resultado.get('factorizacion', 'N/A')}")
    
    def _mostrar_inteligente(self, resultado):
        """Muestra resultados inteligentes."""
        if resultado.get("intencion"):
            print(f"🎯 Intención: {resultado['intencion']['intencion']}")
            print(f"📊 Prioridad: {resultado['intencion']['prioridad']:.0%}")
    
    def _mostrar_grover(self, resultado):
        """Muestra resultados de Grover."""
        print(f"🔍 Encontrados: {resultado.get('mostrados', 0)} resultados")
        for i, r in enumerate(resultado.get("resultados", [])[:5], 1):
            print(f"   {i}. {r.get('titulo', 'Sin título')}")
    
    def _mostrar_cerebro(self, resultado):
        """Muestra resultados del cerebro."""
        print(f"🎲 ID: {resultado.get('id', 'N/A')}")
        if resultado.get("seguridad"):
            print(f"🔒 Encriptada: {resultado['seguridad']['encriptada']}")
    
    def _mostrar_multi(self, resultado):
        """Muestra resultados multi-fuente."""
        print(f"📰 Fuentes: {', '.join(resultado.get('fuentes', []))}")
        print(f"📊 Total: {resultado.get('total', 0)} resultados")
    
    def _mostrar_qaoa(self, resultado):
        """Muestra resultados de QAOA."""
        if resultado.get("mejor_estado"):
            print(f"📊 Mejor estado: {resultado['mejor_estado']}")
        if resultado.get("valor_total"):
            print(f"💰 Valor total: {resultado['valor_total']}")
        if resultado.get("explicacion"):
            print(f"💡 {resultado['explicacion']}")


# ============================================================
# PRUEBA
# ============================================================

if __name__ == "__main__":
    buscador = UnifiedSearch()
    
    print("="*70)
    print("🚀 BUSCADOR UNIFICADO - PRUEBA")
    print("="*70)
    
    consultas = [
        "15",
        "comprar termica bipolar 25 amp",
        "qué es la computación cuántica",
        "mochila 8",
        "noticias de tecnología",
        "optimizar mis recursos"
    ]
    
    for query in consultas:
        resultado = buscador.buscar(query)
        buscador.mostrar_resultado(resultado)