#!/usr/bin/env python3
"""
YoobuMorph - Traitement en batch d'images pour E-commerce
==========================================================

Ce programme permet de traiter en batch un lot d'images présentes dans un dossier.
Il carréifie les images en gardant la dimension maximale et en ajoutant des bordures
selon la rectangularité de l'image.

Fonctionnalités:
- Traitement en batch d'un dossier d'images
- Carréification avec bordures intelligentes
- Génération de noms de fichiers selon la convention e-commerce
- Support de différents formats d'image
"""

import sys
import os
from typing import Tuple

# Ajout du répertoire parent au path pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from utils.logging_config import setup_logging, get_logger  
from utils.argument_parser import ArgumentParser
from src.batch_processor import BatchProcessor

# Configuration du logging 
logger = setup_logging()


def main():
    """Point d'entrée principal du programme"""
    # Initialisation du parser d'arguments
    arg_parser = ArgumentParser()
    args = arg_parser.parse_arguments()
    
    # Récupération de la configuration
    try:
        source_dir, output_base_dir, bg_color = arg_parser.get_configuration(args)
    except SystemExit:
        return
    
    # Validation du dossier source
    if not arg_parser.validate_source_directory(source_dir):
        sys.exit(1)
    
    # Exécution du traitement
    try:
        processor = BatchProcessor(source_dir, output_base_dir)
        processor.process_batch(bg_color)
        logger.info("Traitement terminé avec succès!")
        
    except Exception as e:
        logger.error(f"Erreur fatale: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 