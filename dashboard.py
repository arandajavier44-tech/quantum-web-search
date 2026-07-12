"""
DASHBOARD - Estadisticas y visualizaciones
"""

import json
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime, timedelta
from collections import Counter
import numpy as np

class Dashboard:
    def __init__(self, archivo_historial="historial_busquedas.json"):
        self.archivo_historial = archivo_historial
        self.historial = self._cargar_historial()
    
    def _cargar_historial(self):
        try:
            with open(self.archivo_historial, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def obtener_estadisticas(self):
        if not self.historial:
            return {
                "total_busquedas": 0,
                "promedio_resultados": 0,
                "tiempo_promedio": 0,
                "top_busquedas": [],
                "tendencia": []
            }
        
        total = len(self.historial)
        promedio_resultados = sum(h.get("resultados", 0) for h in self.historial) / total
        tiempo_promedio = sum(h.get("tiempo", 0) for h in self.historial) / total
        
        queries = [h.get("query", "") for h in self.historial]
        top_queries = Counter(queries).most_common(10)
        
        tendencia = []
        for i in range(7):
            fecha = datetime.now() - timedelta(days=i)
            dia_str = fecha.strftime("%Y-%m-%d")
            count = sum(1 for h in self.historial if h.get("fecha", "").startswith(dia_str))
            tendencia.append({
                "fecha": dia_str,
                "busquedas": count
            })
        tendencia.reverse()
        
        return {
            "total_busquedas": total,
            "promedio_resultados": round(promedio_resultados, 2),
            "tiempo_promedio": round(tiempo_promedio, 2),
            "top_busquedas": top_queries,
            "tendencia": tendencia
        }
    
    def generar_grafico_tendencia(self):
        stats = self.obtener_estadisticas()
        if not stats["tendencia"]:
            return None
        
        fechas = [d["fecha"] for d in stats["tendencia"]]
        valores = [d["busquedas"] for d in stats["tendencia"]]
        
        plt.figure(figsize=(10, 6))
        plt.plot(fechas, valores, marker='o', linewidth=2, color='#7c3aed')
        plt.fill_between(fechas, valores, alpha=0.3, color='#7c3aed')
        plt.title('Tendencia de busquedas (ultimos 7 dias)')
        plt.xlabel('Fecha')
        plt.ylabel('Busquedas')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()
        
        return img_base64
    
    def generar_grafico_top(self):
        stats = self.obtener_estadisticas()
        if not stats["top_busquedas"]:
            return None
        
        queries = [q[0] for q in stats["top_busquedas"][:10]]
        counts = [q[1] for q in stats["top_busquedas"][:10]]
        
        plt.figure(figsize=(10, 6))
        plt.barh(queries, counts, color='#7c3aed')
        plt.title('Top 10 busquedas mas frecuentes')
        plt.xlabel('Cantidad')
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()
        
        return img_base64