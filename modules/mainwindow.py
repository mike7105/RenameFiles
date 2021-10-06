"""Главное окно приложения"""
import os

from PyQt5 import QtCore, QtWidgets, QtWinExtras

from modules.MyWindow import MyWindow


class MainWindow(QtWidgets.QMainWindow):
    """
    Главное окно
    """

    def __init__(self, version, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.version = version
        self.setWindowTitle("Rename Files")

        # Создаем кнопку панели задач
        self.taskbarButton = QtWinExtras.QWinTaskbarButton(parent=self)
        # Получаем индикатор процесса, задаем его параметры
        # и делаем его видимым
        self.progress = self.taskbarButton.progress()
        self.progress.setMaximum(0)
        self.progress.show()

        self.dtGeo = QtWidgets.QApplication.desktop().availableGeometry()
        self.setMinimumSize(600, 600)
        self.resize(self.dtGeo.width()//2, self.dtGeo.height()-30)
        # self.showMaximized()
        self.move(self.dtGeo.width()//2, 0)

        QtCore.QCoreApplication.setOrganizationName("Mihail Chesnokov")
        QtCore.QCoreApplication.setApplicationName("renameFiles")
        self.settings = QtCore.QSettings()

        self.mywindow = MyWindow(self)
        self.setCentralWidget(self.mywindow)

        self.menuBar = self.menuBar()
        # toolBar = QtWidgets.QToolBar()

        self.myMenuFile = self.menuBar.addMenu("&File")

        self.myMenuFile.addSeparator()

        action = self.myMenuFile.addAction("&Quit", self.quitApp, QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        action.setStatusTip("Quit program")

        self.myMenuAbout = self.menuBar.addMenu("&About")

        action = self.myMenuAbout.addAction("About...", self.aboutInfo)
        action.setStatusTip("Get info about program")

        action = self.myMenuAbout.addAction("about &Qt...", QtWidgets.qApp.aboutQt)
        action.setStatusTip("Get info about Qt")

        self.restoreSettings()

    def closeEvent(self, evt):
        """
        событие при закрытии приложения
        :param evt: событие
        """
        self.saveSettings()

    def saveSettings(self):
        """
        Сохраняет настройки
        """
        self.settings.beginGroup("Window")
        self.settings.setValue("Geometry", self.geometry())
        self.settings.endGroup()

        self.settings.beginGroup("Data")
        self.settings.setValue("lePathImg", self.mywindow.lePathImg.text())
        self.settings.setValue("leExt", self.mywindow.leExt.text())
        self.settings.setValue("gbRegEx", int(self.mywindow.gbRegEx.isChecked()))
        self.settings.setValue("leFind", self.mywindow.leFind.text())
        self.settings.setValue("leReplace", self.mywindow.leReplace.text())
        self.settings.setValue("gbSep", int(self.mywindow.gbSep.isChecked()))
        self.settings.setValue("leSep", self.mywindow.leSep.text())
        self.settings.endGroup()

    def restoreSettings(self):
        """
        Восстанавливает сохраненные настройки
        """
        if self.settings.contains("Window/Geometry"):
            self.setGeometry(self.settings.value("Window/Geometry"))
        if self.settings.contains("Data/lePathImg"):
            if os.path.exists(self.settings.value("Data/lePathImg")):
                self.mywindow.lePathImg.setText(self.settings.value("Data/lePathImg"))
        if self.settings.contains("Data/leExt"):
            self.mywindow.leExt.setText(self.settings.value("Data/leExt"))
        if self.settings.contains("Data/gbRegEx"):
            self.mywindow.gbRegEx.setChecked(bool(self.settings.value("Data/gbRegEx")))
            if self.settings.value("Data/gbRegEx"):
                if self.settings.contains("Data/leFind"):
                    self.mywindow.leFind.setText(self.settings.value("Data/leFind"))
                if self.settings.contains("Data/leReplace"):
                    self.mywindow.leReplace.setText(self.settings.value("Data/leReplace"))
        if self.settings.contains("Data/gbSep"):
            self.mywindow.gbSep.setChecked(bool(self.settings.value("Data/gbSep")))
            if self.settings.value("Data/gbSep"):
                if self.settings.contains("Data/leSep"):
                    self.mywindow.leSep.setText(self.settings.value("Data/leSep"))

    def quitApp(self):
        """
        ЗАкрывает приложение
        """
        self.saveSettings()
        QtWidgets.qApp.quit()

    def aboutInfo(self):
        """
        Показывает описание программы
        """
        QtWidgets.QMessageBox.about(self, "About program",
                                    f"<center>\"renameFiles\" {self.version}<br><br>"
                                    f"Rename files for current folder<br><br> "
                                    f"(c) Mihail Chesnokov 2021")

    def showEvent(self, evt):
        """
        событие при показе окна на экране
        :param evt:
        """
        self.taskbarButton.setWindow(self.windowHandle())
