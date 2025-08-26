@echo off
setlocal enabledelayedexpansion

REM Ganti ke folder tempat file berada
cd /d "C:\Users\FJ-PC\Downloads\fajarmandiristore\templates\wedding_templates"

for %%f in (*.*) do (
    set "fname=%%~nf"
    set "ext=%%~xf"
    REM Cek apakah nama file berakhir dengan .backup_fix_universal
    echo !fname! | findstr /i ".*\.backup_fix_universal$" >nul
    if not errorlevel 1 (
        set "newname=!fname:.backup_fix_universal=!!ext!"
        echo Renaming "%%f" to "!newname!"
        ren "%%f" "!newname!"
    )
)

echo Selesai!
pause
