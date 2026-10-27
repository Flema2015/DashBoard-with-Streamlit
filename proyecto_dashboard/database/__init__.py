"""
Módulo de base de datos SQLite para el Dashboard de Mesa de Ayuda.
"""
from .connection import get_connection
from .schema_seed import init_db
from .queries import (
    validar_credenciales,
    obtener_kpis_globales,
    obtener_metricas_departamentos,
    obtener_departamento_por_id,
    obtener_tecnicos_por_departamento,
    obtener_tecnico_por_id,
    obtener_tickets_por_tecnico,
    obtener_distribucion_prioridad_tecnico,
    obtener_distribucion_estado_tecnico,
    crear_usuario,
    cambiar_password,
    listar_usuarios,
)

__all__ = [
    "get_connection",
    "init_db",
    "validar_credenciales",
    "obtener_kpis_globales",
    "obtener_metricas_departamentos",
    "obtener_departamento_por_id",
    "obtener_tecnicos_por_departamento",
    "obtener_tecnico_por_id",
    "obtener_tickets_por_tecnico",
    "obtener_distribucion_prioridad_tecnico",
    "obtener_distribucion_estado_tecnico",
    "crear_usuario",
    "cambiar_password",
    "listar_usuarios",
]
