#!/usr/bin/env python3
"""
Ejemplo: Integración con sistema automatizado usando salida JSON

Este script muestra cómo integrar MagicBridge en un sistema automatizado
usando las salidas JSON de los scripts de control.
"""

import subprocess
import json
import sys
from datetime import datetime

# Configuración
ARCHIVO_HMF = " .\Ford_MACH_E_20230901_R018.hmf"  # Cambiar por tu archivo
PUERTO = "COM25"     # Cambiar por tu puerto (COM3 en Windows)
PCB = 5
VARIANTE = "D"

def ejecutar_comando(cmd):
    """Ejecuta comando y retorna código de salida y salida"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except Exception as e:
        return -1, "", str(e)

def cargar_datos():
    """Paso 1: Cargar datos HMF"""
    print("━" * 60)
    print("📥 Cargando datos HMF al MagicBridge...")
    print("━" * 60)
    
    cmd = [
        "python", "../bin/runner_load.py",
        ARCHIVO_HMF, PUERTO, str(PCB), VARIANTE,
        "--json", "carga.json",
        "--quiet"
    ]
    
    codigo, stdout, stderr = ejecutar_comando(cmd)
    
    if codigo == 0:
        # Leer resultado JSON
        with open("carga.json", "r") as f:
            resultado = json.load(f)
        
        print(f"✅ Carga exitosa")
        print(f"   Entradas cargadas: {resultado['result']['entries_loaded']}")
        print(f"   Tiempo: {resultado['timestamp']['duration_ms']}ms")
        return True, resultado
    else:
        print(f"❌ Error al cargar datos (código {codigo})")
        if stderr:
            print(f"   Error: {stderr}")
        return False, None

def programar_chip():
    """Paso 2: Programar chip"""
    print("")
    print("━" * 60)
    print("✍️  Programando chip...")
    print("━" * 60)
    
    comando = f"W{PCB}{VARIANTE.lower()}"
    
    cmd = [
        "python", "../bin/runner_cmd.py",
        PUERTO, comando,
        "--json", "programacion.json",
        "--quiet"
    ]
    
    codigo, stdout, stderr = ejecutar_comando(cmd)
    
    if codigo == 0:
        # Leer resultado JSON
        with open("programacion.json", "r") as f:
            resultado = json.load(f)
        
        print(f"✅ Programación exitosa")
        print(f"   Comando: {resultado.get('input', {}).get('command', comando)}")
        print(f"   Tiempo: {resultado['timestamp']['duration_ms']}ms")
        return True, resultado
    else:
        print(f"❌ Error al programar chip (código {codigo})")
        if stderr:
            print(f"   Error: {stderr}")
        return False, None

def main():
    """Función principal"""
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "MagicBridge - Integración JSON" + " " * 18 + "║")
    print("╚" + "═" * 58 + "╝")
    print("")
    print(f"📋 Configuración:")
    print(f"   Archivo: {ARCHIVO_HMF}")
    print(f"   Puerto:  {PUERTO}")
    print(f"   PCB:     {PCB}")
    print(f"   Variante: {VARIANTE}")
    print(f"   Inicio:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    # Paso 1: Cargar datos
    exito_carga, resultado_carga = cargar_datos()
    if not exito_carga:
        print("\n❌ Proceso abortado por error en carga")
        sys.exit(1)
    
    # Paso 2: Programar
    exito_prog, resultado_prog = programar_chip()
    if not exito_prog:
        print("\n❌ Proceso abortado por error en programación")
        sys.exit(2)
    
    # Resumen
    print("")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "✅ PROCESO COMPLETADO" + " " * 22 + "║")
    print("╠" + "═" * 58 + "╣")
    print(f"║  Entradas cargadas: {resultado_carga['result']['entries_loaded']}" + " " * 32 + "║")
    print(f"║  Tiempo total:      {resultado_carga['timestamp']['duration_ms'] + resultado_prog['timestamp']['duration_ms']}ms" + " " * 30 + "║")
    print("╚" + "═" * 58 + "╝")
    
    # Guardar resumen completo
    resumen = {
        "timestamp": datetime.now().isoformat(),
        "configuracion": {
            "archivo": ARCHIVO_HMF,
            "puerto": PUERTO,
            "pcb": PCB,
            "variante": VARIANTE
        },
        "carga": resultado_carga,
        "programacion": resultado_prog,
        "exito": True
    }
    
    with open("resumen_completo.json", "w") as f:
        json.dump(resumen, f, indent=2)
    
    print("\n📄 Resumen guardado en: resumen_completo.json")
    sys.exit(0)

if __name__ == "__main__":
    main()
