# YoobuMorph - Traitement en Batch d'Images pour E-commerce

## 🎯 Description

YoobuMorph est un outil de traitement en batch d'images spécialement conçu pour les sites e-commerce. Il permet de carréifier automatiquement les images en gardant la dimension maximale et en ajoutant des bordures intelligentes selon la rectangularité de l'image.

## ✨ Fonctionnalités

- **Traitement en batch** : Traite automatiquement toutes les images d'un dossier
- **Carréification intelligente** : Détermine automatiquement la stratégie de carréification selon la rectangularité
- **Convention de nommage e-commerce** : Génère des noms de fichiers selon la règle `<NOM_PRODUIT>_<TYPE>_<ID>_SLY_<LARGEUR>.jpg`
- **Support multi-formats** : JPG, PNG, WebP, BMP, TIFF
- **Logging complet** : Suivi détaillé du traitement avec logs
- **Gestion d'erreurs robuste** : Continue le traitement même en cas d'erreur sur une image

## 🏗️ Architecture

```
YoobuMorph/
├── main.py                 # Point d'entrée principal
├── image_processor.py      # Traitement d'images et carréification
├── file_manager.py         # Gestion des fichiers et dossiers
├── naming_convention.py    # Convention de nommage e-commerce
├── requirements.txt        # Dépendances Python
└── README.md             # Documentation
```

## 🚀 Installation

1. **Cloner le projet** :
```bash
git clone <repository-url>
cd YoobuMorph
```

2. **Installer les dépendances** :
```bash
pip install -r requirements.txt
```

## 📖 Utilisation

### Utilisation de base

```bash
python main.py <dossier_source> <dossier_sortie>
```

### Exemples d'utilisation

```bash
# Traitement avec paramètres par défaut (750x750, fond blanc)
python main.py "images_source" "images_traitees"

# Traitement avec taille personnalisée
python main.py "images_source" "images_traitees" --size 500 500

# Traitement avec couleur de fond personnalisée
python main.py "images_source" "images_traitees" --bg-color 240 240 240
```

### Paramètres disponibles

- `source_dir` : Dossier source contenant les images à traiter
- `output_dir` : Dossier de sortie pour les images traitées
- `--size, -s` : Taille cible pour les images carrées (largeur hauteur). Défaut: 750 750
- `--bg-color, -b` : Couleur de fond pour les bordures (R G B). Défaut: 255 255 255

## 🎨 Stratégies de Carréification

### Image Horizontale (750x50 → 750x750)
```
****************
****************
    *******
    *******
    *******
****************
****************
```
*Bordures ajoutées en haut et en bas*

### Image Verticale (50x750 → 750x750)
```
**  ********  **
**  ********  **
**  ********  **
**  ********  **
**  ********  **
```
*Bordures ajoutées à gauche et à droite*

### Image Carrée (50x50 → 750x750)
```
****************
****************
****************
****************
```
*Redimensionnement direct*

## 📝 Convention de Nommage

Le programme génère automatiquement des noms de fichiers selon la convention e-commerce :

```
<NOM_PRODUIT>_<TYPE>_<ID_ALPHANUMERIQUE>_SLY_<LARGEUR>.jpg
```

### Exemples :
- `sigg-gourde-isotherme_obsidian_1AGH457_SLY_750.jpg`
- `sigg-gourde-isotherme_selenite_2BKL789_SLY_750.jpg`
- `sigg-gourde-isotherme_description_3CMN123_SLY_750.jpg`

### Composants :
- **NOM_PRODUIT** : Extrait automatiquement depuis la structure des dossiers
- **TYPE** : Déterminé selon le sous-dossier (obsidian, selenite, description, etc.)
- **ID_ALPHANUMERIQUE** : Chaîne unique de 7 caractères (A-Z, 0-9)
- **SLY** : Suffixe fixe pour identifier les images traitées
- **LARGEUR** : Largeur cible de l'image (par défaut 750)

## 📁 Structure des Dossiers

Le programme analyse automatiquement la structure des dossiers pour extraire les informations :

```
SIGG-Gourde_Isotherme_reference_pour_YoobuMorph/
└── SIGG - Gourde Isotherme/
    ├── Description/
    │   ├── image1.jpg
    │   └── image2.jpg
    ├── Obsidian/
    │   ├── 05/
    │   │   ├── 05.jpg
    │   │   └── gal_05.jpg
    │   └── 075/
    │       └── 61B7SGi3YPL._AC_SL1500_.jpg
    └── Selenite/
        ├── 05/
        │   ├── 05.jpg
        │   └── gal_05.jpg
        └── 075/
            └── 61Ej9HjdJmL._AC_SL1500_.jpg
```

## 🔧 Configuration

### Formats d'images supportés
- JPG/JPEG
- PNG
- WebP
- BMP
- TIFF/TIF

### Paramètres de qualité
- Qualité JPEG : 95%
- Optimisation : Activée
- Redimensionnement : LANCZOS (haute qualité)

## 📊 Logging

Le programme génère des logs détaillés :

- **Fichier de log** : `yoobumorph.log`
- **Console** : Affichage en temps réel
- **Niveaux** : INFO, WARNING, ERROR

### Exemple de log :
```
2024-01-15 10:30:15 - INFO - Début du traitement en batch
2024-01-15 10:30:15 - INFO - Dossier source: images_source
2024-01-15 10:30:15 - INFO - Dossier de sortie: images_traitees
2024-01-15 10:30:15 - INFO - Taille cible: (750, 750)
2024-01-15 10:30:15 - INFO - Nombre d'images à traiter: 25
2024-01-15 10:30:16 - INFO - Traitement de: image1.jpg
2024-01-15 10:30:16 - INFO - Image originale: 1200x800
2024-01-15 10:30:16 - INFO - Stratégie: Image horizontale - bordures haut/bas
2024-01-15 10:30:16 - INFO - ✓ Traité: sigg-gourde-isotherme_obsidian_1AGH457_SLY_750.jpg
```

## 🛠️ Développement

### Structure des modules

#### `main.py`
- Point d'entrée principal
- Parsing des arguments en ligne de commande
- Orchestration du traitement en batch

#### `image_processor.py`
- Traitement d'images avec PIL
- Logique de carréification intelligente
- Validation des images

#### `file_manager.py`
- Découverte des fichiers d'images
- Analyse de la structure des dossiers
- Validation des dossiers de sortie

#### `naming_convention.py`
- Génération de noms de fichiers selon la convention e-commerce
- Extraction des informations depuis la structure des dossiers
- Validation des noms de fichiers

### Tests

Pour tester le programme avec vos propres images :

```bash
# Créer un dossier de test
mkdir test_images
mkdir test_output

# Copier quelques images dans test_images
# Puis lancer le traitement
python main.py test_images test_output
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

Pour toute question ou problème :

1. Vérifier les logs dans `yoobumorph.log`
2. Consulter la documentation ci-dessus
3. Ouvrir une issue sur GitHub

## 🔄 Versions

- **v1.0.0** : Version initiale avec traitement en batch et carréification intelligente 