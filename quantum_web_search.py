# quantum_web_search.py - Versión mejorada

import json
import hashlib
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import aiohttp
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import warnings
warnings.filterwarnings('ignore')

class QuantumWebSearch:
    """Buscador web con mejoras de rendimiento y caché."""
    
    def __init__(self, cache_ttl_hours=1, max_workers=5):
        self.simulador = AerSimulator()
        self.historial = []
        self.cache = {}
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.session = None
        
        # Configuración
        self.config = {
            "max_resultados": 50,
            "timeout": 10,
            "user_agent": "QuantumWebSearch/2.0",
            "fuentes_prioritarias": ["wikipedia", "google", "youtube"],
            "dominios_confiables": [
                "wikipedia.org", "google.com", "youtube.com",
                "github.com", "stackoverflow.com", "medium.com",
                "arxiv.org", "nature.com", "science.org"
            ]
        }
    
    async def _get_session(self):
        """Obtiene o crea una sesión aiohttp."""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={"User-Agent": self.config["user_agent"]}
            )
        return self.session
    
    def _get_cache_key(self, query: str) -> str:
        """Genera clave de caché."""
        return hashlib.md5(query.lower().strip().encode()).hexdigest()
    
    def _is_cache_valid(self, entry: Dict) -> bool:
        """Verifica si la entrada de caché es válida."""
        if "timestamp" not in entry:
            return False
        timestamp = datetime.fromisoformat(entry["timestamp"])
        return datetime.now() - timestamp < self.cache_ttl
    
    async def buscar_en_internet_async(self, query: str, max_resultados: int = 50) -> List[Dict]:
        """Búsqueda asíncrona en internet."""
        # Verificar caché
        cache_key = self._get_cache_key(query)
        if cache_key in self.cache and self._is_cache_valid(self.cache[cache_key]):
            print(f"📦 Caché hit: '{query}'")
            return self.cache[cache_key]["resultados"]
        
        resultados = []
        session = await self._get_session()
        
        # Búsqueda en DuckDuckGo (API pública)
        try:
            url = f"https://api.duckduckgo.com/?q={query.replace(' ', '+')}&format=json"
            async with session.get(url, timeout=self.config["timeout"]) as response:
                if response.status == 200:
                    data = await response.json()
                    resultados.extend(self._procesar_duckduckgo(data, query))
        except Exception as e:
            print(f"⚠️ Error en DuckDuckGo: {e}")
        
        # Búsqueda en Wikipedia (si hay pocos resultados)
        if len(resultados) < 5:
            try:
                url = f"https://es.wikipedia.org/w/api.php?action=query&list=search&srsearch={query.replace(' ', '%20')}&format=json&srlimit=10"
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        resultados.extend(self._procesar_wikipedia(data, query))
            except Exception as e:
                print(f"⚠️ Error en Wikipedia: {e}")
        
        # Guardar en caché
        self.cache[cache_key] = {
            "timestamp": datetime.now().isoformat(),
            "resultados": resultados[:max_resultados]
        }
        
        return resultados[:max_resultados]
    
    def _procesar_duckduckgo(self, data: Dict, query: str) -> List[Dict]:
        """Procesa resultados de DuckDuckGo."""
        resultados = []
        
        if data.get("Abstract"):
            resultados.append({
                "titulo": data.get("Heading", query),
                "descripcion": data.get("Abstract", ""),
                "url": data.get("AbstractURL", f"https://www.google.com/search?q={query.replace(' ', '+')}"),
                "fuente": "DuckDuckGo",
                "relevancia": 80
            })
        
        for topic in data.get("RelatedTopics", []):
            if "Text" in topic and "FirstURL" in topic:
                texto = topic["Text"]
                if " - " in texto:
                    titulo, descripcion = texto.split(" - ", 1)
                else:
                    titulo, descripcion = texto[:60], texto
                
                resultados.append({
                    "titulo": titulo,
                    "descripcion": descripcion[:300],
                    "url": topic["FirstURL"],
                    "fuente": "DuckDuckGo",
                    "relevancia": 50
                })
        
        return resultados
    
    def _procesar_wikipedia(self, data: Dict, query: str) -> List[Dict]:
        """Procesa resultados de Wikipedia."""
        resultados = []
        for item in data.get("query", {}).get("search", []):
            resultados.append({
                "titulo": item.get("title", ""),
                "descripcion": item.get("snippet", "").replace("<span class='searchmatch'>", "").replace("</span>", ""),
                "url": f"https://es.wikipedia.org/wiki/{item.get('title', '').replace(' ', '_')}",
                "fuente": "Wikipedia",
                "relevancia": 70
            })
        return resultados
    
    def generar_qrng(self, shots: int = 64) -> List[int]:
        """Genera números aleatorios cuánticos optimizados."""
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
            numeros.extend([valor] * count)
        
        return numeros[:shots]
    
    def filtrar_con_grover(self, resultados: List[Dict], query: str, max_resultados: int = 10) -> List[Dict]:
        """Filtra resultados con Grover optimizado."""
        if not resultados:
            return []
        
        query_lower = query.lower()
        palabras_clave = [p for p in query_lower.split() if len(p) > 2]
        
        # Pesos cuánticos para aleatoriedad controlada
        numeros_qrng = self.generar_qrng(shots=len(resultados) * 2)
        
        for i, resultado in enumerate(resultados):
            titulo = resultado.get("titulo", "").lower()
            descripcion = resultado.get("descripcion", "").lower()
            texto = f"{titulo} {descripcion}"
            
            puntuacion = 0
            
            # Coincidencia exacta
            if query_lower in texto:
                puntuacion += 10
            
            # Palabras clave
            for palabra in palabras_clave:
                if palabra in texto:
                    puntuacion += 2
                if palabra in titulo:
                    puntuacion += 3
            
            # Dominios confiables
            url = resultado.get("url", "")
            for dominio in self.config["dominios_confiables"]:
                if dominio in url:
                    puntuacion += 4
                    break
            
            # Longitud de descripción (calidad)
            puntuacion += min(len(descripcion) / 50, 5)
            
            # Aleatoriedad cuántica (evita sesgos)
            if i < len(numeros_qrng):
                puntuacion += (numeros_qrng[i] % 100) / 200
            
            resultado["relevancia"] = round(puntuacion, 2)
        
        resultados.sort(key=lambda x: x.get("relevancia", 0), reverse=True)
        return resultados[:max_resultados]
    
    def buscar(self, query: str, max_resultados_web: int = 50, max_resultados_final: int = 10) -> Dict:
        """Búsqueda principal."""
        import asyncio
        
        print("\n" + "="*70)
        print("🔍 BUSQUEDA WEB CUANTICA")
        print("="*70)
        print(f"📝 Consulta: '{query}'")
        print("-"*50)
        
        inicio = datetime.now()
        
        try:
            # Búsqueda asíncrona
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            resultados_web = loop.run_until_complete(
                self.buscar_en_internet_async(query, max_resultados_web)
            )
        except Exception as e:
            print(f"⚠️ Error en búsqueda asíncrona: {e}")
            resultados_web = self._resultados_fallback(query)
        
        resultados_filtrados = self.filtrar_con_grover(resultados_web, query, max_resultados_final)
        
        tiempo = (datetime.now() - inicio).total_seconds()
        
        self.historial.append({
            "fecha": datetime.now().isoformat(),
            "query": query,
            "resultados": len(resultados_filtrados),
            "tiempo": tiempo
        })
        
        return {
            "query": query,
            "resultados": resultados_filtrados,
            "total_encontrados": len(resultados_web),
            "mostrados": len(resultados_filtrados),
            "tiempo": round(tiempo, 3)
        }
    
    def _resultados_fallback(self, query: str) -> List[Dict]:
        """Resultados de respaldo."""
        query_encoded = query.replace(" ", "+")
        fuentes = [
            {"titulo": f"Google - {query}", "url": f"https://www.google.com/search?q={query_encoded}", "fuente": "Google"},
            {"titulo": f"Wikipedia - {query}", "url": f"https://es.wikipedia.org/wiki/{query_encoded}", "fuente": "Wikipedia"},
            {"titulo": f"YouTube - {query}", "url": f"https://www.youtube.com/results?search_query={query_encoded}", "fuente": "YouTube"},
            {"titulo": f"GitHub - {query}", "url": f"https://github.com/search?q={query_encoded}", "fuente": "GitHub"},
        ]
        
        return [{
            "titulo": f["titulo"],
            "descripcion": f"Buscar '{query}' en {f['fuente']}",
            "url": f["url"],
            "fuente": f["fuente"],
            "relevancia": 30
        } for f in fuentes]