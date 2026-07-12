"""
MULTI-SEARCH - Búsqueda en múltiples fuentes
RUTA: C:/Users/elpel/OneDrive/Desktop/QuantumWebSearch/multi_search.py
"""

import requests
import json
from urllib.parse import quote_plus
import time

class MultiSearch:
    """Buscador en múltiples fuentes."""
    
    def __init__(self):
        self.fuentes = {
            "wikipedia": self._buscar_wikipedia,
            "google": self._buscar_google,
            "youtube": self._buscar_youtube,
            "news": self._buscar_news,
            "github": self._buscar_github
        }
        self.cache = {}
    
    def buscar_en_todas(self, query, max_por_fuente=5):
        """Busca en todas las fuentes y combina resultados."""
        resultados = []
        query_key = query.lower().strip()
        
        # Verificar caché
        if query_key in self.cache:
            return self.cache[query_key][:max_por_fuente * len(self.fuentes)]
        
        for nombre, funcion in self.fuentes.items():
            try:
                resultados.extend(funcion(query, max_por_fuente))
                time.sleep(0.1)  # Pequeña pausa para no saturar
            except Exception as e:
                print(f"Error en {nombre}: {e}")
        
        # Guardar en caché
        self.cache[query_key] = resultados
        
        return resultados
    
    def _buscar_wikipedia(self, query, max_resultados=5):
        """Busca en Wikipedia."""
        resultados = []
        
        # Intentar búsqueda directa
        url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{quote_plus(query)}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                resultados.append({
                    "titulo": data.get("title", query),
                    "descripcion": data.get("extract", ""),
                    "url": f"https://es.wikipedia.org/wiki/{quote_plus(query)}",
                    "fuente": "Wikipedia"
                })
                return resultados
        except:
            pass
        
        # Búsqueda alternativa
        url = f"https://es.wikipedia.org/w/api.php?action=query&list=search&srsearch={quote_plus(query)}&format=json"
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            
            for item in data.get("query", {}).get("search", [])[:max_resultados]:
                resultados.append({
                    "titulo": item.get("title", ""),
                    "descripcion": item.get("snippet", "").replace("<span class='searchmatch'>", "").replace("</span>", ""),
                    "url": f"https://es.wikipedia.org/wiki/{quote_plus(item.get('title', ''))}",
                    "fuente": "Wikipedia"
                })
            return resultados
        except:
            return []
    
    def _buscar_google(self, query, max_resultados=3):
        """Busca en Google (enlace directo)."""
        return [{
            "titulo": f"🔍 Buscar '{query}' en Google",
            "descripcion": "Haz clic para ver los resultados en Google.",
            "url": f"https://www.google.com/search?q={quote_plus(query)}",
            "fuente": "Google"
        }]
    
    def _buscar_youtube(self, query, max_resultados=3):
        """Busca en YouTube."""
        return [{
            "titulo": f"📺 Buscar '{query}' en YouTube",
            "descripcion": "Encuentra videos relacionados en YouTube.",
            "url": f"https://www.youtube.com/results?search_query={quote_plus(query)}",
            "fuente": "YouTube"
        }]
    
    def _buscar_news(self, query, max_resultados=3):
        """Busca en Google News."""
        return [{
            "titulo": f"📰 Noticias sobre '{query}'",
            "descripcion": "Lee las últimas noticias relacionadas.",
            "url": f"https://news.google.com/search?q={quote_plus(query)}",
            "fuente": "Google News"
        }]
    
    def _buscar_github(self, query, max_resultados=3):
        """Busca en GitHub."""
        return [{
            "titulo": f"💻 Buscar '{query}' en GitHub",
            "descripcion": "Encuentra repositorios relacionados con '{query}'.",
            "url": f"https://github.com/search?q={quote_plus(query)}",
            "fuente": "GitHub"
        }]
    
    def limpiar_cache(self):
        """Limpia el caché de búsquedas."""
        self.cache = {}


# ============================================================
# PRUEBA RÁPIDA
# ============================================================

if __name__ == "__main__":
    multi = MultiSearch()
    
    print("="*60)
    print("🌐 PRUEBA DE MULTI BÚSQUEDA")
    print("="*60)
    
    query = input("\n🔍 Busca algo > ")
    resultados = multi.buscar_en_todas(query)
    
    print(f"\n📊 {len(resultados)} resultados encontrados:")
    for i, r in enumerate(resultados, 1):
        print(f"\n{i}. [{r['fuente']}] {r['titulo']}")
        print(f"   {r['descripcion'][:100]}...")
        print(f"   🔗 {r['url']}")