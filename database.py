# database.py - Versión mejorada

import sqlite3
from datetime import datetime
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path="historial.db"):
        self.db_path = db_path
        self._crear_tablas()
        self._crear_indices()
    
    @contextmanager
    def _get_connection(self):
        """Context manager para conexiones."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Para acceder por nombre
        try:
            yield conn
        finally:
            conn.close()
    
    def _crear_indices(self):
        """Crea índices para mejorar rendimiento."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_busquedas_fecha ON busquedas(fecha DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_busquedas_query ON busquedas(query)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_clics_busqueda ON clics(busqueda_id)")
            conn.commit()
    
    def _crear_tablas(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabla busquedas con más campos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS busquedas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    algoritmo TEXT NOT NULL,
                    resultados INTEGER,
                    tiempo REAL,
                    ip TEXT,
                    usuario_id INTEGER,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    busqueda_id INTEGER,
                    url TEXT,
                    relevancia REAL,
                    posicion INTEGER,
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
                    comentario TEXT,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()