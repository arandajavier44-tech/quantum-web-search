"""
SHOR - Algoritmo de factorización cuántica
RUTA: C:/Users/elpel/OneDrive/Desktop/QuantumWebSearch/shor_algorithm.py
"""

import math
import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector
import numpy as np


class ShorAlgorithm:
    """
    Implementación simplificada del algoritmo de Shor.
    """
    
    def __init__(self):
        self.simulador = AerSimulator()
    
    def gcd(self, a, b):
        """Máximo común divisor."""
        while b:
            a, b = b, a % b
        return a
    
    def mod_pow(self, a, power, mod):
        """Potencia modular: a^power mod mod."""
        result = 1
        while power > 0:
            if power % 2 == 1:
                result = (result * a) % mod
            a = (a * a) % mod
            power //= 2
        return result
    
    def encontrar_orden(self, a, N):
        """
        Encuentra el orden de a módulo N (versión simplificada).
        En un computador cuántico real, esto usaría QPE.
        """
        orden = 1
        while self.mod_pow(a, orden, N) != 1:
            orden += 1
            if orden > N:
                return None
        return orden
    
    def factorizar(self, N, intentos=10):
        """
        Factoriza un número N usando el algoritmo de Shor (simulado).
        """
        if N % 2 == 0:
            return [2, N//2]
        
        if N % 3 == 0:
            return [3, N//3]
        
        for _ in range(intentos):
            # 1. Elegir a aleatorio
            a = random.randint(2, N-2)
            
            # 2. Verificar si a y N son coprimos
            if self.gcd(a, N) > 1:
                factor = self.gcd(a, N)
                return [factor, N//factor]
            
            # 3. Encontrar el orden de a módulo N
            orden = self.encontrar_orden(a, N)
            
            if orden is None or orden % 2 != 0:
                continue
            
            # 4. Calcular factores
            x = self.mod_pow(a, orden//2, N)
            if x == N - 1:
                continue
            
            factor1 = self.gcd(x - 1, N)
            factor2 = self.gcd(x + 1, N)
            
            if factor1 > 1 and factor1 < N:
                return [factor1, N//factor1]
            if factor2 > 1 and factor2 < N:
                return [factor2, N//factor2]
        
        return [N, 1]  # No se encontraron factores
    
    def factorizar_con_qpe(self, N):
        """
        Versión "cuántica" usando QPE (estimación de fase cuántica).
        Simulación simplificada.
        """
        print(f"🔬 Factorizando {N} con QPE...")
        
        # Simulación de QPE (en hardware real esto sería cuántico)
        # Usamos el método clásico para simular
        return self.factorizar(N)


# ============================================================
# PRUEBA
# ============================================================

if __name__ == "__main__":
    shor = ShorAlgorithm()
    
    print("="*60)
    print("🔬 ALGORITMO DE SHOR - FACTORIZACIÓN CUÁNTICA")
    print("="*60)
    
    numeros = [15, 21, 35, 77, 91]
    
    for N in numeros:
        print(f"\n🔢 Factorizando: {N}")
        factores = shor.factorizar(N)
        print(f"   {N} = {factores[0]} × {factores[1]}")
        print(f"   ✅ {'Factorización exitosa' if factores[1] > 1 else 'Número primo'}")