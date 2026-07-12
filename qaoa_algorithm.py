"""
QAOA - Algoritmo de Optimización Cuántica
RUTA: C:/Users/elpel/OneDrive/Desktop/QuantumWebSearch/qaoa_algorithm.py
"""

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector
import random


class QAOAAlgorithm:
    """
    Implementación simplificada del algoritmo QAOA para optimización.
    """
    
    def __init__(self):
        self.simulador = AerSimulator()
    
    def crear_circuito_qaoa(self, n_qubits=4, p=1, gamma=0.5, beta=0.5):
        """
        Crea un circuito QAOA básico.
        """
        qc = QuantumCircuit(n_qubits, n_qubits)
        
        # Superposición inicial
        for i in range(n_qubits):
            qc.h(i)
        
        # Capas QAOA
        for _ in range(p):
            # Capa de costo (gamma)
            for i in range(n_qubits - 1):
                qc.cx(i, i + 1)
                qc.rz(gamma, i + 1)
                qc.cx(i, i + 1)
            
            # Capa de mezcla (beta)
            for i in range(n_qubits):
                qc.rx(beta, i)
        
        qc.measure_all()
        return qc
    
    def optimizar(self, n_qubits=4, p=1, iteraciones=20):
        """
        Optimiza usando QAOA para encontrar la mejor configuración.
        """
        print(f"🔬 Optimizando con QAOA ({n_qubits} qubits, {p} capas)...")
        
        mejores_resultados = None
        mejor_energia = float('inf')
        
        for i in range(iteraciones):
            gamma = random.uniform(0, np.pi)
            beta = random.uniform(0, np.pi)
            
            qc = self.crear_circuito_qaoa(n_qubits, p, gamma, beta)
            transpiled = transpile(qc, self.simulador)
            job = self.simulador.run(transpiled, shots=1024)
            counts = job.result().get_counts()
            
            # Calcular "energía" (mejor estado = menor energía)
            for estado, count in counts.items():
                # Convertir a binario y calcular energía
                binario = int(estado, 2)
                energia = binario  # Simplificado: menor binario = mejor
                
                if energia < mejor_energia:
                    mejor_energia = energia
                    mejores_resultados = {
                        "estado": estado,
                        "energia": energia,
                        "gamma": gamma,
                        "beta": beta,
                        "conteos": count
                    }
        
        if mejores_resultados:
            return {
                "mejor_estado": mejores_resultados["estado"],
                "energia": mejores_resultados["energia"],
                "gamma": mejores_resultados["gamma"],
                "beta": mejores_resultados["beta"],
                "frecuencia": mejores_resultados["conteos"]
            }
        else:
            return {"error": "No se encontraron resultados"}
    
    def problema_mochila(self, pesos, valores, capacidad):
        """
        Resuelve el problema de la mochila con QAOA (simulación).
        
        Args:
            pesos (list): Pesos de los objetos
            valores (list): Valores de los objetos
            capacidad (int): Capacidad máxima
        
        Returns:
            dict: Mejor combinación encontrada
        """
        n = len(pesos)
        print(f"🎒 Problema de la mochila: {n} objetos, capacidad {capacidad}")
        
        mejor_valor = 0
        mejor_combinacion = []
        mejor_estado = ""
        
        # Simular QAOA (búsqueda exhaustiva simplificada)
        for i in range(2**n):
            binario = format(i, f'0{n}b')
            peso_total = 0
            valor_total = 0
            
            for j, bit in enumerate(binario):
                if bit == '1':
                    peso_total += pesos[j]
                    valor_total += valores[j]
            
            if peso_total <= capacidad and valor_total > mejor_valor:
                mejor_valor = valor_total
                mejor_combinacion = [j for j, bit in enumerate(binario) if bit == '1']
                mejor_estado = binario
        
        return {
            "mejor_estado": mejor_estado,
            "valor_total": mejor_valor,
            "peso_total": sum(pesos[i] for i in mejor_combinacion),
            "objetos": mejor_combinacion,
            "explicacion": f"Seleccionar objetos {mejor_combinacion} con valor total {mejor_valor}"
        }


# ============================================================
# PRUEBA
# ============================================================

if __name__ == "__main__":
    qaoa = QAOAAlgorithm()
    
    print("="*60)
    print("🔬 QAOA - OPTIMIZACIÓN CUÁNTICA")
    print("="*60)
    
    # 1. QAOA básico
    print("\n📊 Optimización QAOA (4 qubits):")
    resultado = qaoa.optimizar(n_qubits=4, p=1, iteraciones=10)
    print(f"   Mejor estado: {resultado['mejor_estado']}")
    print(f"   Energía: {resultado['energia']}")
    print(f"   Frecuencia: {resultado['frecuencia']}")
    
    # 2. Problema de la mochila
    print("\n🎒 Problema de la mochila:")
    pesos = [2, 3, 4, 5]
    valores = [3, 4, 5, 6]
    capacidad = 8
    
    resultado = qaoa.problema_mochila(pesos, valores, capacidad)
    print(f"   Mejor estado: {resultado['mejor_estado']}")
    print(f"   Valor total: {resultado['valor_total']}")
    print(f"   Peso total: {resultado['peso_total']}")
    print(f"   {resultado['explicacion']}")