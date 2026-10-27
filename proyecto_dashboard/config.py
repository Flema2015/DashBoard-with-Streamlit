"""
Configuración centralizada, constantes y paleta de colores corporativa (Estilo GLPI / ITSM).
"""
import os

# Rutas de base de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = "mesa_ayuda.db"

# Localizar la base de datos en el directorio actual o en el directorio raíz
if os.path.exists(os.path.join(BASE_DIR, DB_NAME)):
    DB_PATH = os.path.join(BASE_DIR, DB_NAME)
elif os.path.exists(os.path.join(os.path.dirname(BASE_DIR), DB_NAME)):
    DB_PATH = os.path.join(os.path.dirname(BASE_DIR), DB_NAME)
else:
    DB_PATH = os.path.join(BASE_DIR, DB_NAME)

# Paleta de Colores Corporativa (Inspirada en paneles GLPI / ITSM)
COLOR_PRIMARY = "#1E40AF"       # Azul institucional (Totales y barras base)
COLOR_CYAN = "#0284C7"          # Celeste / Cyan (En proceso / Asignados)
COLOR_GREEN = "#059669"         # Verde esmeralda (Resueltos / Dentro de SLA)
COLOR_RED = "#DC2626"           # Rojo coral (Vencidos / Fuera de SLA)
COLOR_AMBER = "#D97706"         # Naranja / Amarillo (Por vencer / Advertencia)
COLOR_CRITICAL = "#7F1D1D"      # Rojo oscuro / Prioridad crítica
COLOR_DARK = "#1E293B"          # Gris pizarra oscuro (Cabecera y contrastes)
COLOR_CARD_BG = "#FFFFFF"       # Blanco puro para tarjetas
COLOR_GRID = "rgba(128,128,128,0.2)"  # Grilla punteada tenue requerida

# Mapeo de Colores para Semáforo de SLA
COLOR_SEMAFORO = {
    "VERDE": COLOR_GREEN,
    "AMARILLO": COLOR_AMBER,
    "ROJO": COLOR_RED,
}

# Textos Formales de Referencia de SLA
SLA_DESCRIPCIONES = {
    "VERDE": "Dentro de SLA (Situación normal / favorable)",
    "AMARILLO": "Por vencer — menos del 20% del tiempo de SLA restante (Advertencia)",
    "ROJO": "Vencido / Fuera de SLA (Situación crítica)",
}

# Mapeo de Colores para Prioridades
COLOR_PRIORIDAD = {
    "critica": COLOR_CRITICAL,
    "alta": COLOR_RED,
    "media": COLOR_AMBER,
    "baja": COLOR_PRIMARY,
}
