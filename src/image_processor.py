"""
Module de traitement d'images pour YoobuMorph
============================================

Ce module contient la logique de traitement d'images, notamment la carréification
avec bordures intelligentes selon la rectangularité de l'image.
"""

from PIL import Image, ImageOps
from pathlib import Path
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Classe pour le traitement d'images avec carréification intelligente"""
    
    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'}
    
    def squareify_image(self, input_path: Path, output_path: Path, 
                       target_size: Tuple[int, int] = (750, 750),
                       bg_color: Tuple[int, int, int] = (255, 255, 255)) -> None:
        """
        Carréifie une image en gardant la dimension maximale et en ajoutant des bordures
        
        Args:
            input_path: Chemin vers l'image source
            output_path: Chemin vers l'image de sortie
            target_size: Taille cible (largeur, hauteur)
            bg_color: Couleur de fond pour les bordures (R, G, B)
        
        Raises:
            ValueError: Si l'image ne peut pas être ouverte
            OSError: Si l'image ne peut pas être sauvegardée
        """
        try:
            # Ouvrir l'image
            with Image.open(input_path) as img:
                # Convertir en RGB si nécessaire
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                original_width, original_height = img.size
                target_width, target_height = target_size
                
                logger.info(f"Image originale: {original_width}x{original_height}")
                logger.info(f"Taille cible: {target_width}x{target_height}")
                
                # Déterminer la stratégie de carréification
                strategy = self._determine_squareification_strategy(
                    original_width, original_height, target_width, target_height
                )
                
                # Appliquer la carréification
                squared_image = self._apply_squareification_strategy(
                    img, strategy, target_size, bg_color
                )
                
                # Sauvegarder l'image
                if strategy == 'square':
                    # Pour les images carrées, garder le format original
                    logger.info("Sauvegarde de l'image originale sans modification")
                    squared_image.save(output_path)
                else:
                    # Pour les images carréifiées, sauvegarder en JPG optimisé
                    logger.info("Sauvegarde de l'image carréifiée en JPG")
                    squared_image.save(output_path, quality=95, optimize=True)
                
                logger.info(f"Image carréifiée sauvegardée: {output_path}")
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement de {input_path}: {str(e)}")
            raise
    
    def _determine_squareification_strategy(self, original_width: int, original_height: int,
                                          target_width: int, target_height: int) -> str:
        """
        Détermine la stratégie de carréification selon la rectangularité
        
        Returns:
            str: 'horizontal', 'vertical', ou 'square'
        """
        # Calculer les ratios
        original_ratio = original_width / original_height
        target_ratio = target_width / target_height
        
        logger.info(f"Image originale: {original_width}x{original_height}")
        logger.info(f"Ratio original: {original_ratio:.2f}")
        logger.info(f"Taille cible: {target_width}x{target_height}")
        
        # Déterminer la stratégie
        if abs(original_ratio - 1.0) < 0.1:  # Image déjà carrée (±10%)
            logger.info("Image déjà carrée - pas de carréification nécessaire")
            return 'square'
        elif original_ratio > 1.0:  # Image horizontale (largeur > hauteur)
            logger.info("Image horizontale - bordures haut/bas")
            return 'horizontal'
        else:  # Image verticale (hauteur > largeur)
            logger.info("Image verticale - bordures gauche/droite")
            return 'vertical'
    
    def _apply_squareification_strategy(self, img: Image.Image, strategy: str,
                                      target_size: Tuple[int, int],
                                      bg_color: Tuple[int, int, int]) -> Image.Image:
        """
        Applique la stratégie de carréification
        
        Args:
            img: Image PIL à traiter
            strategy: Stratégie ('horizontal', 'vertical', 'square')
            target_size: Taille cible (largeur, hauteur)
            bg_color: Couleur de fond
        
        Returns:
            Image.Image: Image carréifiée
        """
        target_width, target_height = target_size
        original_width, original_height = img.size
        
        if strategy == 'square':
            # Image déjà carrée, NE PAS la redimensionner, garder les dimensions originales
            logger.info("Stratégie: Image déjà carrée - GARDER les dimensions originales")
            logger.info(f"Image {original_width}x{original_height} → Pas de changement")
            return img  # Retourner l'image originale sans modification
        
        elif strategy == 'horizontal':
            # Image horizontale: bordures en haut et bas
            logger.info("Stratégie: Image horizontale - bordures haut/bas")
            logger.info(f"Exemple: {original_width}x{original_height} → {target_width}x{target_height}")
            
            # Calculer la nouvelle taille en gardant la largeur maximale
            scale_factor = target_width / original_width
            new_width = target_width
            new_height = int(original_height * scale_factor)
            
            logger.info(f"Redimensionnement: {original_width}x{original_height} → {new_width}x{new_height}")
            
            # Redimensionner l'image
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Créer l'image finale avec bordures
            final_img = Image.new('RGB', target_size, bg_color)
            
            # Centrer l'image
            y_offset = (target_height - new_height) // 2
            final_img.paste(resized_img, (0, y_offset))
            
            logger.info(f"Bordures ajoutées: {y_offset}px en haut et en bas")
            return final_img
        
        elif strategy == 'vertical':
            # Image verticale: bordures à gauche et droite
            logger.info("Stratégie: Image verticale - bordures gauche/droite")
            logger.info(f"Exemple: {original_width}x{original_height} → {target_width}x{target_height}")
            
            # Calculer la nouvelle taille en gardant la hauteur maximale
            scale_factor = target_height / original_height
            new_width = int(original_width * scale_factor)
            new_height = target_height
            
            logger.info(f"Redimensionnement: {original_width}x{original_height} → {new_width}x{new_height}")
            
            # Redimensionner l'image
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Créer l'image finale avec bordures
            final_img = Image.new('RGB', target_size, bg_color)
            
            # Centrer l'image
            x_offset = (target_width - new_width) // 2
            final_img.paste(resized_img, (x_offset, 0))
            
            logger.info(f"Bordures ajoutées: {x_offset}px à gauche et à droite")
            return final_img
        
        else:
            raise ValueError(f"Stratégie inconnue: {strategy}")
    
    def get_image_info(self, image_path: Path) -> dict:
        """
        Récupère les informations d'une image
        
        Args:
            image_path: Chemin vers l'image
        
        Returns:
            dict: Informations de l'image (dimensions, format, etc.)
        """
        try:
            with Image.open(image_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'size_bytes': image_path.stat().st_size
                }
        except Exception as e:
            logger.error(f"Erreur lors de la lecture des infos de {image_path}: {str(e)}")
            raise
    
    def validate_image(self, image_path: Path) -> bool:
        """
        Valide qu'une image peut être traitée
        
        Args:
            image_path: Chemin vers l'image
        
        Returns:
            bool: True si l'image est valide
        """
        try:
            with Image.open(image_path) as img:
                # Vérifier que l'image peut être convertie en RGB
                img.convert('RGB')
                return True
        except Exception as e:
            logger.warning(f"Image invalide {image_path}: {str(e)}")
            return False 