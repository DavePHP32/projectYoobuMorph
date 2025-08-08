#!/usr/bin/env python3
"""
Configuration du logging pour YoobuMorph
"""

import logging
from pathlib import Path


def setup_logging(log_file: str = 'yoobumorph.log') -> logging.Logger:
    """
    Configure le logging pour l'application
    
    Args:
        log_file: Nom du fichier de log
        
    Returns:
        Logger configuré
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def get_logger() -> logging.Logger:
    """
    Retourne le logger configuré
    
    Returns:
        Logger configuré
    """
    return logging.getLogger(__name__) 