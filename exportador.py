"""
EXPORTADOR - Exportación de resultados
RUTA: C:/Users/elpel/OneDrive/Desktop/QuantumWebSearch/exportador.py
"""

import json
import csv
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

class Exportador:
    def exportar_json(self, datos, archivo="export.json"):
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        return archivo
    
    def exportar_csv(self, datos, archivo="export.csv"):
        if not datos:
            return None
        campos = []
        for d in datos:
            if isinstance(d, dict):
                campos.extend(d.keys())
        campos = list(set(campos))
        with open(archivo, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            for d in datos:
                writer.writerow(d)
        return archivo
    
    def exportar_pdf(self, datos, titulo="Resultados", archivo="export.pdf"):
        c = canvas.Canvas(archivo, pagesize=A4)
        width, height = A4
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, height - 50, titulo)
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 70, f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        y = height - 100
        c.setFont("Helvetica", 10)
        for i, item in enumerate(datos[:20]):
            if y < 50:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 10)
            if isinstance(item, dict):
                texto = f"{i+1}. {item.get('titulo', 'Sin titulo')[:80]}"
                c.drawString(50, y, texto)
                y -= 20
                texto2 = f"   {item.get('url', '#')[:80]}"
                c.setFont("Helvetica", 8)
                c.drawString(50, y, texto2)
                y -= 20
                c.setFont("Helvetica", 10)
                if item.get('descripcion'):
                    texto3 = f"   {item.get('descripcion', '')[:100]}..."
                    c.setFont("Helvetica", 9)
                    c.drawString(50, y, texto3)
                    y -= 25
                    c.setFont("Helvetica", 10)
            else:
                c.drawString(50, y, f"{i+1}. {str(item)[:100]}")
                y -= 20
            if i % 5 == 0 and i > 0:
                y -= 10
        c.save()
        return archivo