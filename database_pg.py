"""
BASE DE DATOS POSTGRESQL
RUTA: C:/Users/elpel/OneDrive/Desktop/QuantumWebSearch/database_pg.py
"""

import os
import psycopg2
from datetime import datetime

class DatabasePG:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'quantum_search'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )
        self._crear_tablas()
    
    def _crear_tablas(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS busquedas (
                    id SERIAL PRIMARY KEY,
                    query TEXT NOT NULL,
                    algoritmo TEXT NOT NULL,
                    resultados INTEGER,
                    tiempo REAL,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS clics (
                    id SERIAL PRIMARY KEY,
                    busqueda_id INTEGER REFERENCES busquedas(id),
                    url TEXT,
                    relevancia REAL,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    query TEXT,
                    url TEXT,
                    relevancia REAL,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.commit()
    
    def guardar_busqueda(self, query, algoritmo, resultados, tiempo):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO busquedas (query, algoritmo, resultados, tiempo)
                VALUES (%s, %s, %s, %s) RETURNING id
            """, (query, algoritmo, resultados, tiempo))
            self.conn.commit()
            return cur.fetchone()[0]
    
    def guardar_clic(self, busqueda_id, url, relevancia):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO clics (busqueda_id, url, relevancia)
                VALUES (%s, %s, %s)
            """, (busqueda_id, url, relevancia))
            self.conn.commit()
    
    def obtener_historial(self, limite=100):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, query, algoritmo, resultados, tiempo, fecha
                FROM busquedas
                ORDER BY fecha DESC
                LIMIT %s
            """, (limite,))
            return cur.fetchall()
    
    def obtener_estadisticas(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM busquedas")
            total = cur.fetchone()[0]
            
            cur.execute("""
                SELECT algoritmo, COUNT(*) as count
                FROM busquedas
                GROUP BY algoritmo
                ORDER BY count DESC
            """)
            algoritmos = cur.fetchall()
            
            cur.execute("SELECT AVG(resultados) FROM busquedas")
            avg_resultados = cur.fetchone()[0] or 0
            
            cur.execute("SELECT AVG(tiempo) FROM busquedas")
            avg_tiempo = cur.fetchone()[0] or 0
            
            return {
                "total_busquedas": total,
                "algoritmos_mas_usados": algoritmos,
                "promedio_resultados": round(avg_resultados, 2),
                "tiempo_promedio": round(avg_tiempo, 2)
            }