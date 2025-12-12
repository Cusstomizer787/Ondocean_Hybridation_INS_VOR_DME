@echo off
REM Script de lancement rapide des tests de validation
REM Etapes 15-20 du plan de correction

echo ======================================================================
echo VALIDATION SCENARIOS CORRIGES - INS + VOR/DME
echo ======================================================================
echo.

cd /d "%~dp0"

echo Verification environnement Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH
    echo.
    echo Installer Python depuis: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python detecte
echo.

echo Verification dependances...
python -c "import numpy, scipy, matplotlib" >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Dependances manquantes
    echo.
    echo Installation des dependances...
    pip install numpy scipy matplotlib
    if errorlevel 1 (
        echo [ERREUR] Echec installation dependances
        pause
        exit /b 1
    )
)

echo [OK] Dependances presentes
echo.

echo ======================================================================
echo EXECUTION TESTS DE VALIDATION
echo ======================================================================
echo.
echo Duree estimee: 2-5 minutes
echo.

python test_scenarios.py

if errorlevel 1 (
    echo.
    echo [ERREUR] Les tests ont echoue
    echo Consulter les messages ci-dessus pour diagnostiquer le probleme
    echo.
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo TESTS TERMINES
echo ======================================================================
echo.
echo Resultats sauvegardes dans: resultats_tests_scenarios.json
echo.
echo Pour executer le notebook complet:
echo   1. Ouvrir simulation_ins_vor_dme.ipynb
echo   2. Modifier numero_scenario (cellule 6)
echo   3. Executer toutes les cellules
echo.

pause
