O:\Progs\Python\TestLink\venv\Scripts\activate
pyinstaller --onefile -w ^
--icon=modules\ico\ico.ico ^
--add-data "modules/ico";"modules/ico/" ^
--add-data "geckodriver.exe";"." ^
-n testLink_GUI.exe ^
--hidden-import selenium ^
--hidden-import PyQt5 ^
testLinkW.py
pause