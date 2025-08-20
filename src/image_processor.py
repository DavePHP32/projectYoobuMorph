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
                       bg_color: Tuple[int, int, int] = (255, 255, 255)) -> Tuple[int, int]:
        """
        Carréifie une image en gardant la dimension maximale et en ajoutant des bordures
        
        Args:
            input_path: Chemin vers l'image source
            output_path: Chemin vers l'image de sortie
            bg_color: Couleur de fond pour les bordures (R, G, B)
        
        Returns:
            Tuple[int, int]: Dimensions finales de l'image (largeur, hauteur)
        
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
                
                logger.info(f"Image originale: {original_width}x{original_height}")
                
                # Déterminer la stratégie de carréification
                strategy = self._determine_squareification_strategy(
                    original_width, original_height
                )
                
                # Appliquer la carréification
                squared_image, final_dimensions = self._apply_squareification_strategy(
                    img, strategy, bg_color
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
                logger.info(f"Dimensions finales: {final_dimensions[0]}x{final_dimensions[1]}")
                
                return final_dimensions
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement de {input_path}: {str(e)}")
            raise
    
    def _determine_squareification_strategy(self, original_width: int, original_height: int) -> str:
        """
        Détermine la stratégie de carréification selon la rectangularité
        
        Returns:
            str: 'horizontal', 'vertical', ou 'square'
        """
        # Calculer les ratios
        original_ratio = original_width / original_height
        
        logger.info(f"Image originale: {original_width}x{original_height}")
        logger.info(f"Ratio original: {original_ratio:.4f}")
        
        # Déterminer la stratégie
        if original_ratio == 1.0:  # Image parfaitement carrée (±1%)
            logger.info("Image parfaitement carrée - pas de carréification nécessaire")
            return 'square'
   
        elif original_ratio > 1.0:  # Image horizontale (largeur > hauteur)
            logger.info("Image horizontale - bordures haut/bas")
            return 'horizontal'
        else:  # Image verticale (hauteur > largeur)
            logger.info("Image verticale - bordures gauche/droite")
            return 'vertical'
    
    def _apply_squareification_strategy(self, img: Image.Image, strategy: str,
                                      bg_color: Tuple[int, int, int]) -> Tuple[Image.Image, Tuple[int, int]]:
        """
        Applique la stratégie de carréification
        
        Args:
            img: Image PIL à traiter
            strategy: Stratégie ('horizontal', 'vertical', 'square')
            bg_color: Couleur de fond
        
        Returns:
            Tuple[Image.Image, Tuple[int, int]]: Image carréifiée et dimensions finales
        """
        original_width, original_height = img.size
        
        if strategy == 'square':
            # Image déjà carrée, NE PAS la redimensionner, garder les dimensions originales
            logger.info("Stratégie: Image déjà carrée - GARDER les dimensions originales")
            logger.info(f"Image {original_width}x{original_height} → Pas de changement")
            return img, (original_width, original_height) # Retourner l'image originale sans modification
        
        elif strategy == 'horizontal':
            # Image horizontale: garder la largeur maximale et carréifier
            logger.info("Stratégie: Image horizontale - garder largeur maximale et carréifier")
            logger.info(f"Exemple: {original_width}x{original_height} → {original_width}x{original_width}")
            
            # Garder la largeur originale et créer une image carrée
            square_size = original_width
            
            logger.info(f"Carréification: {original_width}x{original_height} → {square_size}x{square_size}")
            
            # Créer l'image finale carrée avec bordures
            final_img = Image.new('RGB', (square_size, square_size), bg_color)
            
            # Centrer l'image originale (sans redimensionnement)
            y_offset = (square_size - original_height) // 2
            final_img.paste(img, (0, y_offset))
            
            logger.info(f"Bordures ajoutées: {y_offset}px en haut et en bas")
            return final_img, (square_size, square_size)
        
        elif strategy == 'vertical':
            # Image verticale: garder la hauteur maximale et carréifier
            logger.info("Stratégie: Image verticale - garder hauteur maximale et carréifier")
            logger.info(f"Exemple: {original_width}x{original_height} → {original_height}x{original_height}")
            
            # Garder la hauteur originale et créer une image carrée
            square_size = original_height
            
            logger.info(f"Carréification: {original_width}x{original_height} → {square_size}x{square_size}")
            
            # Créer l'image finale carrée avec bordures
            final_img = Image.new('RGB', (square_size, square_size), bg_color)
            
            # Centrer l'image originale (sans redimensionnement)
            x_offset = (square_size - original_width) // 2
            final_img.paste(img, (x_offset, 0))
            
            logger.info(f"Bordures ajoutées: {x_offset}px à gauche et à droite")
            return final_img, (square_size, square_size)
        
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