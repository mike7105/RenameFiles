O:\Progs\Python\RenameFiles\venv\Scripts\activate
pyinstaller --onefile -w ^
--icon=modules\ico\ico.ico ^
--add-data "modules/ico";"modules/ico/" ^
-n renameFiles.exe ^
--hidden-import PyQt5 ^
renameFiles.py
pause