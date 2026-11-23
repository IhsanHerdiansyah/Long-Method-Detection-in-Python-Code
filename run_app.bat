@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\streamlit.exe" (
    echo Dependencies belum tersedia. Menyiapkan virtual environment...
    python -m venv .venv
    if errorlevel 1 goto :error
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto :error
)

".venv\Scripts\streamlit.exe" run app.py
goto :eof

:error
echo.
echo Penyiapan aplikasi gagal. Periksa koneksi internet dan versi Python.
pause

