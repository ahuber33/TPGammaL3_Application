@echo off
REM ---------------------------------------------------
REM Désinstallateur TPGammaL3_App Windows
REM ---------------------------------------------------

SET /P INSTALL_DIR=Entrez le chemin d'installation de TPGammaL3_App :

IF EXIST "%INSTALL_DIR%" (
    echo Suppression du dossier d'installation : %INSTALL_DIR%
    rmdir /S /Q "%INSTALL_DIR%"
) ELSE (
    echo Le dossier %INSTALL_DIR% n'existe pas.
)

REM Suppression du raccourci bureau si existant
SET DESKTOP_FILE=%USERPROFILE%\Desktop\TPGammaL3_App.lnk
IF EXIST "%DESKTOP_FILE%" (
    echo Suppression du raccourci bureau : %DESKTOP_FILE%
    del "%DESKTOP_FILE%"
)

echo Désinstallation terminée !
pause
