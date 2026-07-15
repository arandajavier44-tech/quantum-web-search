# intelligent_search.py - Versión mejorada con más funcionalidades

import json
import numpy as np
from datetime import datetime
from collections import defaultdict, Counter
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import re

@dataclass
class QueryAnalysis:
    """Análisis de una consulta."""
    query: str
    intencion: str
    palabras_clave: List[str]
    entidades: List[str]
    prioridad: float
    timestamp: datetime

class IntelligentSearch:
    """Buscador inteligente mejorado."""
    
    def __init__(self):
        self.bridge = QuantumBridge()
        self.historial_usuario = []
        self.perfil_usuario = self._init_perfil()
        self.recomendaciones_cache = {}
        self.modelo_confianza = {}
        
        # Configuración
        self.config = {
            "max_recomendaciones": 10,
            "umbral_confianza": 0.6,
            "peso_reciente": 0.3,
            "peso_frecuencia": 0.4,
            "peso_relevancia": 0.3
        }
        
        # Diccionarios de intención
        self.intenciones = {
            "compra": ["comprar", "precio", "oferta", "descuento", "costo", "cuanto", "cuesta"],
            "informacion": ["qué es", "como", "cuando", "donde", "quien", "por qué", "significa", "definición"],
            "recomendacion": ["mejor", "top", "ranking", "recomienda", "sugiere", "mejor", "ideal"],
            "navegacion": ["ruta", "camino", "distancia", "tiempo", "llegar", "ubicación"],
            "optimizacion": ["optimizar", "mejorar", "eficiencia", "rendimiento"],
            "comparacion": ["vs", "versus", "comparar", "diferencia", "mejor que"],
            "tutorial": ["tutorial", "guía", "aprender", "curso", "introducción"]
        }
    
    def _init_perfil(self) -> Dict:
        """Inicializa el perfil del usuario."""
        return {
            "preferencias": defaultdict(int),
            "categorias": defaultdict(int),
            "fuentes": defaultdict(int),
            "palabras_clave": defaultdict(int),
            "entidades": defaultdict(int),
            "clics": 0,
            "busquedas": 0,
            "feedback_positivo": 0,
            "feedback_negativo": 0,
            "ultima_actividad": None,
            "nivel_experiencia": "intermedio"  # principiante, intermedio, avanzado
        }
    
    def analizar_intencion(self, query: str) -> QueryAnalysis:
        """Analiza la intención del usuario de forma más precisa."""
        query_lower = query.lower()
        palabras = query_lower.split()
        
        # Detectar intención con puntuación
        puntuaciones = {}
        for intencion, palabras_clave in self.intenciones.items():
            puntuacion = sum(1 for p in palabras if p in palabras_clave)
            puntuacion += sum(1 for p in palabras_clave if p in query_lower) * 0.5
            if puntuacion > 0:
                puntuaciones[intencion] = puntuacion
        
        # Intención principal
        intencion_principal = max(puntuaciones, key=puntuaciones.get) if puntuaciones else "general"
        
        # Extraer entidades (nombres propios, marcas, etc.)
        entidades = self._extraer_entidades(query)
        
        # Palabras clave relevantes
        palabras_clave = [p for p in palabras if len(p) > 3 and p not in self._get_stopwords()]
        
        # Calcular prioridad
        prioridad = self._calcular_prioridad(query, intencion_principal)
        
        return QueryAnalysis(
            query=query,
            intencion=intencion_principal,
            palabras_clave=palabras_clave,
            entidades=entidades,
            prioridad=prioridad,
            timestamp=datetime.now()
        )
    
    def _extraer_entidades(self, query: str) -> List[str]:
        """Extrae entidades de la consulta."""
        # Patrones para detectar entidades
        patrones = {
            "marca": r'\b(Acer|Asus|Dell|HP|Lenovo|Samsung|Apple|Sony|Nike|Adidas|Fender|Gibson)\b',
            "producto": r'\b(laptop|teléfono|celular|computadora|tablet|guitarra|zapatillas|auriculares)\b',
            "ubicacion": r'\b(calle|avenida|barrio|ciudad|pueblo)\b'
        }
        
        entidades = []
        for tipo, patron in patrones.items():
            matches = re.findall(patron, query, re.IGNORECASE)
            entidades.extend(matches)
        
        return entidades
    
    def _get_stopwords(self) -> set:
        """Palabras vacías en español."""
        return {
            "el", "la", "los", "las", "un", "una", "unos", "unas",
            "de", "del", "al", "a", "ante", "bajo", "con", "contra",
            "en", "entre", "hacia", "hasta", "para", "por", "según",
            "sin", "sobre", "tras", "y", "o", "pero", "porque", "sino",
            "que", "cual", "quien", "donde", "cuando", "como"
        }
    
    def _calcular_prioridad(self, query: str, intencion: str) -> float:
        """Calcula la prioridad de la consulta."""
        # Factores de prioridad
        factores = {
            "longitud": min(len(query.split()) / 10, 1.0),
            "especificidad": 0.5 if any(c.isdigit() for c in query) else 0.3,
            "urgencia": 0.7 if any(w in query.lower() for w in ["urgente", "rapido", "ahora"]) else 0.3,
            "intencion_compra": 0.8 if intencion == "compra" else 0.2,
            "historial": self._prioridad_por_historial(query)
        }
        
        return sum(factores.values()) / len(factores)
    
    def _prioridad_por_historial(self, query: str) -> float:
        """Calcula prioridad basada en historial."""
        if not self.historial_usuario:
            return 0.5
        
        # Verificar si la consulta es similar a anteriores
        queries_anteriores = [h.get("query", "").lower() for h in self.historial_usuario[-20:]]
        query_lower = query.lower()
        
        for q in queries_anteriores:
            if query_lower in q or q in query_lower:
                return 0.8
        
        return 0.3
    
    def recomendar(self, query: str, resultados: List[Dict], top_n: int = 5) -> Dict:
        """Genera recomendaciones mejoradas."""
        print(f"📊 Generando recomendaciones para: '{query}'")
        
        if not resultados:
            return {"recomendaciones": [], "justificacion": "No hay resultados suficientes"}
        
        # Analizar intención
        analisis = self.analizar_intencion(query)
        
        # Puntuación de resultados
        for r in resultados:
            r["puntuacion_final"] = self._calcular_puntuacion_final(r, analisis)
        
        # Ordenar por puntuación
        resultados.sort(key=lambda x: x.get("puntuacion_final", 0), reverse=True)
        
        # Seleccionar top
        top_resultados = resultados[:top_n]
        
        # Generar justificación
        justificacion = self._generar_justificacion_detallada(query, top_resultados, analisis)
        
        return {
            "recomendaciones": top_resultados,
            "justificacion": justificacion,
            "analisis": {
                "intencion": analisis.intencion,
                "palabras_clave": analisis.palabras_clave,
                "entidades": analisis.entidades,
                "prioridad": round(analisis.prioridad, 2)
            }
        }
    
    def _calcular_puntuacion_final(self, resultado: Dict, analisis: QueryAnalysis) -> float:
        """Calcula la puntuación final de un resultado."""
        puntuacion = 0
        
        # 1. Relevancia base
        relevancia = resultado.get("relevancia", 50) / 100
        
        # 2. Coincidencia de palabras clave
        texto = (resultado.get("titulo", "") + " " + resultado.get("descripcion", "")).lower()
        coincidencias = sum(1 for p in analisis.palabras_clave if p in texto)
        puntuacion_keywords = min(coincidencias / max(len(analisis.palabras_clave), 1), 1.0)
        
        # 3. Entidades
        entidades_match = sum(1 for e in analisis.entidades if e.lower() in texto)
        puntuacion_entidades = min(entidades_match / max(len(analisis.entidades), 1), 1.0)
        
        # 4. Fuente confiable
        url = resultado.get("url", "")
        puntuacion_fuente = 0.5
        fuentes_confiables = ["wikipedia", "google", "github", "stackoverflow", "medium", "arxiv", "nature"]
        for f in fuentes_confiables:
            if f in url:
                puntuacion_fuente = 1.0
                break
        
        # 5. Calidad de descripción
        descripcion = resultado.get("descripcion", "")
        puntuacion_calidad = min(len(descripcion) / 200, 1.0)
        
        # Ponderación
        puntuacion = (
            relevancia * 0.25 +
            puntuacion_keywords * 0.30 +
            puntuacion_entidades * 0.20 +
            puntuacion_fuente * 0.15 +
            puntuacion_calidad * 0.10
        )
        
        return round(puntuacion * 100, 2)
    
    def _generar_justificacion_detallada(self, query: str, resultados: List[Dict], analisis: QueryAnalysis) -> str:
        """Genera una justificación detallada."""
        partes = []
        
        # 1. Análisis de intención
        partes.append(f"🎯 Analicé tu búsqueda '{query}' como: **{analisis.intencion}**")
        
        # 2. Palabras clave
        if analisis.palabras_clave:
            partes.append(f"🔑 Palabras clave: {', '.join(analisis.palabras_clave[:5])}")
        
        # 3. Entidades detectadas
        if analisis.entidades:
            partes.append(f"📌 Entidades: {', '.join(analisis.entidades)}")
        
        # 4. Prioridad
        partes.append(f"📊 Prioridad: {analisis.prioridad:.0%}")
        
        # 5. Resultados seleccionados
        partes.append("\n⭐ Las mejores opciones son:")
        for i, r in enumerate(resultados[:3], 1):
            titulo = r.get("titulo", "Sin título")[:50]
            punt = r.get("puntuacion_final", 0)
            partes.append(f"   {i}. {titulo} (puntuación: {punt:.1f}%)")
        
        # 6. Recomendación específica
        if analisis.intencion == "compra":
            partes.append("\n💰 Consejo: Revisa los precios en diferentes tiendas antes de comprar.")
        elif analisis.intencion == "recomendacion":
            partes.append("\n💡 Consejo: Considera las opiniones de otros usuarios.")
        
        return "\n".join(partes)
    
    def aprender(self, query: str, resultado_seleccionado: Dict, feedback: Optional[int] = None):
        """Aprende de las interacciones del usuario."""
        print(f"🧠 Aprendiendo de: '{query}'")
        
        # Actualizar estadísticas
        self.perfil_usuario["busquedas"] += 1
        
        if resultado_seleccionado:
            self.perfil_usuario["clics"] += 1
            fuente = resultado_seleccionado.get("fuente", "desconocida")
            self.perfil_usuario["fuentes"][fuente] += 1
        
        if feedback is not None:
            if feedback > 0:
                self.perfil_usuario["feedback_positivo"] += 1
            else:
                self.perfil_usuario["feedback_negativo"] += 1
        
        # Actualizar palabras clave
        analisis = self.analizar_intencion(query)
        for palabra in analisis.palabras_clave:
            self.perfil_usuario["palabras_clave"][palabra] += 1
        
        for entidad in analisis.entidades:
            self.perfil_usuario["entidades"][entidad] += 1
        
        self.perfil_usuario["categorias"][analisis.intencion] += 1
        self.perfil_usuario["ultima_actividad"] = datetime.now().isoformat()
        
        # Guardar historial
        self.historial_usuario.append({
            "fecha": datetime.now().isoformat(),
            "query": query,
            "intencion": analisis.intencion,
            "resultado": resultado_seleccionado,
            "accion": "clic" if resultado_seleccionado else "busqueda",
            "feedback": feedback
        })
        
        # Guardar perfil
        self._guardar_perfil()
    
    def _guardar_perfil(self):
        """Guarda el perfil del usuario."""
        try:
            with open("perfil_usuario.json", "w", encoding="utf-8") as f:
                json.dump({
                    "perfil": {
                        k: dict(v) if isinstance(v, defaultdict) else v 
                        for k, v in self.perfil_usuario.items()
                    },
                    "historial": self.historial_usuario[-100:]
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Error guardando perfil: {e}")