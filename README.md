# Projet CR : Solveur de Picross

## Présentation du Projet

Ce projet explore l’application des solveurs SAT et des problèmes de satisfaction de contraintes (CSP) pour résoudre des puzzles logiques, en particulier les **nonogrammes** (également appelés Picross ou Hanjie). L’objectif est de développer un **solveur automatisé** capable de déterminer si un nonogramme donné (2D et 3D) a une solution et, le cas échéant, de trouver cette solution efficacement.

## Structure du Projet

- **main.ipynb** : Ce notebook Jupyter présente le projet en détail, explique les concepts de base et montre comment les solveurs SAT sont utilisés pour résoudre les nonogrammes 2D et 3D.
- **picross2d** : Ce dossier contient le fichier `picross2d.py` qui implémente le solveur pour les nonogrammes 2D.
- **picross3d** : Ce dossier contient le fichier `picross3d.py` qui implémente le solveur pour les nonogrammes 3D.

## Installation des Dépendances

Pour installer les dépendances nécessaires à l'exécution de ce projet, utilisez le fichier `requirements.txt`. Vous pouvez installer les dépendances en utilisant la commande suivante :

```bash
pip install -r requirements.txt
```

## Solveur de Nonogrammes 2D

Pour résoudre un nonogramme 2D, exécutez le script picross2d.py avec le fichier d'indices en argument :

```bash
python picross2d/picross2d.py --input_filename <nom_du_fichier_d_indices>
```

## Solveur de Nonogrammes 3D

Pour résoudre un nonogramme 3D, exécutez le script picross3d.py avec le fichier du puzzle en argument :

```bash
python picross3d/picross3d.py <nom_du_fichier_du_puzzle>
```
