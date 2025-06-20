"""
Utilidades básicas para el sistema de agentes.
"""
import logging


def setup_logging(level="INFO"):
    """Configura el logging básico."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
    )
