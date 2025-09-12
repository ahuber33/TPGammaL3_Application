#!/bin/bash
# ---------------------------------------------------
# Installateur portable TPGammaL3_App Linux / WSL
# Optimisé pour WSLg et Linux natif
# ---------------------------------------------------

SOURCE_DIR="$(pwd)"
echo "Source des fichiers : $SOURCE_DIR"

# Chemin d'installation
read -p "Entrez le chemin d'installation (ex : /mnt/d/Simulation/TPGammaL3_App) : " INSTALL_DIR
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/Resultats"

# Copie des fichiers essentiels
echo "Copie des fichiers..."
cp -r "$SOURCE_DIR/bundle" "$INSTALL_DIR/"
cp -r "$SOURCE_DIR/app" "$INSTALL_DIR/"
cp "$SOURCE_DIR/vis.mac" "$INSTALL_DIR/" 2>/dev/null || true
cp "$SOURCE_DIR/main.py" "$INSTALL_DIR/" 2>/dev/null || true
cp "$SOURCE_DIR/monicone.ico" "$INSTALL_DIR/" 2>/dev/null || true
echo "Fichiers copiés avec succès."

# Détection plateforme
OS_TYPE="$(uname -s)"
IS_WSL=0
if grep -qi microsoft /proc/version 2>/dev/null; then
    IS_WSL=1
    OS_TYPE="WSL"
fi
echo "Plateforme détectée : $OS_TYPE"

# Installation des bibliothèques système Qt/XCB nécessaires (Linux natif uniquement)
if [[ "$IS_WSL" -eq 0 ]]; then
    echo "Vérification des bibliothèques système Qt..."
    sudo apt update
    sudo apt install -y libx11-xcb1 libxcb1 libxcb-xinerama0 libxcb-cursor0 \
    libxrender1 libxext6 libxfixes3 libxcomposite1 libxi6 libxrandr2 libglib2.0-0
fi

# Création du virtualenv
echo "Création de l'environnement Python virtuel..."
python3 -m venv "$INSTALL_DIR/venv"

# Installation des dépendances Python
source "$INSTALL_DIR/venv/bin/activate"
pip install --upgrade pip
pip install PySide6 numpy scipy matplotlib pandas uproot
deactivate
echo "Environnement virtuel prêt avec PySide6 et numpy."

# Script portable de lancement
LAUNCHER="$INSTALL_DIR/run_tpgamma.sh"
cat > "$LAUNCHER" <<'EOL'
#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"

# Activation du venv
source "$DIR/venv/bin/activate"

# Forcer le venv à utiliser ses propres bibliothèques Qt
PYTHON_VERSION=$(python -c "import sys; print('python{}.{}'.format(sys.version_info[0], sys.version_info[1]))")
export LD_LIBRARY_PATH="$DIR/venv/lib/$PYTHON_VERSION/site-packages/PySide6/Qt/lib:$LD_LIBRARY_PATH"

# Lancement de l'application
python "$DIR/app/main.py" "$@"
EOL
chmod +x "$LAUNCHER"
echo "Script de lancement créé : $LAUNCHER"

# Option raccourci bureau
echo "Voulez-vous créer :"
echo "1) Raccourci bureau"
echo "2) Script terminal"
echo "3) Les deux"
read -p "Entrez votre choix (1/2/3) : " CHOICE

if [[ $CHOICE -eq 1 || $CHOICE -eq 3 ]]; then
    if [ -d "$HOME/Desktop" ]; then
        DESKTOP_FILE="$HOME/Desktop/TPGammaL3_App.desktop"
        cat > "$DESKTOP_FILE" <<EOL
[Desktop Entry]
Name=TPGammaL3_App
Comment=Lancer TPGammaL3_App
Exec=$LAUNCHER
Icon=$INSTALL_DIR/monicone.ico
Terminal=true
Type=Application
Categories=Education;Science;
EOL
        chmod +x "$DESKTOP_FILE"
        echo "Raccourci bureau créé : $DESKTOP_FILE"
    else
        echo "Bureau non détecté. Impossible de créer le raccourci."
    fi
fi

echo "Installation terminée !"
echo "Vous pouvez lancer l'application via le script ou le raccourci."
