@echo off
setlocal
cd /d "%~dp0"
echo.
echo ================================================
echo   OptiDecarb v1.1.1 - local Streamlit launcher
echo ================================================
echo.
where py >nul 2>nul
if %errorlevel%==0 (
  set PY=py
) else (
  set PY=python
)
%PY% --version || goto :python_error
if not exist ".venv\Scripts\python.exe" (
  echo Creating local virtual environment...
  %PY% -m venv .venv || goto :install_error
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -e ".[app]" || goto :install_error
echo.
echo Opening OptiDecarb at http://localhost:8501
echo Close this window to stop the app.
echo.
python -m streamlit run app.py
exit /b 0

:python_error
echo.
echo Python was not found. Install Python 3.11+ from https://www.python.org/downloads/
echo During installation, enable "Add Python to PATH".
pause
exit /b 1

:install_error
echo.
echo Dependency installation failed. Check your internet connection and Python installation.
pause
exit /b 1
