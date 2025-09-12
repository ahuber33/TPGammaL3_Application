#!/bin/bash
# ---------------------------------------------------
# Désinstallateur TPGammaL3_App Linux / WSL
# ---------------------------------------------------

# Chemin d'installation à supprimer
read -p "Entrez le chemin d'installation de TPGammaL3_App : " INSTALL_DIR

if [ -d "$INSTALL_DIR" ]; then
    echo "Suppression du dossier d'installation : $INSTALL_DIR"
    rm -rf "$INSTALL_DIR"
else
    echo "Le dossier $INSTALL_DIR n'existe pas."
fi

# Suppression du raccourci bureau si existant
DESKTOP_FILE="$HOME/Desktop/TPGammaL3_App.desktop"
if [ -f "$DESKTOP_FILE" ]; then
    echo "Suppression du raccourci bureau : $DESKTOP_FILE"
    rm "$DESKTOP_FILE"
fi

echo "Désinstallation terminée !"
