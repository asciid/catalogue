"""
    TODO:
- Автоматическая проверка/правка метаданных бинарных файлов -> PyPDF2
- Бинарные файлы
+ Возможность указать сторонний каталог корня
- Замена lineEdit в главном окне на statusBar [!!!]
x Склейка единой базы из каждой книги
- Обновление listWidget после добавления нового файла
- Проверить, не удобнее ли обходиться без генерации кода окон

[config.py]
+ Генерация HTML через index_of
+ Время генерации через QSettings
+ Валидация каталога вывода

"""

from index_of.main import IndexOf
from PyQt5 import QtWidgets, QtCore
from gui.gui import Ui_MainWindow
from gui.info import Ui_Dialog as infoDialog
from gui.config import Ui_Dialog as configDialog
from gui.add_meta import Ui_Dialog as fillDialog
import shutil
import sys
import os


ROOT_PATH = "settings/root"
INDEX_PATH = "settings/index"
INDEX_DATE = "data/index_date"

ROOT_PATH_DEFAULT = os.path.join(os.getcwd(), "root")
INDEX_PATH_DEFAULT = os.path.join(os.getcwd(), "index")


def get_files():
    out = []
    count = 0
    root = QtCore.QSettings().value(ROOT_PATH)

    tree = os.walk(root)
    first = True

    for base, dirs, files in tree:
        if first:
            first = False
            continue
        elif not files:
            continue

        for file in files:
            if not file.endswith(".meta"):
                out.append(base+"/"+file)
                count += 1

    return out, count


def get_statistics():
    count = 0
    size = 0
    root = QtCore.QSettings().value(ROOT_PATH)
    authors = len(os.listdir(root))

    tree = os.walk(root)
    first = True

    for base, dirs, files in tree:
        if first:
            first = False
            continue
        elif not files:
            continue

        for file in files:
            size += os.path.getsize(base+"/"+file)
            if not file.endswith(".meta"):
                count += 1

    size /= 1024**3
    precision = 3

    while round(size, precision) == 0:
        precision += 1

    size = round(size, precision)

    return count, size, authors


def extract_metadata(path):
    metadata = {}
    with open(path+".meta") as file:
        for line in file.readlines():
            if line.endswith("\n"):
                line = line[:-1]
            key, value = line.split("=")
            metadata.update({key: value})
    #print(path.replace(metadata["TITLE"], ""))
    return metadata


class FillDialogWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = fillDialog()
        self.ui.setupUi(self)

        self.path = ""
        self.form_data = {
            "TITLE": "",
            "AUTHOR": "",
            "PUBLISHER": "",
            "PUBLICATION_YEAR": "",
            "LANGUAGE": "",
            "QUALITY": "",
            "PAGES": "",
            "TAGS": "",
            "PATH": ""
        }

        self.ui.pushButton.clicked.connect(self.form_sent)
        self.ui.pushButton_3.clicked.connect(self.choose_file)

    def choose_file(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "catalogue::upload()")

        if file_name:
            self.ui.lineEdit_9.setText(file_name)

    def upload(self):
        file_name = self.form_data["PATH"].split("/")[-1]
        title = file_name.split(".")[0]

        path = "root/{}/{}".format(self.form_data["AUTHOR"], title)

        if not os.path.exists(path):
            os.makedirs(path)

        if not os.path.exists(path+"/"+file_name):
            if self.ui.checkBox.isChecked():
                shutil.move(self.form_data["PATH"], path)
            else:
                shutil.copy(self.form_data["PATH"], path)

        with open("{}/{}.meta".format(path, file_name), 'w+') as file:
            file.writelines(
                "TITLE={}\n"
                "AUTHOR={}\n"
                "PUBLISHER={}\n"
                "PUBLICATION_YEAR={}\n"
                "LANGUAGE={}\n"
                "QUALITY={}\n"
                "PAGES={}\n"
                "TAGS={}".format(self.form_data["TITLE"], self.form_data["AUTHOR"], self.form_data["PUBLISHER"],
                                 self.form_data["PUBLICATION_YEAR"], self.form_data["LANGUAGE"],
                                 self.form_data["QUALITY"], self.form_data["PAGES"], self.form_data["TAGS"]))

        self.hide()

    def form_sent(self):
        self.form_data["TITLE"] = self.ui.lineEdit.text()
        self.form_data["AUTHOR"] = self.ui.lineEdit_2.text()
        self.form_data["PUBLISHER"] = self.ui.lineEdit_3.text()
        self.form_data["PUBLICATION_YEAR"] = self.ui.lineEdit_4.text()
        self.form_data["LANGUAGE"] = self.ui.lineEdit_5.text()
        self.form_data["QUALITY"] = self.ui.lineEdit_6.text()
        self.form_data["PAGES"] = self.ui.lineEdit_7.text()
        self.form_data["TAGS"] = self.ui.lineEdit_8.text()
        self.form_data["PATH"] = self.ui.lineEdit_9.text()

        self.upload()

        self.hide()

    def list_info(self, path):
        self.form_data["PATH"] = path

        with open(path+".meta", "r+") as file:
            for line in file.readlines():
                if line.endswith("\n"):
                    line = line[:len("\n")*-1]
                key_value = line.split("=")
                self.form_data.update({key_value[0]: key_value[1]})

        #print(self.form_data)
        self.update_window()

    def pass_path(self, path):
        self.path = path
        self.list_info(self.path)

    def show_window(self):
        self.exec_()
        self.show()

    def update_window(self):
        self.ui.lineEdit.setText(self.form_data["TITLE"])
        self.ui.lineEdit_2.setText(self.form_data["AUTHOR"])
        self.ui.lineEdit_3.setText(self.form_data["PUBLISHER"])
        self.ui.lineEdit_4.setText(self.form_data["PUBLICATION_YEAR"])
        self.ui.lineEdit_5.setText(self.form_data["LANGUAGE"])
        self.ui.lineEdit_6.setText(self.form_data["QUALITY"])
        self.ui.lineEdit_7.setText(self.form_data["PAGES"])
        self.ui.lineEdit_8.setText(self.form_data["TAGS"])
        self.ui.lineEdit_9.setText(self.form_data["PATH"])


class InfoDialogWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = infoDialog()
        self.ui.setupUi(self)
        self.get_info()
        self.exec_()
        self.show()

    def get_info(self):
        count, size, authors = get_statistics()
        self.ui.label_4.setText(str(count))
        self.ui.label_5.setText(str(size))
        self.ui.label_6.setText(str(authors))


class MainWindow(QtWidgets.QMainWindow):
 
    def __init__(self):

        super().__init__()

        self.set_options()

        self.clear = False

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.lineEdit.setText("Добро пожаловать в catalogue!")

        self.ui.listWidget.itemDoubleClicked.connect(self.show_entity_info)
        self.ui.pushButton.clicked.connect(self.btn_clicked)
        self.ui.pushButton_3.clicked.connect(self.show_info)
        self.ui.pushButton_4.clicked.connect(self.upload_file)
        self.ui.toolButton.clicked.connect(self.config)

    def show_entity_info(self):
        win = FillDialogWindow()
        win.pass_path(self.ui.listWidget.currentItem().text())
        win.show_window()

    def upload_file(self):
        win = FillDialogWindow()
        win.show_window()

    def show_dialog(self):
        FillDialogWindow()
        self.list_clear()
        self.list_scan()

    def btn_clicked(self):
        if not self.clear:
            self.list_clear()
        else:
            self.list_scan()

    def list_scan(self):
        self.ui.listWidget.clear()
        self.ui.lineEdit.clear()
        self.ui.pushButton.setText("Сканировать")
        self.clear = False

    def list_clear(self):
        data, count = get_files()
        self.ui.lineEdit.setText("Найдено {} книг(и).".format(count))
        if data:
            self.ui.listWidget.setWordWrap(True)

            for item in data:
                self.ui.listWidget.addItem(item.replace(QtCore.QSettings().value(ROOT_PATH), ""))

            #self.ui.listWidget.addItems(data)
            self.ui.pushButton.setText("Очистить")
            self.clear = True
        else:
            self.ui.lineEdit.setText("Ничего не найдено!")

    def show_info(self):
        InfoDialogWindow()

    def set_options(self):
        QtCore.QCoreApplication.setOrganizationName("null")
        QtCore.QCoreApplication.setOrganizationDomain("nodomain")
        QtCore.QCoreApplication.setApplicationName("catalogue")

        settings = QtCore.QSettings()

        settings.value(ROOT_PATH, type=str)
        settings.value(INDEX_PATH, type=str)
        settings.value(INDEX_DATE, type=str)

        if not settings.value(INDEX_PATH):
            settings.setValue(INDEX_PATH, INDEX_PATH_DEFAULT)

        if not settings.value(ROOT_PATH):
            settings.setValue(ROOT_PATH, ROOT_PATH_DEFAULT)

        settings.sync()

    def config(self):
        ConfigDialogWindow(self)


class ConfigDialogWindow(QtWidgets.QDialog):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.ui = configDialog()
        self.ui.setupUi(self)

        self.settings = QtCore.QSettings()
        self.root_path = self.settings.value(ROOT_PATH)
        self.index_path = self.settings.value(INDEX_PATH)
        self.index_date = self.settings.value(INDEX_DATE)

        self.ui.lineEdit.setText(self.root_path)
        self.ui.lineEdit_2.setText(self.index_path)
        self.ui.lineEdit_3.setText(self.index_date)

        self.ui.pushButton.clicked.connect(self.save_data)
        self.ui.pushButton_3.clicked.connect(self.index)

        self.show()
        self.exec_()

    def save_data(self):
        root_path = self.ui.lineEdit.text()
        index_path = self.ui.lineEdit_2.text()

        access_error = False
        err_folder = ""

        if root_path and index_path:
            for folder in (root_path, index_path):
                if os.path.exists(folder):
                    if not os.access(folder, os.W_OK):
                        err_folder = folder
                        access_error = True
                else:
                    if os.access(folder, os.W_OK):
                        os.makedirs(folder)
                    else:
                        err_folder = folder
                        access_error = True
        else:
            if root_path == "": root_path = ROOT_PATH_DEFAULT
            if index_path == "":
                index_path = INDEX_PATH_DEFAULT
                self.settings.setValue(INDEX_DATE, 0)
            self.root.ui.lineEdit.setText("Пустые значения недопустимы. Установлены каталоги по умолчанию.")

        if access_error:
            self.root.ui.lineEdit.setText("Недостаточно привилегий для записи в {}!".format(err_folder))

        else:
            self.settings.setValue(ROOT_PATH, root_path)
            self.settings.setValue(INDEX_PATH, index_path)
            self.settings.sync()

        self.close()

    def index(self):
        index = IndexOf(self.root_path, self.index_path)

        self.root.ui.lineEdit.setText("Индекс успешно обновлён. Добавлено файлов: {}".format(index.files_created))

        self.settings.setValue(INDEX_DATE, index.termination_time)
        self.settings.sync()

        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    application = MainWindow()
    application.show()

    sys.exit(app.exec())
