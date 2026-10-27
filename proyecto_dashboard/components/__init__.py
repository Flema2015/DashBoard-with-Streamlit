"""
Módulo de componentes visuales corporativos.
"""
from .styles import inject_corporate_styles, get_semaphore_badge
from .header_sidebar import render_header, render_sidebar
from .kpi_cards import render_kpi_cards, render_semaphore_reference

__all__ = [
    "inject_corporate_styles",
    "get_semaphore_badge",
    "render_header",
    "render_sidebar",
    "render_kpi_cards",
    "render_semaphore_reference",
]
