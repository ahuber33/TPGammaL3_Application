TPGammaL3_App
=============

TPGammaL3_App est une application scientifique pour la simulation et l’analyse de données, développée dans le cadre d’un projet L3.
Elle utilise Python 3, PySide6 pour l’interface graphique et les bibliothèques scientifiques NumPy, SciPy, Matplotlib et Pandas.

Prérequis
---------

Linux natif :
- Python 3.12
- Bibliothèques système Qt/XCB :
  sudo apt update
  sudo apt install -y libx11-xcb1 libxcb1 libxcb-xinerama0 libxcb-cursor0 \
    libxrender1 libxext6 libxfixes3 libxcomposite1 libxi6 libxrandr2 libglib2.0-0

WSL 2 (Windows 11/10) :
- VSCode avec extension Remote - WSL et WSLg recommandé
- Si WSL sans WSLg : serveur X externe (VcXsrv) nécessaire

Windows :
- Conda ou venv avec Python 3.12
- PySide6 et dépendances scientifiques installées

Installation
------------

### Linux / WSL

1. Ouvrir un terminal dans le dossier contenant `install_tpgamma.sh`
2. Lancer le script :
   ./install_tpgamma.sh
3. Suivre les instructions pour choisir le dossier d’installation et créer un raccourci bureau.

Le script effectue automatiquement :
- Installation des bibliothèques système Qt/XCB
- Création d’un virtualenv Python
- Installation des dépendances Python : PySide6, numpy, scipy, matplotlib, pandas
- Création du script de lancement `run_tpgamma.sh` avec détection de WSL et configuration Qt

### Windows

1. Installer Anaconda / Miniconda si nécessaire
2. Créer un environnement Conda dédié :
   conda create -n tpgamma python=3.12 pyside6=6.9 numpy scipy matplotlib pandas
   conda activate tpgamma
3. Copier le dossier de l’application où souhaité
4. Lancer l’application via :
   python app\main.py

Lancement de l’application
-------------------------

Linux / WSL :
./run_tpgamma.sh
- Active automatiquement le virtualenv
- Configure les bibliothèques Qt pour PySide6
- Pour WSL avec WSLg : pas besoin de serveur X externe
- Pour WSL sans WSLg : lancer un serveur X (VcXsrv) avant de lancer le script

Windows :
- Depuis un terminal Conda activé :
  python app\main.py

Raccourcis
----------

- L’installateur peut créer un raccourci bureau Linux/WSL (.desktop)
- Pour Windows, lancement via terminal Conda ou script `.bat`

Désinstallation
---------------

Supprimer l’application et le virtualenv associé :
rm -rf /chemin/vers/TPGammaL3_App

Support & dépannage
------------------

- WSL + VSCode + WSLg : lancer directement `./run_tpgamma.sh` depuis le terminal VSCode
- WSL sans WSLg : installer et lancer un serveur X externe (VcXsrv)
- Linux natif : vérifier que les bibliothèques Qt/XCB sont installées
- Si un module Python est manquant :
  source /chemin/vers/venv/bin/activate
  pip install <module>

Fonctionnalités principales
--------------------------

- Interface graphique interactive avec PySide6
- Exploration et manipulation de données scientifiques
- Visualisation avec Matplotlib
- Calculs numériques et statistiques avec NumPy et SciPy
- Gestion de fichiers et résultats scientifiques via le dossier `Resultats`

Notes spécifiques WSL + VSCode
-------------------------------

- Préférez WSL 2 avec WSLg pour éviter tout problème de serveur X
- Si WSLg n’est pas disponible, le script d’installation vous demandera de lancer VcXsrv
- Le script détecte automatiquement la présence de WSL et configure `DISPLAY` pour Qt

Licence
-------

-

Auteur
------

Arnaud HUBER
TPGammaL3_App – Projet L3
