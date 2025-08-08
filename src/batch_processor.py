#!/usr/bin/env python3
"""
Traitement en batch des images pour YoobuMorph
"""

import sys
import os
from pathlib import Path
from typing import Tuple, List
from PIL import Image

# Ajouter le répertoire parent au path pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from utils.logging_config import get_logger
from src.image_processor import ImageProcessor
from src.file_manager import FileManager
from src.naming_convention import NamingConvention

logger = get_logger()


class BatchProcessor:
    """Gestionnaire du traitement en batch d'images"""
    
    def __init__(self, source_dir: str, output_base_dir: str):
        self.source_dir = Path(source_dir)
        self.output_base_dir = Path(output_base_dir)
        self.image_processor = ImageProcessor()
        self.file_manager = FileManager()
        self.naming_convention = NamingConvention()
        
        # Le dossier de sortie sera généré automatiquement selon le nom du dossier source
        # Pas besoin de le créer ici, il sera créé pour chaque image
    
    def process_batch(self, target_size: Tuple[int, int] = (750, 750), 
                     bg_color: Tuple[int, int, int] = (255, 255, 255)):
        """
        Traite en batch toutes les images du dossier source
        
        Args:
            target_size: Taille cible pour les images carrées (largeur, hauteur)
            bg_color: Couleur de fond pour les bordures (R, G, B)
        """
        self._log_batch_start(target_size)
        
        # Récupérer toutes les images du dossier source
        image_files = self.file_manager.get_image_files(self.source_dir)
        
        if not image_files:
            logger.warning("Aucune image trouvée dans le dossier source")
            return
        
        logger.info(f"Nombre d'images à traiter: {len(image_files)}")
        
        processed_count, errors = self._process_images(image_files, target_size, bg_color)
        self._log_batch_summary(processed_count, errors)
    
    def _log_batch_start(self, target_size: Tuple[int, int]):
        """Log les informations de début de traitement"""
        logger.info(f"Début du traitement en batch")
        logger.info(f"Dossier source: {self.source_dir}")
        logger.info(f"Dossier de base de sortie: {self.output_base_dir}")
        logger.info(f"Taille cible: {target_size}")
    
    def _process_images(self, image_files: List[Path], target_size: Tuple[int, int], 
                       bg_color: Tuple[int, int, int]) -> Tuple[int, List[str]]:
        """
        Traite la liste d'images
        
        Args:
            image_files: Liste des chemins d'images à traiter
            target_size: Taille cible
            bg_color: Couleur de fond
            
        Returns:
            Tuple (nombre_traitées, liste_erreurs)
        """
        processed_count = 0
        errors = []
        
        for image_path in image_files:
            try:
                logger.info(f"Traitement de: {image_path.name}")
                
                # Génération du nom de fichier et du dossier de sortie selon la convention e-commerce
                new_filename, output_dir_name = self.naming_convention.generate_filename_and_output_dir(
                    image_path, self.source_dir, target_size[0]
                )
                
                # Créer le dossier de sortie spécifique dans le dossier de base
                output_dir = self.output_base_dir / output_dir_name
                output_dir.mkdir(parents=True, exist_ok=True)
                
                output_path = output_dir / new_filename
                
                # Traitement de l'image
                self.image_processor.squareify_image(
                    image_path, output_path, target_size, bg_color
                )
                
                processed_count += 1
                logger.info(f"✓ Traité: {new_filename} dans {output_dir_name}")
                
            except Exception as e:
                error_msg = f"Erreur lors du traitement de {image_path.name}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        return processed_count, errors
    

    
    def _log_batch_summary(self, processed_count: int, errors: List[str]):
        """Log le résumé du traitement"""
        logger.info(f"\n=== RÉSUMÉ DU TRAITEMENT ===")
        logger.info(f"Images traitées avec succès: {processed_count}")
        logger.info(f"Erreurs: {len(errors)}")
        
        if errors:
            logger.error("Erreurs rencontrées:")
            for error in errors:
                logger.error(f"  - {error}") 