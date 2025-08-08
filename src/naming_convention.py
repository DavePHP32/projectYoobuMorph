"""
Module de convention de nommage pour YoobuMorph
==============================================

Ce module gère la génération de noms de fichiers selon la convention e-commerce:
<NOM PRODUIT> + Chaine alphanumérique 7 + SLY + Largeur

Exemple: sigg - gourde isotherme_obisidian_1AGH457_SLY_500.jpg

Le NOM_PRODUIT est la concaténation des noms de dossiers du produit.
Le dossier de sortie est le nom du dossier source suivi de _outputs.
"""

import re
import random
import string
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class NamingConvention:
    """Classe pour la génération de noms de fichiers selon la convention e-commerce"""
    
    def __init__(self):
        # Caractères autorisés pour la chaîne alphanumérique
        self.alphanumeric_chars = string.ascii_uppercase + string.digits
        
        # Cache pour éviter les doublons
        self.generated_ids = set()
    
    def generate_filename_and_output_dir(self, image_path: Path, source_dir: Path, 
                                       target_width: int = 750) -> Tuple[str, str]:
        """
        Génère un nom de fichier et le dossier de sortie selon la convention e-commerce
        
        Args:
            image_path: Chemin vers l'image source
            source_dir: Dossier source principal
            target_width: Largeur cible pour le suffixe
        
        Returns:
            Tuple[str, str]: (nom_fichier, dossier_sortie)
        """
        try:
            # Extraction du nom du produit depuis la structure des dossiers
            product_name = self._extract_product_name_from_path(image_path, source_dir)
            
            # Génération de la chaîne alphanumérique unique de 7 caractères
            alphanumeric_id = self._generate_unique_id()
            
            # Construction du nom de fichier
            filename = f"{product_name}_{alphanumeric_id}_SLY_{target_width}.jpg"
            
            # Nettoyage du nom de fichier
            filename = self._clean_filename(filename)
            
            # Génération du nom du dossier de sortie
            output_dir = self._generate_output_dir_name(source_dir)
            
            logger.info(f"Nom généré: {filename}")
            logger.info(f"Dossier de sortie: {output_dir}")
            
            return filename, output_dir
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du nom pour {image_path}: {e}")
            fallback_id = self._generate_unique_id()
            fallback_filename = f"image_{fallback_id}_SLY_{target_width}.jpg"
            fallback_output_dir = f"{source_dir.name}_outputs"
            return fallback_filename, fallback_output_dir
    
    def _extract_product_name_from_path(self, image_path: Path, source_dir: Path) -> str:
        """
        Extrait le nom du produit en concaténant les noms de dossiers
        
        Args:
            image_path: Chemin vers l'image
            source_dir: Dossier source principal
        
        Returns:
            str: Nom du produit normalisé (concaténation des dossiers)
        """
        try:
            # Calculer le chemin relatif depuis le dossier source
            relative_path = image_path.relative_to(source_dir)
            path_parts = relative_path.parts
            
            # Concaténer tous les dossiers du chemin
            if len(path_parts) > 1:
                # Prendre tous les dossiers sauf le dernier (qui est le nom du fichier)
                folder_parts = path_parts[:-1]
                product_name = '_'.join(folder_parts)
            else:
                # Si pas de sous-dossiers, utiliser le nom du dossier source
                product_name = source_dir.name
            
        except ValueError:
            # Si le chemin relatif ne peut pas être calculé
            product_name = source_dir.name
        
        # Normalisation du nom du produit
        product_name = self._normalize_product_name(product_name)
        
        return product_name
    
    def _generate_output_dir_name(self, source_dir: Path) -> str:
        """
        Génère le nom du dossier de sortie : nom_dossier_source + _outputs
        
        Args:
            source_dir: Dossier source principal
        
        Returns:
            str: Nom du dossier de sortie
        """
        return f"{source_dir.name}_outputs"
    
    def _normalize_product_name(self, product_name: str) -> str:
        """
        Normalise le nom du produit pour la convention de nommage
        
        Args:
            product_name: Nom du produit brut
        
        Returns:
            str: Nom du produit normalisé
        """
        # Convertir en minuscules
        normalized = product_name.lower()
        
        # Remplacement des caractères spéciaux par des underscores
        normalized = re.sub(r'[^a-z0-9\s-]', '_', normalized)
        
        # Remplacement des espaces par des underscores
        normalized = normalized.replace(' ', '_')
        
        # Remplacer les underscores multiples par un seul
        normalized = re.sub(r'_+', '_', normalized)
        
        # Supprimer les underscores en début et fin
        normalized = normalized.strip('_')
        
        # Limitation de la longueur
        if len(normalized) > 50:
            normalized = normalized[:50]
        
        return normalized
    
    def _generate_unique_id(self, length: int = 7) -> str:
        """
        Génère une chaîne alphanumérique unique
        
        Args:
            length: Longueur de la chaîne
        
        Returns:
            str: Chaîne alphanumérique unique
        """
        max_attempts = 1000
        attempts = 0
        
        while attempts < max_attempts:
            # Générer une chaîne alphanumérique
            unique_id = ''.join(random.choices(self.alphanumeric_chars, k=length))
            
            # Vérifier qu'elle n'existe pas déjà
            if unique_id not in self.generated_ids:
                self.generated_ids.add(unique_id)
                return unique_id
            
            attempts += 1
        
        # Si on n'arrive pas à générer un ID unique, utiliser un timestamp
        import time
        timestamp = int(time.time() * 1000) % (10 ** length)
        return f"{timestamp:0{length}d}"
    
    def _clean_filename(self, filename: str) -> str:
        """
        Nettoie un nom de fichier pour qu'il soit compatible avec le système de fichiers
        
        Args:
            filename: Nom de fichier à nettoyer
        
        Returns:
            str: Nom de fichier nettoyé
        """
        # Remplacer les caractères non autorisés
        cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remplacer les underscores multiples par un seul underscore
        cleaned = re.sub(r'_+', '_', cleaned)
        
        # Supprimer les underscores en début et fin
        cleaned = cleaned.strip('_')
        
        # Limiter la longueur totale
        if len(cleaned) > 200:
            # Garder l'extension
            name_part, ext_part = cleaned.rsplit('.', 1)
            max_name_length = 200 - len(ext_part) - 1
            cleaned = name_part[:max_name_length] + '.' + ext_part
        
        return cleaned
    
    def parse_filename(self, filename: str) -> dict:
        """
        Parse un nom de fichier selon la convention e-commerce
        
        Args:
            filename: Nom de fichier à parser
        
        Returns:
            dict: Informations extraites du nom de fichier
        """
        # Pattern pour parser le nom de fichier
        pattern = r'^(.+)_([A-Z0-9]{7})_SLY_(\d+)\.(.+)$'
        match = re.match(pattern, filename)
        
        if match:
            return {
                'product_name': match.group(1),
                'unique_id': match.group(2),
                'width': int(match.group(3)),
                'extension': match.group(4)
            }
        else:
            return {
                'product_name': 'unknown',
                'unique_id': 'unknown',
                'width': 0,
                'extension': 'unknown'
            }
    
    def validate_filename(self, filename: str) -> bool:
        """
        Valide qu'un nom de fichier respecte la convention
        
        Args:
            filename: Nom de fichier à valider
        
        Returns:
            bool: True si le nom respecte la convention
        """
        pattern = r'^[a-z0-9_-]+_[A-Z0-9]{7}_SLY_\d+\.(jpg|jpeg|png|webp)$'
        return bool(re.match(pattern, filename))
    
    def get_filename_components(self, image_path: Path, source_dir: Path) -> dict:
        """
        Récupère tous les composants pour générer un nom de fichier
        
        Args:
            image_path: Chemin vers l'image
            source_dir: Dossier source principal
        
        Returns:
            dict: Composants du nom de fichier
        """
        return {
            'product_name': self._extract_product_name_from_path(image_path, source_dir),
            'unique_id': self._generate_unique_id(),
            'target_width': 750  # Valeur par défaut
        } 