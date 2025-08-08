#!/usr/bin/env python3
"""
Gestion des arguments de ligne de commande pour YoobuMorph
"""

import argparse
import sys
import os
from typing import Tuple, Optional

# Ajouter le répertoire parent au path pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from utils.logging_config import get_logger

logger = get_logger()


class ArgumentParser:
    """Gestionnaire des arguments de ligne de commande"""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Crée le parser d'arguments"""
        parser = argparse.ArgumentParser(
            description="YoobuMorph - Traitement en batch d'images pour E-commerce"
        )
        
        parser.add_argument(
            "source_dir",
            nargs='?',
            help="Dossier source contenant les images à traiter"
        )
        
        parser.add_argument(
            "output_dir", 
            nargs='?',
            help="Dossier de sortie pour les images traitées"
        )
        
        parser.add_argument(
            "--size", "-s",
            type=int,
            nargs=2,
            default=[750, 750],
            help="Taille cible pour les images carrées (largeur hauteur). Défaut: 750 750"
        )
        
        parser.add_argument(
            "--bg-color", "-b",
            type=int,
            nargs=3,
            default=[255, 255, 255],
            help="Couleur de fond pour les bordures (R G B). Défaut: 255 255 255"
        )
        
        parser.add_argument(
            "--config", "-c",
            action="store_true",
            help="Utiliser la configuration depuis le fichier config"
        )
        
        return parser
    
    def parse_arguments(self):
        """Parse les arguments de ligne de commande"""
        return self.parser.parse_args()
    
    def get_configuration(self, args) -> Tuple[str, str, Tuple[int, int], Tuple[int, int, int]]:
        """
        Récupère la configuration depuis les arguments ou le fichier config
        
        Args:
            args: Arguments parsés
            
        Returns:
            Tuple (source_dir, output_base_dir, target_size, bg_color)
        """
        # Si l'option config est demandée ou si aucun argument n'est fourni
        if args.config or (not args.source_dir and not args.output_dir):
            return self._get_config_from_file()
        else:
            return self._get_config_from_args(args)
    
    def _get_config_from_file(self) -> Tuple[str, str, Tuple[int, int], Tuple[int, int, int]]:
        """Récupère la configuration depuis le fichier config"""
        try:
            from config.config import Config
            config = Config()
            
            if not config.validate_config():
                logger.error("Configuration invalide. Vérifiez le fichier config/yoobumorph_config.json")
                sys.exit(1)
            
            source_dir = config.get_source_directory()
            output_base_dir = config.get_output_base_directory()
            target_size = config.get_target_size()
            bg_color = config.get_background_color()
            
            logger.info("Utilisation de la configuration depuis le fichier config")
            return source_dir, output_base_dir, target_size, bg_color
            
        except ImportError:
            logger.error("Module config non trouvé")
            sys.exit(1)
    
    def _get_config_from_args(self, args) -> Tuple[str, str, Tuple[int, int], Tuple[int, int, int]]:
        """Récupère la configuration depuis les arguments de ligne de commande"""
        if not args.source_dir or not args.output_dir:
            logger.error("Les arguments source_dir et output_dir sont requis")
            sys.exit(1)
        
        source_dir = args.source_dir
        output_base_dir = args.output_dir  # Utilisé comme dossier de base
        target_size = tuple(args.size)
        bg_color = tuple(args.bg_color)
        
        return source_dir, output_base_dir, target_size, bg_color
    
    def validate_source_directory(self, source_dir: str) -> bool:
        """
        Valide l'existence du dossier source
        
        Args:
            source_dir: Chemin du dossier source
            
        Returns:
            True si le dossier existe, False sinon
        """
        if not os.path.exists(source_dir):
            logger.error(f"Le dossier source n'existe pas: {source_dir}")
            return False
        return True 