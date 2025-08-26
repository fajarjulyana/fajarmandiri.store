@echo off
setlocal enabledelayedexpansion

cd /d "C:\Users\FJ-PC\Downloads\fajarmandiristore\templates\wedding_templates"

for %%f in (*.*) do (
    set "oldname=%%f"
    set "newname=!oldname:.backup_fix_universal=!"
    if not "!oldname!"=="!newname!" (
        echo Renaming "%%f" to "!newname!"
        ren "%%f" "!newname!"
    )
)

echo Selesai!
pause
