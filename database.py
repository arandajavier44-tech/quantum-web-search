"""
BASE DE DATOS - SQLite
RUTA: C:/Users/elpel/OneDrive/Desktop/QuantumWebSearch/database.py
"""

import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_path="historial.db"):
        self.db_path = db_path
        self._crear_tablas()
    
    def _crear_tablas(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS busquedas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    algoritmo TEXT NOT NULL,
                    resultados INTEGER,
                    tiempo REAL,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    busqueda_id INTEGER,
                    url TEXT,
                    relevancia REAL,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (busqueda_id) REFERENCES busquedas(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT,
                    url TEXT,
                    relevancia REAL,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def guardar_busqueda(self, query, algoritmo, resultados, tiempo):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO busquedas (query, algoritmo, resultados, tiempo)
                VALUES (?, ?, ?, ?)
            """, (query, algoritmo, resultados, tiempo))
            conn.commit()
            return cursor.lastrowid
    
    def guardar_clic(self, busqueda_id, url, relevancia):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO clics (busqueda_id, url, relevancia)
                VALUES (?, ?, ?)
            """, (busqueda_id, url, relevancia))
            conn.commit()
    
    def obtener_historial(self, limite=100):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, query, algoritmo, resultados, tiempo, fecha
                FROM busquedas
                ORDER BY fecha DESC
                LIMIT ?
            """, (limite,))
            return cursor.fetchall()
    
    def obtener_estadisticas(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM busquedas")
            total = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT algoritmo, COUNT(*) as count
                FROM busquedas
                GROUP BY algoritmo
                ORDER BY count DESC
            """)
            algoritmos = cursor.fetchall()
            
            cursor.execute("SELECT AVG(resultados) FROM busquedas")
            avg_resultados = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT AVG(tiempo) FROM busquedas")
            avg_tiempo = cursor.fetchone()[0] or 0
            
            return {
                "total_busquedas": total,
                "algoritmos_mas_usados": algoritmos,
                "promedio_resultados": round(avg_resultados, 2),
                "tiempo_promedio": round(avg_tiempo, 2)
            }