"""
Punto de entrada compatible main.py.
Ejecuta el dashboard modular ubicado en proyecto_dashboard/app.py.
"""
import os
import sys
import runpy

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROYECTO_DIR = os.path.join(BASE_DIR, "proyecto_dashboard")
TARGET_SCRIPT = os.path.join(PROYECTO_DIR, "app.py")

if PROYECTO_DIR not in sys.path:
    sys.path.insert(0, PROYECTO_DIR)

runpy.run_path(TARGET_SCRIPT, run_name="__main__")
