"""Rename files for current folder
Mihail Chesnokov 04.10.2021"""
__version__ = 'Version:1.0'

import os
import sys
from PyQt5 import QtGui, QtWidgets

from modules.mainwindow import MainWindow


def resource_path(relative_path: str) -> str:
    """ Get absolute path to resource, works for dev and for PyInstaller

    :param relative_path: относительный путь к файлу
    :return: реальный путь для теста и прода
    """
    if getattr(sys, 'frozen', False):
        # noinspection PyUnresolvedReferences,PyProtectedMember
        base_path = sys._MEIPASS
    else:
        base_path = os.getcwd()
    return os.path.join(base_path, relative_path)


try:
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(resource_path(r"modules\ico\ico256.png")))
    window = MainWindow(__version__)
    window.show()
    sys.exit(app.exec_())
except Exception as ex:
    print(ex)
    input()
