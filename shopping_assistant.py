"""
SHOPPING ASSISTANT - Asistente de compras con algoritmos cuánticos
RUTA: C:/Users/elpel/OneDrive/Desktop/QuantumWebSearch/shopping_assistant.py
"""

import json
import re
import requests
from datetime import datetime
from urllib.parse import quote_plus
from quantum_bridge import QuantumBridge
import warnings
warnings.filterwarnings('ignore')


class ShoppingAssistant:
    """
    Asistente de compras que recomienda productos con:
    - Precio
    - Calidad
    - Confiabilidad de tienda
    - Cercanía
    - Enlaces directos
    """
    
    def __init__(self):
        self.bridge = QuantumBridge()
        self.historial_compras = []
        self.preferencias_usuario = {}
        
        # Base de datos de tiendas confiables
        self.tiendas_confiables = {
            "mercadolibre": {"confianza": 95, "url": "https://www.mercadolibre.com.ar"},
            "amazon": {"confianza": 98, "url": "https://www.amazon.com"},
            "ebay": {"confianza": 90, "url": "https://www.ebay.com"},
            "fravega": {"confianza": 88, "url": "https://www.fravega.com"},
            "musimundo": {"confianza": 87, "url": "https://www.musimundo.com"},
            "garbarino": {"confianza": 85, "url": "https://www.garbarino.com"},
            "tiendamia": {"confianza": 82, "url": "https://www.tiendamia.com"},
            "linio": {"confianza": 80, "url": "https://www.linio.com"},
            "walmart": {"confianza": 92, "url": "https://www.walmart.com"},
            "bestbuy": {"confianza": 91, "url": "https://www.bestbuy.com"}
        }
        
        # Palabras clave para detectar intención de compra
        self.palabras_compra = [
            "comprar", "precio", "oferta", "descuento", "costo", "cuanto",
            "donde", "tienda", "mercadolibre", "amazon", "local"
        ]
    
    # ================================================================
    # 1. ANÁLISIS DE INTENCIÓN DE COMPRA
    # ================================================================
    
    def analizar_intencion_compra(self, query):
        """
        Analiza si la búsqueda es una intención de compra y extrae datos.
        """
        query_lower = query.lower()
        
        # Detectar si es una compra
        es_compra = any(p in query_lower for p in self.palabras_compra)
        
        # Extraer producto
        producto = self._extraer_producto(query)
        
        # Extraer precio si menciona
        precio = self._extraer_precio(query)
        
        # Extraer ubicación si menciona
        ubicacion = self._extraer_ubicacion(query)
        
        return {
            "es_compra": es_compra,
            "producto": producto,
            "precio_estimado": precio,
            "ubicacion": ubicacion,
            "necesita_datos": not producto or not precio
        }
    
    def _extraer_producto(self, query):
        """
        Extrae el nombre del producto de la consulta.
        """
        # Eliminar palabras de compra
        palabras_compra = ["comprar", "precio", "oferta", "descuento", "costo", "cuanto", "donde", "tienda"]
        producto = query
        for p in palabras_compra:
            producto = producto.replace(p, "")
        
        # Limpiar y devolver
        producto = producto.strip()
        if not producto:
            return query
        
        return producto
    
    def _extraer_precio(self, query):
        """
        Extrae un precio mencionado en la consulta.
        """
        import re
        # Buscar números con formato de precio
        patrones = [
            r'\$(\d+[.,]?\d*)',
            r'(\d+[.,]?\d*)\s*(?:USD|dólares|pesos|ars)',
            r'(\d+[.,]?\d*)'
        ]
        
        for patron in patrones:
            match = re.search(patron, query)
            if match:
                try:
                    return float(match.group(1).replace(',', '.'))
                except:
                    return None
        return None
    
    def _extraer_ubicacion(self, query):
        """
        Extrae una ubicación mencionada en la consulta.
        """
        palabras_ubicacion = ["en", "cerca", "cercano", "local", "tienda"]
        for p in palabras_ubicacion:
            if p in query.lower():
                partes = query.lower().split(p)
                if len(partes) > 1:
                    return partes[1].strip()
        return None
    
    # ================================================================
    # 2. BÚSQUEDA DE PRODUCTOS
    # ================================================================
    
    def buscar_producto(self, producto):
        """
        Busca el producto en internet y simula resultados de tiendas.
        """
        print(f"🔍 Buscando: {producto}")
        
        # Simular resultados de búsqueda
        resultados = self._simular_resultados(producto)
        
        # Usar Grover para filtrar los mejores
        return self._filtrar_mejores(resultados, producto)
    
    def _simular_resultados(self, producto):
        """
        Simula resultados de búsqueda con precios y tiendas.
        """
        # Lista de productos simulados con precios y tiendas
        productos_simulados = {
            "termica bipolar": [
                {"nombre": "Térmica Bipolar 25A", "precio": 12500, "tienda": "MercadoLibre", "calificacion": 4.8},
                {"nombre": "Térmica Bipolar 25A", "precio": 14900, "tienda": "Fravega", "calificacion": 4.5},
                {"nombre": "Térmica Bipolar 25A", "precio": 16900, "tienda": "Musimundo", "calificacion": 4.2},
                {"nombre": "Térmica Bipolar 25A", "precio": 13500, "tienda": "Garbarino", "calificacion": 4.6},
                {"nombre": "Térmica Bipolar 25A Kit", "precio": 18900, "tienda": "Amazon", "calificacion": 4.9},
            ],
            "laptop": [
                {"nombre": "Laptop Dell XPS 13", "precio": 1200000, "tienda": "MercadoLibre", "calificacion": 4.9},
                {"nombre": "Laptop MacBook Pro", "precio": 1500000, "tienda": "Amazon", "calificacion": 4.8},
                {"nombre": "Laptop Lenovo ThinkPad", "precio": 1100000, "tienda": "Fravega", "calificacion": 4.7},
                {"nombre": "Laptop HP Spectre", "precio": 1300000, "tienda": "Garbarino", "calificacion": 4.6},
            ],
            "zapatillas": [
                {"nombre": "Zapatillas Adidas Ultraboost", "precio": 85000, "tienda": "MercadoLibre", "calificacion": 4.7},
                {"nombre": "Zapatillas Nike Air Max", "precio": 92000, "tienda": "Amazon", "calificacion": 4.8},
                {"nombre": "Zapatillas Puma RS-X", "precio": 78000, "tienda": "Fravega", "calificacion": 4.5},
            ],
            "default": [
                {"nombre": f"{producto} - Opción 1", "precio": 10000, "tienda": "MercadoLibre", "calificacion": 4.5},
                {"nombre": f"{producto} - Opción 2", "precio": 12000, "tienda": "Amazon", "calificacion": 4.3},
                {"nombre": f"{producto} - Opción 3", "precio": 9000, "tienda": "Fravega", "calificacion": 4.0},
            ]
        }
        
        # Buscar coincidencia
        producto_lower = producto.lower()
        for clave, resultados in productos_simulados.items():
            if clave in producto_lower:
                return resultados
        
        return productos_simulados["default"]
    
    def _filtrar_mejores(self, resultados, producto):
        """
        Filtra y ordena resultados usando Grover (simulado).
        """
        if not resultados:
            return []
        
        # Calcular puntuación para cada resultado
        for r in resultados:
            # Puntuación de precio (más barato = mejor)
            precio_score = 100 - (r["precio"] / 100000) * 10
            
            # Puntuación de calificación
            calificacion_score = r["calificacion"] / 5 * 100
            
            # Confianza de la tienda
            tienda_confianza = self.tiendas_confiables.get(
                r["tienda"].lower(), {"confianza": 70}
            )["confianza"]
            
            # Puntuación total (Grover adaptativo)
            r["puntuacion"] = round(
                precio_score * 0.4 + calificacion_score * 0.3 + tienda_confianza * 0.3,
                2
            )
        
        # Ordenar por puntuación
        resultados.sort(key=lambda x: x["puntuacion"], reverse=True)
        
        return resultados
    
    # ================================================================
    # 3. RECOMENDACIONES PERSONALIZADAS
    # ================================================================
    
    def recomendar(self, query):
        """
        Genera recomendaciones completas de compra.
        """
        print("\n" + "="*70)
        print("🛒 ASISTENTE DE COMPRAS CUÁNTICO")
        print("="*70)
        print(f"📝 Consulta: '{query}'")
        print("-"*50)
        
        # 1. Analizar intención
        intencion = self.analizar_intencion_compra(query)
        
        # 2. Si es compra, buscar producto
        if intencion["es_compra"]:
            producto = intencion["producto"]
            resultados = self.buscar_producto(producto)
        else:
            # Si no es compra, usar búsqueda normal
            return {"error": "No detecté intención de compra. Prueba: 'comprar termica bipolar 25 amp'"}
        
        # 3. Generar recomendaciones
        recomendaciones = self._generar_recomendaciones(resultados, intencion)
        
        # 4. Guardar historial
        self.historial_compras.append({
            "fecha": datetime.now().isoformat(),
            "query": query,
            "producto": producto,
            "recomendaciones": recomendaciones
        })
        
        return {
            "producto": producto,
            "intencion": intencion,
            "resultados": resultados,
            "recomendaciones": recomendaciones,
            "necesita_datos": intencion["necesita_datos"]
        }
    
    def _generar_recomendaciones(self, resultados, intencion):
        """
        Genera recomendaciones con todos los detalles.
        """
        if not resultados:
            return {"mensaje": "No se encontraron productos"}
        
        mejor = resultados[0]
        
        # Calcular estadísticas
        precios = [r["precio"] for r in resultados]
        precio_min = min(precios)
        precio_max = max(precios)
        precio_promedio = sum(precios) / len(precios)
        
        return {
            "mejor_opcion": mejor,
            "precio_minimo": precio_min,
            "precio_maximo": precio_max,
            "precio_promedio": precio_promedio,
            "total_opciones": len(resultados),
            "tiendas_confiables": [r["tienda"] for r in resultados if r["puntuacion"] > 70],
            "consejos": self._generar_consejos(mejor, intencion)
        }
    
    def _generar_consejos(self, mejor, intencion):
        """
        Genera consejos basados en el producto y la intención.
        """
        consejos = []
        
        if mejor["calificacion"] >= 4.5:
            consejos.append("⭐ Excelente calificación - Producto muy recomendado")
        elif mejor["calificacion"] >= 4.0:
            consejos.append("👍 Buena calificación - Opción sólida")
        else:
            consejos.append("ℹ️ Verifica otras opciones")
        
        if intencion["precio_estimado"]:
            precio_estimado = intencion["precio_estimado"]
            if mejor["precio"] <= precio_estimado * 1.1:
                consejos.append(f"💰 Precio dentro de tu presupuesto estimado (${precio_estimado:,.0f})")
            else:
                consejos.append(f"⚠️ El precio está por encima de tu presupuesto (${precio_estimado:,.0f})")
        
        consejos.append(f"🏷️ Tienda confiable: {mejor['tienda']}")
        consejos.append(f"🔗 Enlace directo: {self.tiendas_confiables.get(mejor['tienda'].lower(), {}).get('url', '#')}")
        
        return consejos
    
    # ================================================================
    # 4. MOSTRAR RESULTADOS
    # ================================================================
    
    def mostrar_recomendaciones(self, resultado):
        """
        Muestra las recomendaciones de forma bonita.
        """
        if "error" in resultado:
            print(f"\n❌ {resultado['error']}")
            return
        
        producto = resultado["producto"]
        recomendaciones = resultado["recomendaciones"]
        resultados = resultado["resultados"]
        intencion = resultado["intencion"]
        
        print("\n" + "="*70)
        print(f"🛒 RECOMENDACIONES PARA: {producto.upper()}")
        print("="*70)
        
        # Mejor opción
        mejor = recomendaciones["mejor_opcion"]
        print(f"\n⭐ MEJOR OPCIÓN:")
        print(f"   📦 Producto: {mejor['nombre']}")
        print(f"   💰 Precio: ${mejor['precio']:,.0f}")
        print(f"   ⭐ Calificación: {mejor['calificacion']}/5")
        print(f"   🏷️ Tienda: {mejor['tienda']}")
        print(f"   📊 Puntuación: {mejor['puntuacion']:.2f}")
        
        # Enlace directo
        tienda_info = self.tiendas_confiables.get(mejor['tienda'].lower(), {})
        if tienda_info:
            print(f"   🔗 Link: {tienda_info.get('url', '#')}")
        
        # Estadísticas de precios
        print(f"\n📊 COMPARATIVA DE PRECIOS:")
        print(f"   💰 Mínimo: ${recomendaciones['precio_minimo']:,.0f}")
        print(f"   💰 Máximo: ${recomendaciones['precio_maximo']:,.0f}")
        print(f"   💰 Promedio: ${recomendaciones['precio_promedio']:,.0f}")
        print(f"   📦 Total opciones: {recomendaciones['total_opciones']}")
        
        # Tiendas confiables
        if recomendaciones['tiendas_confiables']:
            print(f"\n🏷️ TIENDAS CONFIABLES:")
            for tienda in set(recomendaciones['tiendas_confiables']):
                confianza = self.tiendas_confiables.get(tienda.lower(), {}).get('confianza', 70)
                print(f"   ✅ {tienda} (confianza: {confianza}%)")
        
        # Consejos
        print(f"\n💡 CONSEJOS:")
        for consejo in recomendaciones['consejos']:
            print(f"   • {consejo}")
        
        # Datos faltantes
        if resultado["necesita_datos"]:
            print(f"\n⚠️ DATOS FALTANTES:")
            if not intencion["producto"]:
                print("   • No especificaste el producto claramente")
            if not intencion["precio_estimado"]:
                print("   • No especificaste un presupuesto (ej: 'comprar X por menos de $10000')")
            if not intencion["ubicacion"]:
                print("   • No especificaste tu ubicación para tiendas cercanas")
            print("\n   💡 Sugerencia: 'comprar termica bipolar 25 amp por menos de $15000 en Buenos Aires'")
        
        print("\n" + "="*70)


# ============================================================
# PRUEBA
# ============================================================

if __name__ == "__main__":
    asistente = ShoppingAssistant()
    
    print("="*70)
    print("🛒 ASISTENTE DE COMPRAS CUÁNTICO - PRUEBA")
    print("="*70)
    
    consultas = [
        "comprar termica bipolar 25 amp",
        "termica bipolar 25 amp",
        "comprar termica bipolar 25 amp por menos de $15000 en Buenos Aires"
    ]
    
    for query in consultas:
        resultado = asistente.recomendar(query)
        asistente.mostrar_recomendaciones(resultado)