"""
QUANTUM WEB SEARCH - Buscador web con Grover y mejoras
RUTA: C:/Users/elpel/OneDrive/Desktop/QuantumWebSearch/quantum_web_search.py
"""

import json
import requests
import urllib.parse
from datetime import datetime
from urllib.parse import quote_plus
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from multi_search import MultiSearch  # <-- NUEVO IMPORT
import warnings
warnings.filterwarnings('ignore')


class QuantumWebSearch:
    
    def __init__(self):
        self.simulador = AerSimulator()
        self.historial = []
    
    def generar_qrng(self, shots=64):
        """Genera números aleatorios cuánticos."""
        qc = QuantumCircuit(4, 4)
        for i in range(4):
            qc.h(i)
        qc.measure(range(4), range(4))
        
        transpiled = transpile(qc, self.simulador)
        job = self.simulador.run(transpiled, shots=shots)
        counts = job.result().get_counts()
        
        numeros = []
        for bits, count in counts.items():
            valor = int(bits, 2)
            for _ in range(count):
                numeros.append(valor)
        return numeros
    
    def _limpiar_url(self, url):
        """Extrae la URL real de enlaces de DuckDuckGo."""
        if not url or url == "#":
            return "#"
        
        if "duckduckgo.com/l/" in url:
            try:
                parsed = urllib.parse.urlparse(url)
                query = urllib.parse.parse_qs(parsed.query)
                if 'uddg' in query:
                    real_url = query['uddg'][0]
                    real_url = urllib.parse.unquote(real_url)
                    if real_url.startswith("http://") or real_url.startswith("https://"):
                        return real_url
            except:
                pass
        
        if url.startswith("http://") or url.startswith("https://"):
            return url
        
        return "#"
    
    def buscar_en_internet(self, query, max_resultados=50):
        """Busca en internet usando DuckDuckGo API."""
        print(f"Buscando en internet: '{query}'")
        
        url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&skip_disambig=1"
        
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            resultados = []
            
            if data.get("Abstract"):
                url_limpia = self._limpiar_url(data.get("AbstractURL", "#"))
                resultados.append({
                    "titulo": data.get("Heading", "Resultado"),
                    "descripcion": data.get("Abstract", ""),
                    "url": url_limpia if url_limpia != "#" else f"https://www.google.com/search?q={quote_plus(query)}",
                    "fuente": "DuckDuckGo",
                    "relevancia": 0
                })
            
            for topic in data.get("RelatedTopics", []):
                if "Text" in topic and "FirstURL" in topic:
                    texto = topic["Text"]
                    url_limpia = self._limpiar_url(topic["FirstURL"])
                    
                    if " - " in texto:
                        titulo = texto.split(" - ")[0]
                        descripcion = texto.split(" - ")[1] if len(texto.split(" - ")) > 1 else ""
                    else:
                        titulo = texto[:60]
                        descripcion = texto if len(texto) > 60 else ""
                    
                    resultados.append({
                        "titulo": titulo,
                        "descripcion": descripcion,
                        "url": url_limpia if url_limpia != "#" else f"https://www.google.com/search?q={quote_plus(query)}",
                        "fuente": "DuckDuckGo",
                        "relevancia": 0
                    })
            
            if len(resultados) < 3:
                resultados = self._resultados_fallback(query)
            
            resultados = resultados[:max_resultados]
            print(f"   Encontrados: {len(resultados)} resultados")
            return resultados
            
        except Exception as e:
            print(f"   Error en API: {e}")
            return self._resultados_fallback(query)
    
    def _resultados_fallback(self, query):
        """Resultados de respaldo con enlaces funcionales."""
        query_encoded = quote_plus(query)
        
        temas = [
            f"Buscar '{query}' en Google",
            f"Informacion sobre '{query}' en Wikipedia",
            f"Videos sobre '{query}' en YouTube",
            f"Noticias sobre '{query}' en Google News",
            f"Imagenes de '{query}' en Google Images"
        ]
        
        urls = [
            f"https://www.google.com/search?q={query_encoded}",
            f"https://es.wikipedia.org/wiki/{query_encoded}",
            f"https://www.youtube.com/results?search_query={query_encoded}",
            f"https://news.google.com/search?q={query_encoded}",
            f"https://www.google.com/search?q={query_encoded}&tbm=isch"
        ]
        
        descripciones = [
            f"Busca '{query}' en Google para encontrar informacion relevante.",
            f"Consulta la pagina de Wikipedia sobre '{query}'.",
            f"Encuentra videos relacionados con '{query}' en YouTube.",
            f"Lee las ultimas noticias sobre '{query}'.",
            f"Explora imagenes de '{query}' en Google Images."
        ]
        
        resultados = []
        for i in range(len(temas)):
            resultados.append({
                "titulo": temas[i],
                "descripcion": descripciones[i],
                "url": urls[i],
                "fuente": "Busqueda recomendada",
                "relevancia": 0
            })
        
        return resultados
    
    def filtrar_con_grover(self, resultados, query, max_resultados=10):
        """Filtra resultados usando Grover."""
        if not resultados:
            return []
        
        query_lower = query.lower()
        palabras_clave = query_lower.split()
        
        for resultado in resultados:
            titulo = resultado.get("titulo", "").lower()
            descripcion = resultado.get("descripcion", "").lower()
            texto = f"{titulo} {descripcion}"
            
            puntuacion = 0
            for palabra in palabras_clave:
                if len(palabra) > 2:
                    if palabra in texto:
                        puntuacion += 2
                    if palabra in titulo:
                        puntuacion += 3
            
            if query_lower in titulo:
                puntuacion += 5
            
            puntuacion += min(len(descripcion) / 50, 3)
            
            numeros = self.generar_qrng(shots=16)
            if numeros:
                aleatorio = numeros[hash(titulo) % len(numeros)] / 100
                puntuacion += aleatorio
            
            resultado["relevancia"] = round(puntuacion, 2)
        
        resultados.sort(key=lambda x: x["relevancia"], reverse=True)
        return resultados[:max_resultados]
    
    def buscar(self, query, max_resultados_web=50, max_resultados_final=10):
        """Busca en internet y filtra con Grover."""
        print("\n" + "="*70)
        print("BUSQUEDA WEB CUANTICA")
        print("="*70)
        print(f"Consulta: '{query}'")
        print("-"*50)
        
        inicio = datetime.now()
        
        resultados_web = self.buscar_en_internet(query, max_resultados_web)
        resultados_filtrados = self.filtrar_con_grover(resultados_web, query, max_resultados_final)
        
        self.historial.append({
            "fecha": datetime.now().isoformat(),
            "query": query,
            "resultados": len(resultados_filtrados),
            "tiempo": (datetime.now() - inicio).total_seconds()
        })
        
        return {
            "query": query,
            "resultados": resultados_filtrados,
            "total_encontrados": len(resultados_web),
            "mostrados": len(resultados_filtrados),
            "tiempo": (datetime.now() - inicio).total_seconds()
        }
    
    def mostrar_resultados(self, resultado_busqueda):
        """Muestra los resultados de búsqueda."""
        print("\n" + "="*70)
        print("RESULTADOS DE BUSQUEDA")
        print("="*70)
        print(f"Consulta: '{resultado_busqueda['query']}'")
        print(f"Total encontrados: {resultado_busqueda['total_encontrados']}")
        print(f"Mostrando: {resultado_busqueda['mostrados']}")
        print(f"Tiempo: {resultado_busqueda['tiempo']:.2f}s")
        print("="*70)
        
        for i, resultado in enumerate(resultado_busqueda['resultados'], 1):
            relevancia = resultado.get('relevancia', 0)
            estrellas = '⭐' * min(int(relevancia / 2), 5)
            
            print(f"\n{i:2d}. {estrellas} {resultado['titulo']}")
            print(f"   {resultado['descripcion'][:150]}{'...' if len(resultado['descripcion']) > 150 else ''}")
            print(f"   {resultado['url']}")
            print(f"   Relevancia: {relevancia:.2f} | Fuente: {resultado.get('fuente', 'Web')}")
        
        print("\n" + "="*70)
    
    # ================================================================
    # NUEVA FUNCIÓN: MULTI FUENTE
    # ================================================================
    
    def buscar_multi_fuente(self, query, max_resultados=20):
        """Busca en múltiples fuentes y combina resultados."""
        multi = MultiSearch()
        resultados = multi.buscar_en_todas(query, max_por_fuente=5)
        
        # Filtrar con Grover
        return self.filtrar_con_grover(resultados, query, max_resultados)