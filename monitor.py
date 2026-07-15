# monitor.py - Nuevo archivo para monitoreo

import time
import json
import logging
from datetime import datetime
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import threading

@dataclass
class Metric:
    """Métrica de rendimiento."""
    nombre: str
    valor: float
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)

class Monitor:
    """Sistema de monitoreo y rendimiento."""
    
    def __init__(self, max_historial=1000):
        self.metricas = defaultdict(lambda: deque(maxlen=max_historial))
        self.alertas = []
        self.umbrales = {
            "tiempo_busqueda": 5.0,  # segundos
            "tasa_error": 0.1,       # 10%
            "cache_hit_rate": 0.3    # 30%
        }
        self.lock = threading.Lock()
        self._iniciar_monitoreo()
    
    def _iniciar_monitoreo(self):
        """Inicia el monitoreo en segundo plano."""
        def monitorear():
            while True:
                time.sleep(60)  # Cada minuto
                self._verificar_alertas()
        
        thread = threading.Thread(target=monitorear, daemon=True)
        thread.start()
    
    def registrar_metrica(self, nombre: str, valor: float, tags: Optional[Dict] = None):
        """Registra una métrica."""
        with self.lock:
            self.metricas[nombre].append(Metric(
                nombre=nombre,
                valor=valor,
                tags=tags or {}
            ))
    
    def registrar_busqueda(self, query: str, tiempo: float, exito: bool, resultados: int):
        """Registra una búsqueda."""
        self.registrar_metrica("busqueda_tiempo", tiempo, {"query": query[:30]})
        self.registrar_metrica("busqueda_resultados", resultados)
        self.registrar_metrica("busqueda_exito", 1 if exito else 0)
    
    def registrar_cache(self, hit: bool):
        """Registra un acceso a caché."""
        self.registrar_metrica("cache_hit", 1 if hit else 0)
    
    def _verificar_alertas(self):
        """Verifica si hay alertas que generar."""
        # Tiempo de búsqueda
        tiempos = [m.valor for m in self.metricas.get("busqueda_tiempo", [])[-10:]]
        if tiempos and sum(tiempos) / len(tiempos) > self.umbrales["tiempo_busqueda"]:
            self.alertas.append({
                "tipo": "rendimiento",
                "mensaje": f"Tiempo de búsqueda elevado: {sum(tiempos)/len(tiempos):.2f}s",
                "timestamp": datetime.now().isoformat()
            })
        
        # Tasa de error
        exitos = [m.valor for m in self.metricas.get("busqueda_exito", [])[-20:]]
        if exitos:
            tasa_error = 1 - (sum(exitos) / len(exitos))
            if tasa_error > self.umbrales["tasa_error"]:
                self.alertas.append({
                    "tipo": "error",
                    "mensaje": f"Tasa de error alta: {tasa_error:.1%}",
                    "timestamp": datetime.now().isoformat()
                })
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas del sistema."""
        with self.lock:
            stats = {
                "metricas": {},
                "alertas": self.alertas[-10:],
                "resumen": {
                    "total_busquedas": len(self.metricas.get("busqueda_tiempo", [])),
                    "total_metricas": sum(len(v) for v in self.metricas.values()),
                    "ultima_actualizacion": datetime.now().isoformat()
                }
            }
            
            # Calcular promedios
            for nombre, metricas in self.metricas.items():
                if metricas:
                    valores = [m.valor for m in metricas]
                    stats["metricas"][nombre] = {
                        "promedio": sum(valores) / len(valores),
                        "min": min(valores),
                        "max": max(valores),
                        "ultimo": metricas[-1].valor,
                        "cantidad": len(valores)
                    }
            
            return stats
    
    def exportar_metricas(self, archivo="metricas.json"):
        """Exporta métricas a archivo."""
        with self.lock:
            data = []
            for nombre, metricas in self.metricas.items():
                for m in metricas:
                    data.append({
                        "nombre": m.nombre,
                        "valor": m.valor,
                        "timestamp": m.timestamp.isoformat(),
                        "tags": m.tags
                    })
            
            with open(archivo, "w") as f:
                json.dump(data, f, indent=2)

# Uso en app.py
monitor = Monitor()

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    if hasattr(request, 'start_time'):
        elapsed = time.time() - request.start_time
        monitor.registrar_metrica(
            "request_tiempo",
            elapsed,
            {"path": request.path, "method": request.method}
        )
    return response