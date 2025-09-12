@echo off
REM ---------------------------------------------------
REM Installateur portable TPGammaL3_App Windows
REM ---------------------------------------------------

SET SOURCE_DIR=%CD%
echo Source des fichiers : %SOURCE_DIR%

SET /P INSTALL_DIR=Entrez le chemin d'installation (ex : C:\Users\User\TPGammaL3_App) :

REM Création dossiers
mkdir "%INSTALL_DIR%"
mkdir "%INSTALL_DIR%\Resultats"

REM Copie fichiers
xcopy /E /I "%SOURCE_DIR%\bundle" "%INSTALL_DIR%\bundle"
xcopy /E /I "%SOURCE_DIR%\app" "%INSTALL_DIR%\app"
copy "%SOURCE_DIR%\vis.mac" "%INSTALL_DIR%" >nul 2>nul
copy "%SOURCE_DIR%\monicone.ico" "%INSTALL_DIR%" >nul 2>nul
copy "%SOURCE_DIR%\main.py" "%INSTALL_DIR%" >nul 2>nul
echo Fichiers copiés avec succès.

REM Création venv
python -m venv "%INSTALL_DIR%\venv"
call "%INSTALL_DIR%\venv\Scripts\activate.bat"
pip install --upgrade pip
pip install PySide6 pyinstaller
deactivate
echo Venv prêt avec PySide6 et PyInstaller.

REM Création script lancement
SET LAUNCHER="%INSTALL_DIR%\run_tpgamma.bat"
(
echo @echo off
echo REM Lancement TPGammaL3_App
echo "%INSTALL_DIR%\app\dist\TPGammaL3App.exe" %%*
) > %LAUNCHER%
echo Script de lancement Windows créé : %LAUNCHER%

echo Installation terminée ! Vous pouvez lancer l'application via le script.
pause
