"""Основной компонент приложения"""
import os
import re
import time
import glob
import shutil

from PyQt5 import QtCore, QtWidgets, QtGui

class ClickedLabel(QtWidgets.QLabel):
    """Кдикабельная по двойному нажатию Label"""
    doubleclicked = QtCore.pyqtSignal()

    def mouseDoubleClickEvent(self, event):
        """
        Событие двойногонажатия
        :param event: событие
        """
        super().mouseDoubleClickEvent(event)

        self.doubleclicked.emit()

class MyStandardItemModel(QtGui.QStandardItemModel):
    """
    Класс, поддерживающий подкраску ячейки
    """
    _colorize = False

    def __init__(self, parent=None):
        super(MyStandardItemModel, self).__init__(parent)

    def setColorized(self, state):
        """
        Подкрашивать или нет
        :param bool state: True or False
        """
        self._colorize = state

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """
        апдейтит данные
        :param index: индекс
        :param role: роль
        :return:
        """
        if role == QtCore.Qt.BackgroundColorRole and not self._colorize:
            return QtGui.QBrush()

        return super(MyStandardItemModel, self).data(index, role)

# noinspection PyAttributeOutsideInit
class MyWindow(QtWidgets.QWidget):
    """
    Класс приложения
    """

    def __init__(self, parent=None):

        QtWidgets.QWidget.__init__(self, parent)
        self.statusBar: QtWidgets.QStatusBar = parent.statusBar()

        self.vbox = QtWidgets.QVBoxLayout()

        # блок для папки с результатом
        self.label1 = QtWidgets.QLabel("Current folder")
        self.vbox.addWidget(self.label1)
        self.hbox = QtWidgets.QHBoxLayout()
        self.lePathImg = QtWidgets.QLineEdit()
        self.lePathImg.setReadOnly(True)
        self.hbox.addWidget(self.lePathImg)
        self.btnPathImg = QtWidgets.QPushButton("...")
        self.btnPathImg.clicked.connect(self.on_open_result)
        self.btnPathImg.setToolTip("Press open folder for rename files")
        self.hbox.addWidget(self.btnPathImg)
        self.vbox.addLayout(self.hbox)

        # блок фильтрации
        self.hboxIDSet = QtWidgets.QHBoxLayout()
        self.hbox = QtWidgets.QHBoxLayout()
        self.gbFilters = QtWidgets.QGroupBox("Filters")
        self.label2 = QtWidgets.QLabel("Extensions:")
        self.label2.setToolTip("File extensions devided by | (ex. png|jpg|gif)")
        self.hbox.addWidget(self.label2)
        self.leExt = QtWidgets.QLineEdit()
        self.leExt.setText("")
        self.hbox.addWidget(self.leExt)
        self.gbFilters.setLayout(self.hbox)
        self.hboxIDSet.addWidget(self.gbFilters)

        # блок по регулярке
        self.hbox = QtWidgets.QHBoxLayout()
        self.gbRegEx = QtWidgets.QGroupBox("RegExp")
        self.gbRegEx.setCheckable(True)
        self.gbRegEx.toggled.connect(lambda flag: self.gbSep.setChecked(not flag) if flag else flag)
        self.label3 = QtWidgets.QLabel("Find what:")
        self.label3.setToolTip("Search part of the file name to replace")
        self.hbox.addWidget(self.label3)
        self.leFind = QtWidgets.QLineEdit()
        self.leFind.setText("")
        self.hbox.addWidget(self.leFind)
        self.label4 = QtWidgets.QLabel("Replace with:")
        self.hbox.addWidget(self.label4)
        self.leReplace = QtWidgets.QLineEdit()
        self.leReplace.setText("")
        self.hbox.addWidget(self.leReplace)
        self.gbRegEx.setLayout(self.hbox)
        self.hboxIDSet.addWidget(self.gbRegEx)

        # блок по разделителю
        self.hbox = QtWidgets.QHBoxLayout()
        self.gbSep = QtWidgets.QGroupBox("Separator")
        self.gbSep.setCheckable(True)
        self.gbSep.setChecked(False)
        self.gbSep.toggled.connect(lambda flag: self.gbRegEx.setChecked(not flag) if flag else flag)
        self.label5 = QtWidgets.QLabel("Type separator")
        self.label5.setToolTip("Split file name by separator and choose first part")
        self.hbox.addWidget(self.label5)
        self.leSep = QtWidgets.QLineEdit()
        self.hbox.addWidget(self.leSep)
        self.gbSep.setLayout(self.hbox)
        self.hboxIDSet.addWidget(self.gbSep)

        self.vbox.addLayout(self.hboxIDSet)

        # блок с табличкой и моделью для данных из Экселя
        self.tv = QtWidgets.QTableView()
        self.sti = MyStandardItemModel()
        self.tv.setModel(self.sti)
        self.vbox.addWidget(self.tv)
        # self.vbox.addStretch(1)

        # блок с кнопками
        self.hbox = QtWidgets.QHBoxLayout()
        self.btnGet: QtWidgets.QPushButton = QtWidgets.QPushButton("&Get")
        self.btnGet.clicked.connect(self.on_get)
        self.btnGet.setShortcut("Ctrl+G")
        self.btnGet.setToolTip("Press to get file names (Ctrl+G)")
        self.hbox.addWidget(self.btnGet)

        self.btnTry: QtWidgets.QPushButton = QtWidgets.QPushButton("&Try")
        self.btnTry.clicked.connect(self.on_try)
        self.btnTry.setShortcut("Ctrl+T")
        self.btnTry.setToolTip("Press to try (Ctrl+T)")
        self.hbox.addWidget(self.btnTry)

        self.btnRun: QtWidgets.QPushButton = QtWidgets.QPushButton("&Run")
        self.btnRun.clicked.connect(self.on_run)
        self.btnRun.setShortcut("Ctrl+R")
        self.btnRun.setToolTip("Press to rename (Ctrl+R)")
        self.hbox.addWidget(self.btnRun)

        self.btnQuit = QtWidgets.QPushButton("&Quit")
        self.btnQuit.clicked.connect(self.parent().quitApp)
        # self.btnRun.setShortcut("Ctrl+Q")
        self.hbox.addWidget(self.btnQuit)
        self.vbox.addLayout(self.hbox)

        # блок со статусами
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setFormat("%v from %m  %p%")
        # self.vbox.addWidget(self.progressBar)

        self.lblStatus = QtWidgets.QLabel()
        self.resPath = ""
        self.lblPerStatus = ClickedLabel()
        self.lblPerStatus.doubleclicked.connect(self.open_folder)
        self.lblPerStatus.setToolTip("Double click to open folder")

        self.statusBar.addWidget(self.progressBar, 2)
        self.statusBar.addWidget(self.lblStatus, 1)
        self.statusBar.addPermanentWidget(self.lblPerStatus, 1)

        self.setLayout(self.vbox)

        # Создаем кнопку панели задач
        # Получаем индикатор процесса, задаем его параметры
        # и делаем его видимым
        self.progress = self.parent().progress

        self.rens = set()

    @QtCore.pyqtSlot()
    def open_folder(self):
        """
        Открывает папку с переименованными файлами
        """
        if self.resPath:
            os.startfile(self.resPath)

    @QtCore.pyqtSlot()
    def on_open_result(self):
        """
        Метод открывает папку с файлами
        """
        dirName = QtWidgets.QFileDialog.getExistingDirectory(
            caption='Folder for rename',
            directory=self.lePathImg.text() if self.lePathImg.text() else QtCore.QDir.currentPath())
        if dirName:
            self.lePathImg.setText(dirName)
            self.sti.clear()

    @QtCore.pyqtSlot()
    def create_resPath(self):
        """
        создает папку для переименованных файлов
        """
        self.resPath = os.path.normpath(os.path.join(
            self.lePathImg.text(), "Renamed " + time.strftime("%Y%m%d_%H%M%S", time.localtime(self.startTime))))
        os.makedirs(self.resPath, exist_ok=True)
        self.lblPerStatus.setText(f"{self.resPath}")

    @QtCore.pyqtSlot()
    def on_get(self):
        """
        Собирает файлы с фильтрами
        """
        if not self.lePathImg.text():
            QtWidgets.QMessageBox.critical(self, "Error", "Choose the folder for rename files",
                                           defaultButton=QtWidgets.QMessageBox.Ok)
            return
        exts: list
        if self.leExt.text():
            exts = self.leExt.text().split("|")
        else:
            exts = ["*"]
        files: list = []
        for ext in exts:
            files.extend(glob.glob(os.path.join(self.lePathImg.text(), f"*.{ext}")))
            # files = glob.glob(join(fPath, "**", "*.txt"), recursive=True)
        self.lblStatus.setText(f"Get files from folders")
        self.sti.clear()
        self.progressBar.reset()
        self.progress.reset()
        self.progressBar.setValue(0)
        self.progress.setValue(0)

        cols = ["Name", "Ext", "Full Name", "Rename"]

        for file in files:
            colsCurr = [QtGui.QStandardItem(os.path.splitext(os.path.basename(file))[0]),
                        QtGui.QStandardItem(os.path.splitext(os.path.basename(file))[1]),
                        QtGui.QStandardItem(os.path.basename(file)), QtGui.QStandardItem("")]
            self.sti.appendRow(colsCurr)

        self.sti.setHorizontalHeaderLabels(cols)
        self.tv.resizeColumnsToContents()
        self.tv.setColumnWidth(3, self.tv.columnWidth(2))
        self.progressBar.setMaximum(self.sti.rowCount())
        self.progress.setMaximum(self.sti.rowCount())
        # self.btnRun.setDisabled(False)

    @QtCore.pyqtSlot()
    def on_try(self):
        """
        Проставляет новые имена файлов, чтоыб посмотреть все ли в порядке
        """
        self.lblStatus.setText(f"Try and revise column Rename")
        self.rens.clear()
        if self.isValid("try"):
            self.sti.setColorized(True)
            for i in range(0, self.sti.rowCount()):
                self.sti.item(i, 3).setText("")
                txt = self.sti.item(i, 0).text()
                ren = ""

                if self.gbRegEx.isChecked():
                    what = re.compile(self.leFind.text())
                    res = self.leReplace.text()
                    if what.search(txt):
                        ren = what.sub(res, txt)

                if self.gbSep.isChecked():
                    ren = txt.split(self.leSep.text())[0]

                ren = ren if ren else txt

                self.sti.item(i, 3).setText(ren)
                self.color_dup(self.sti.item(i, 3))

                QtWidgets.qApp.processEvents()
            # self.sti.endResetModel()

    @QtCore.pyqtSlot()
    def on_run(self):
        """
        Переименовывает файлы
        """

        if self.isValid():
            self.setAllDisabled()
            self.startTime = time.time()
            self.create_resPath()

            for i in range(0, self.sti.rowCount()):
                if self.sti.item(i, 3).text():
                    curr = self.sti.item(i, 2).text()
                    ren = self.sti.item(i, 3).text() + self.sti.item(i, 1).text()

                    shutil.copy2(os.path.join(self.lePathImg.text(), curr), os.path.join(self.resPath, ren))

                    self.tv.scrollTo(self.sti.index(i, 0), QtWidgets.QAbstractItemView.EnsureVisible)
                    self.progressBar.setValue(self.progressBar.value() + 1)
                    self.progress.setValue(self.progress.value() + 1)

                QtWidgets.qApp.processEvents()

            self.progressBar.setValue(self.progressBar.value() + 1)
            self.progress.reset()
            self.finishTime = time.time()
            self.lblStatus.setText(f"Done! duration: {(self.finishTime - self.startTime) / 60:.4f} min")
            self.setAllDisabled(False)

            os.startfile(self.resPath)

    def setAllDisabled(self, flag=True):
        """
        метод все кнопки переключает с актвиных на неактвиные и наоборот
        :param bool flag: True если не активно нужно сделать
        """
        self.lePathImg.setDisabled(flag)
        self.leExt.setDisabled(flag)
        if self.gbRegEx.isChecked():
            self.leFind.setDisabled(flag)
            self.leReplace.setDisabled(flag)
        self.gbRegEx.setDisabled(flag)

        if self.gbSep.isChecked():
            self.leSep.setDisabled(flag)
        self.gbSep.setDisabled(flag)

        self.btnPathImg.setDisabled(flag)
        self.btnTry.setDisabled(flag)
        self.btnRun.setDisabled(flag)
        self.btnQuit.setDisabled(flag)

        self.parent().menuBar.setDisabled(flag)

    def isValid(self, method="run"):
        """
        Проверяет валидность введённых параметров
        :param str method: какой метод вызывает валидацию
        :return bool:
        """
        if not self.lePathImg.text():
            QtWidgets.QMessageBox.critical(self, "Error", "Choose the folder for rename files",
                                           defaultButton=QtWidgets.QMessageBox.Ok)
            return False
        if not os.path.exists(self.lePathImg.text()):
            QtWidgets.QMessageBox.critical(self, "Error", f"Folder {self.lePathImg.text()} doesn't exist!",
                                           defaultButton=QtWidgets.QMessageBox.Ok)
            return False
        if self.gbRegEx.isChecked() and self.gbSep.isChecked():
            QtWidgets.QMessageBox.critical(self, "Error", "You must choose something one: RegExp or Separator",
                                           defaultButton=QtWidgets.QMessageBox.Ok)
            return False
        if self.gbRegEx.isChecked():
            if not self.leFind.text():
                QtWidgets.QMessageBox.critical(self, "Error", "Type what to replace in file names",
                                               defaultButton=QtWidgets.QMessageBox.Ok)
                return False
        if self.gbSep.isChecked():
            if not self.leSep.text():
                QtWidgets.QMessageBox.critical(self, "Error", "Type separator to devide file names",
                                               defaultButton=QtWidgets.QMessageBox.Ok)
                return False
        if self.sti.rowCount() == 0:
            QtWidgets.QMessageBox.critical(self, "Error", f"Push button Get",
                                           defaultButton=QtWidgets.QMessageBox.Ok)
            return False

        if method == "run":
            self.rens.clear()
            for i in range(0, self.sti.rowCount()):
                self.color_dup(self.sti.item(i, 3))

        if len(self.rens) > 0 and len(self.rens) != self.sti.rowCount():
            QtWidgets.QMessageBox.critical(self, "Error", f"You have duplicate names in Rename columns!",
                                           defaultButton=QtWidgets.QMessageBox.Ok)
            return False
        return True

    def color_dup(self, sind):
        """
        Смотрит является ли текущий элемент дубликатом и подкрашивает дубли
        :param MyStandardItemModel sind: индекс элемента
        """
        if sind.text() in self.rens:
            self.sti.setData(self.sti.indexFromItem(sind), QtGui.QColor(QtCore.Qt.red), QtCore.Qt.BackgroundColorRole)
        else:
            self.sti.setData(self.sti.indexFromItem(sind), QtGui.QColor(QtCore.Qt.white), QtCore.Qt.BackgroundColorRole)
            self.rens.add(sind.text())
