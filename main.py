#!/usr/bin/env python3

from index_of.main import IndexOf
from PyQt5 import QtWidgets, QtCore, uic
import shutil
import sys
import os

from gui import main
from PyQt5.QtWidgets import QTreeWidgetItem

import webbrowser


VERSION = "04.09.21"

ROOT_PATH = "settings/root"
INDEX_PATH = "settings/index"
INDEX_DATE = "data/index_date"

ROOT_PATH_DEFAULT = os.path.join(os.getcwd(), "root")
INDEX_PATH_DEFAULT = os.path.join(os.getcwd(), "index")

GREETING_MESSAGE = "Добро пожаловать в catalogue [{}]".format(VERSION)


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
    return metadata


class FillDialogWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("gui/add_meta.ui", self)
        #self.ui = gui.add_meta.Ui_Dialog()
        #self.ui.setupUi(self)

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
        #path = os.path.join(os.getcwd(), "root", path[1:])
        print(path)
        self.form_data["PATH"] = path

        with open(path+".meta", "r+") as file:
            for line in file.readlines():
                if line.endswith("\n"):
                    line = line[:len("\n")*-1]
                key_value = line.split("=")
                self.form_data.update({key_value[0]: key_value[1]})

        self.update_window()

    def pass_path(self, path):
        self.path = path
        self.list_info(self.path)

    def show_window(self):
        self.show()
        self.exec_()

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
        self.ui = uic.loadUi("gui/info.ui", self)
        self.get_info()
        self.show()
        self.exec_()

    def get_info(self):
        count, size, authors = get_statistics()
        self.ui.label_4.setText(str(count))
        self.ui.label_5.setText(str(size))
        self.ui.label_6.setText(str(authors))


class MainWindow(QtWidgets.QMainWindow):
 
    def __init__(self):

        super().__init__()

        self.settings = QtCore.QSettings()
        self.set_options()

        self.list_is_empty = True
        self.button_locked = False

        #self.ui = uic.loadUi("gui/main.ui", self)
        self.ui = main.Ui_MainWindow()
        self.ui.setupUi(self)


        # DRAFT BEGINNING

        self.fill_tree()

        # DRAFT END


        self.status_bar = self.statusBar()
        self.status_bar.showMessage(GREETING_MESSAGE)

        #self.ui.listWidget.itemDoubleClicked.connect(self.show_entity_info)

        self.ui.pushButton.clicked.connect(self.open_index)
        self.ui.pushButton_3.clicked.connect(self.show_info)
        self.ui.pushButton_4.clicked.connect(self.upload_file)
        self.ui.toolButton.clicked.connect(self.config)

    # DRAFT FUNCTIONS
    def get_entity(self):
        item = self.ui.treeWidget.currentItem()
        if item.childCount() == 0:
            path = os.path.join(self.root_folder, item.parent().parent().text(0), item.parent().text(0),item.text(0)) 
            win = FillDialogWindow()
            win.pass_path(path)
            win.show_window()
    
    def open_index(self):
        path = self.settings.value(INDEX_PATH)
        if os.listdir(path):
            webbrowser.open(os.path.join(path, "index.html"))
        else:
            self.ui.status_bar.showMessage("Каталог пуст!")

    def fill_tree(self):
        item = QTreeWidgetItem()
        self.root_folder = self.settings.value(ROOT_PATH)

        for root_entity in os.listdir(self.root_folder):

            root_item = QTreeWidgetItem()
            root_item.setText(0, root_entity)
            
            self.ui.treeWidget.addTopLevelItem(root_item)

            for subfolder in os.listdir(os.path.join(self.root_folder, root_entity)):
                
                subfolder_item = QTreeWidgetItem()
                subfolder_item.setText(0, subfolder)
                
                root_item.addChild(subfolder_item)


                for file in os.listdir(os.path.join(self.root_folder, root_entity, subfolder)):
                    
                    if not file.endswith(".meta"):

                        file_item = QTreeWidgetItem()
                        file_item.setText(0, file)
                        subfolder_item.addChild(file_item)

        self.ui.treeWidget.itemDoubleClicked.connect(self.get_entity)


    def refresh_tree(self):
        self.ui.treeWidget.clear()
        self.fill_tree()
    # DRAFT FUNCTIONS


    def upload_file(self):
        win = FillDialogWindow()
        win.show_window()

        self.refresh_tree()


    def show_dialog(self):
        FillDialogWindow()
        
        #self.refresh_tree()


    def show_info(self):
        InfoDialogWindow()

    def set_options(self):

        QtCore.QCoreApplication.setOrganizationName("null")
        QtCore.QCoreApplication.setOrganizationDomain("nodomain")
        QtCore.QCoreApplication.setApplicationName("catalogue")

        self.settings.value(ROOT_PATH, type=str)
        self.settings.value(INDEX_PATH, type=str)
        self.settings.value(INDEX_DATE, type=str)

        if not self.settings.value(INDEX_PATH):
            self.settings.setValue(INDEX_PATH, INDEX_PATH_DEFAULT)

        if not self.settings.value(ROOT_PATH):
            self.settings.setValue(ROOT_PATH, ROOT_PATH_DEFAULT)

        self.settings.sync()

    def config(self):
        ConfigDialogWindow(self)


class ConfigDialogWindow(QtWidgets.QDialog):
    def __init__(self, root):
        super().__init__()
        self.root = root
        #self.ui = gui.config.Ui_Dialog()
        self.ui = uic.loadUi("gui/config.ui", self)
        #self.ui.setupUi(self)

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
                        os.mkdir(folder)
                    else:
                        os.mkdir(folder)
                        err_folder = folder
                        access_error = True
        else:
            if root_path == "": root_path = ROOT_PATH_DEFAULT
            if index_path == "":
                index_path = INDEX_PATH_DEFAULT
                self.settings.setValue(INDEX_DATE, "")
            self.root.status_bar.showMessage("Пустые значения недопустимы. Установлены каталоги по умолчанию.")

        if access_error:
            self.root.status_bar.showMessage("Недостаточно привилегий для записи в {}!".format(err_folder))

        else:
            self.settings.setValue(ROOT_PATH, root_path)
            self.settings.setValue(INDEX_PATH, index_path)
            self.settings.sync()

        self.close()

    def index(self):
        index = IndexOf(self.root_path, self.index_path)

        self.root.status_bar.showMessage("Индекс успешно обновлён. Добавлено файлов: {}".format(index.files_created))

        self.settings.setValue(INDEX_DATE, index.termination_time)
        self.settings.sync()

        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    application = MainWindow()
    application.show()

    sys.exit(app.exec())
