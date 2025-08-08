"""
Module de gestion des fichiers pour YoobuMorph
=============================================

Ce module gère la découverte, la validation et l'organisation des fichiers d'images
dans les dossiers source.
"""

from pathlib import Path
from typing import List, Set, Optional
import logging
import os

logger = logging.getLogger(__name__)

class FileManager:
    """Classe pour la gestion des fichiers d'images"""
    
    def __init__(self):
        # Formats d'images supportés
        self.supported_extensions = {
            '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif'
        }
        
        # Extensions pour les images de référence (non traitées)
        self.reference_extensions = {'.webp', '.svg'}
    
    def get_image_files(self, directory: Path, recursive: bool = True) -> List[Path]:
        """
        Récupère tous les fichiers d'images dans un dossier
        
        Args:
            directory: Dossier à scanner
            recursive: Scanner récursivement les sous-dossiers
        
        Returns:
            List[Path]: Liste des chemins vers les images
        """
        image_files = []
        
        if not directory.exists():
            logger.warning(f"Le dossier n'existe pas: {directory}")
            return image_files
        
        # Définir le pattern de recherche
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"
        
        # Scanner les fichiers
        for file_path in directory.glob(pattern):
            if file_path.is_file() and self._is_image_file(file_path):
                image_files.append(file_path)
        
        # Trier par nom de fichier
        image_files.sort(key=lambda x: x.name.lower())
        
        logger.info(f"Trouvé {len(image_files)} images dans {directory}")
        return image_files
    
    def _is_image_file(self, file_path: Path) -> bool:
        """
        Vérifie si un fichier est une image supportée
        
        Args:
            file_path: Chemin vers le fichier
        
        Returns:
            bool: True si c'est une image supportée
        """
        extension = file_path.suffix.lower()
        return extension in self.supported_extensions
    
    def get_directory_structure(self, directory: Path) -> dict:
        """
        Analyse la structure d'un dossier pour comprendre l'organisation des produits
        
        Args:
            directory: Dossier à analyser
        
        Returns:
            dict: Structure du dossier avec informations sur les produits
        """
        structure = {
            'root': directory,
            'products': {},
            'total_images': 0,
            'subdirectories': []
        }
        
        if not directory.exists():
            return structure
        
        # Analyser les sous-dossiers
        for item in directory.iterdir():
            if item.is_dir():
                product_info = self._analyze_product_directory(item)
                if product_info:
                    structure['products'][item.name] = product_info
                    structure['total_images'] += product_info['image_count']
                structure['subdirectories'].append(item.name)
        
        return structure
    
    def _analyze_product_directory(self, product_dir: Path) -> Optional[dict]:
        """
        Analyse un dossier de produit
        
        Args:
            product_dir: Dossier du produit
        
        Returns:
            dict: Informations sur le produit
        """
        product_info = {
            'path': product_dir,
            'image_count': 0,
            'image_types': set(),
            'subdirectories': []
        }
        
        # Compter les images dans ce dossier
        images = self.get_image_files(product_dir, recursive=False)
        product_info['image_count'] = len(images)
        
        # Analyser les sous-dossiers
        for item in product_dir.iterdir():
            if item.is_dir():
                sub_images = self.get_image_files(item, recursive=False)
                if sub_images:
                    product_info['subdirectories'].append({
                        'name': item.name,
                        'path': item,
                        'image_count': len(sub_images)
                    })
                    product_info['image_count'] += len(sub_images)
        
        return product_info if product_info['image_count'] > 0 else None
    
    def create_output_structure(self, output_dir: Path, structure: dict) -> None:
        """
        Crée la structure de dossiers de sortie basée sur l'analyse
        
        Args:
            output_dir: Dossier de sortie principal
            structure: Structure analysée du dossier source
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Créer les sous-dossiers pour chaque produit
        for product_name, product_info in structure['products'].items():
            product_output_dir = output_dir / product_name
            product_output_dir.mkdir(exist_ok=True)
            
            # Créer les sous-dossiers pour les types d'images
            for subdir_info in product_info['subdirectories']:
                subdir_output = product_output_dir / subdir_info['name']
                subdir_output.mkdir(exist_ok=True)
        
        logger.info(f"Structure de sortie créée: {output_dir}")
    
    def get_file_size_mb(self, file_path: Path) -> float:
        """
        Récupère la taille d'un fichier en MB
        
        Args:
            file_path: Chemin vers le fichier
        
        Returns:
            float: Taille en MB
        """
        try:
            return file_path.stat().st_size / (1024 * 1024)
        except OSError:
            return 0.0
    
    def get_directory_size_mb(self, directory: Path) -> float:
        """
        Calcule la taille totale d'un dossier en MB
        
        Args:
            directory: Dossier à analyser
        
        Returns:
            float: Taille totale en MB
        """
        total_size = 0.0
        
        try:
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    total_size += self.get_file_size_mb(file_path)
        except OSError as e:
            logger.warning(f"Erreur lors du calcul de la taille de {directory}: {e}")
        
        return total_size
    
    def validate_output_directory(self, output_dir: Path) -> bool:
        """
        Valide qu'un dossier de sortie peut être utilisé
        
        Args:
            output_dir: Dossier de sortie à valider
        
        Returns:
            bool: True si le dossier est valide
        """
        try:
            # Vérifier si le dossier existe
            if output_dir.exists():
                # Vérifier les permissions d'écriture
                test_file = output_dir / '.test_write'
                test_file.touch()
                test_file.unlink()
                return True
            else:
                # Essayer de créer le dossier
                output_dir.mkdir(parents=True, exist_ok=True)
                return True
        except (OSError, PermissionError) as e:
            logger.error(f"Erreur de validation du dossier de sortie {output_dir}: {e}")
            return False 