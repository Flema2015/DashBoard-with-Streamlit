"""
Módulo de vistas analíticas del Dashboard en 3 niveles.
"""
from .login_view import render_login_view
from .nivel1_deptos import render_nivel1_view
from .nivel2_tecnicos import render_nivel2_view
from .nivel3_tickets import render_nivel3_view

__all__ = [
    "render_login_view",
    "render_nivel1_view",
    "render_nivel2_view",
    "render_nivel3_view",
]
