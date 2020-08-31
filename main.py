# -*- coding: utf-8 -*-
import csv
import json
import os
import shutil
import sys
import time
import traceback

import fitz
import pandas as pd
import yaml
from PyPDF2 import PdfFileReader, PdfFileWriter
from PyQt5.QtCore import (QAbstractTableModel, QBasicTimer, QEventLoop, QSize,
                          QSortFilterProxyModel, Qt, QTimer)
from PyQt5.QtGui import QFont, QImage, QPixmap
from PyQt5.QtSql import QSqlDatabase, QSqlQueryModel
from PyQt5.QtWidgets import (QAbstractItemView, QAction, QApplication,
                             QDesktopWidget, QDialog, QHeaderView, QLabel,
                             QMainWindow, QMenu, QMessageBox, QProgressBar,
                             QPushButton, QTreeWidgetItem, QWidget)

from setting.UI import *
from setting import check_pkg
from setting.dsu_db import Database


class PandasModel(QAbstractTableModel):

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None


class MyMainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):

        super(MyMainWindow, self).__init__(parent)

        self.setupUi(self)
        self.setWindowTitle("Order Editor")
        # define virables
        self.version = 'Version:3.5.0'
        self.header_page = 0
        self.line_page = 0
        self.img_dir = ''
        self.json_dir = ''
        self.img_file = []
        self.img_key = []
        self.json_file = []
        self.json_key = []
        self.oring_json = {}

        # setup combobox for custitem table
        self.comboBox.setCurrentIndex(1)

        # setup config
        self.config = yaml.load(
            open(("setting/config.yaml"), "r"), Loader=yaml.Loader)

        # setup DB MySql
        self.dsudb = Database()

        self.df_addr = self.dsudb.get_table('active_address')

        self.vNum = QLabel(self.version)
        self.treeWidget.header().setDefaultSectionSize(210)
        self.treeWidget.itemDoubleClicked.connect(self.checkEdit)
        self.treeWidget.itemChanged.connect(self.enable_action)

        # statusBar
        self.statusBar.showMessage('Status:', 0)
        self.statusBar.addPermanentWidget(self.vNum, stretch=0)

        # action
        self.actionOpen_Image.triggered.connect(self.imgpath)
        self.actionOpen_Json.triggered.connect(self.jsonpath)
        self.actionPrev_Page.triggered.connect(lambda: self.jsonchange(-1))
        self.actionNext_Page.triggered.connect(lambda: self.jsonchange(1))
        self.action_Save.triggered.connect(self.saveJson)
        self.action_Close.triggered.connect(self.close)
        self.actionDelete_line.triggered.connect(self.delete_line)

        # funciton
        self.next_btn.clicked.connect(lambda: self.orderchange(1))
        self.prev_btn.clicked.connect(lambda: self.orderchange(-1))
        self.save_btn.clicked.connect(self.saveJson)

        self.json_list.clicked.connect(self.jsonclicked)

        # customer item search
        self.customer_search.textChanged.connect(
            lambda: self.set_custitem_view(self.customer_view))
        self.comboBox.currentTextChanged.connect(
            lambda: self.set_custitem_view(self.customer_view))

        # wpg item search
        self.wpgitem_customer_search.textChanged.connect(
            lambda: self.set_wpgitem_view(self.wpgitem_view))

        self.set_currency_view(self.currency_view)

    def error_exception(self, e):
        error_class = e.__class__.__name__  # 取得錯誤類型
        detail = e
        error_msg = "[{}] {}".format(error_class, detail)
        print(error_msg)
        return error_msg

    def checkEdit(self, item, column):
        # allow editing only of column 1:
        children = self.treeWidget.currentItem().childCount()
        tmp = item.flags()
        self.treeWidget.blockSignals(True)
        self.actionNext_Page.setEnabled(False)
        self.actionPrev_Page.setEnabled(False)
        if column == 1 and children == 0:
            item.setFlags(tmp | QtCore.Qt.ItemIsEditable)
        elif tmp & QtCore.Qt.ItemIsEditable:
            item.setFlags(tmp ^ QtCore.Qt.ItemIsEditable)
        self.treeWidget.blockSignals(False)

    def enable_action(self):
        self.actionNext_Page.setEnabled(True)
        self.actionPrev_Page.setEnabled(True)

    def openMenu(self, position):

        menu = QMenu()

        menu.addAction(self.tr("Add line"), self.create_line)
        menu.addAction(self.tr("Insert line"), self.insert_line)
        menu.addAction(self.tr("Delete line"), self.delete_line)

        menu.exec_(self.treeWidget.viewport().mapToGlobal(position))

    def saveJson(self):

        try:
            filename = self.json_name.text().split(':')[1]
            if filename != '':
                reply = QtWidgets.QMessageBox.question(None, 'save', '\nDo you want to save %s?' % (filename),
                                                       QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.Yes:

                    toplevel = self.treeWidget.topLevelItem(0)

                    jf = self.genJson(toplevel)
                    # print(jf)
                    with open(self.json_dir+'/'+filename, 'w', encoding='utf8') as outfile:
                        json.dump(jf, outfile, ensure_ascii=False,
                                  indent=4, separators=(',', ': '))

                    self.readjson(filename)
                    self.statusBar.showMessage(
                        'Save file %s success!!' % (filename), 0)
        except Exception as e:
            self.error_exception(e)
            QtWidgets.QMessageBox.warning(
                None, 'Fail', '\nThere is no data to save!', QtWidgets.QMessageBox.Ok)

    def genJson(self, item):

        nchild = item.childCount()

        if item.text(2) == 'dict':
            document = {}
            for i in range(nchild):
                ch = item.child(i)
                document[ch.text(0)] = self.genJson(ch)
            return document

        elif item.text(2) == 'list':
            document = []
            for i in range(nchild):
                ch = item.child(i)
                document.append(self.genJson(ch))
            return document

        elif item.text(2) == 'int':
            try:
                if float(item.text(1)).is_integer():
                    return int(float(item.text(1)))
                return float(item.text(1))
            except Exception as e:
                self.error_exception(e)
                return int(0)

        elif item.text(2) == 'float':
            try:
                if float(item.text(1)).is_integer():
                    return int(float(item.text(1)))
                return float(item.text(1))
            except Exception as e:
                self.error_exception(e)
                return float(0)
        else:
            return item.text(1)

    def change_color(self):

        # setting 'shipaddr' color
        level_4 = ["custPartNoStatus"]
        # orage
        level_3 = ["custPartNo"]
        # green
        level_2 = ["custPoNumber",
                   "poDate",
                   "lineNumber",
                   "sellingPrice",
                   "voQty",
                   "originalRequestDate"]
        # white
        level_1 = ["shipAddr",
                   "payCurrency",
                   "billAddr",
                   "deliverAddr",
                   ]
        # gray
        level_0 = ["paymentTerm", "tradeTerm", "tax", "buyerName", "supplierName", "shipAddrStatus",
                   "poDateStatus", "billAddrStatus", "deliverAddrStatus", "payCurrencyStatus",
                   "paymentTermStatus", "taxStatus", "tradeTermStatus", "originalRequestDateStatus"]

        all_child = []

        # toplevel = self.treeWidget.topLevelItem(0)  # content
        # toplevel = self.get_header(toplevel)
        try:
            clist = self.treeWidget.findItems(
                'header', Qt.MatchContains | Qt.MatchRecursive, 0)
            toplevel = clist[0].parent()

            for ch in range(toplevel.childCount()):
                item = toplevel.child(ch)  # header & line
                if item.text(0) == 'line':
                    nchild = item.childCount()  # line 的 child
                    for i in range(nchild):
                        all_child.append(item.child(i))
                else:
                    all_child.append(item)

            for item in all_child:
                nchild = item.childCount()
                for i in range(nchild):
                    # hide columns with 'ID' 2019-11-21
                    if 'ID' in item.child(i).text(0):
                        item.child(i).setHidden(True)

                    if item.child(i).text(0) in level_4:
                        item.child(i).setForeground(
                            0, QtGui.QBrush(QtGui.QColor("#59FAFC")))
                        item.child(i).setForeground(
                            1, QtGui.QBrush(QtGui.QColor("#59FAFC")))
                        font = QFont()
                        font.setWeight(QFont.Bold)
                        font.setPixelSize(25)
                        item.child(i).setFont(1, font)

                    elif item.child(i).text(0) in level_3:
                        item.child(i).setForeground(
                            0, QtGui.QBrush(QtGui.QColor("#F38023")))
                        item.child(i).setForeground(
                            1, QtGui.QBrush(QtGui.QColor("#F38023")))
                        query = 'SELECT * FROM cust_part_no WHERE cust_part_no = \"{}\"'.format(
                            item.child(i).text(1))
                        df = self.dsudb.query(query)
                        if len(df) > 0:
                            item.child(i).setForeground(
                                1, QtGui.QBrush(QtGui.QColor("#F38")))
                    elif item.child(i).text(0) in level_2:
                        item.child(i).setForeground(
                            0, QtGui.QBrush(QtGui.QColor("#98cf19")))
                        item.child(i).setForeground(
                            1, QtGui.QBrush(QtGui.QColor("#98cf19")))
                    elif item.child(i).text(0) in level_0 or 'id' in item.child(i).text(0).lower():
                        item.child(i).setForeground(
                            0, QtGui.QBrush(QtGui.QColor("#34383C")))
                        item.child(i).setForeground(
                            1, QtGui.QBrush(QtGui.QColor("#34383C")))
        except Exception as e:
            self.error_exception(e)
            QtWidgets.QMessageBox.information(
                None, 'NoData', '\nJson format Error.\n There is no \'header\' or \'line\' in content.', QtWidgets.QMessageBox.Ok)

    def insert_line(self):
        try:
            current = self.treeWidget.currentItem()
            clist = self.treeWidget.findItems(
                'line', Qt.MatchContains | Qt.MatchRecursive, 0)
            parent = clist[0]
            # parent = self.treeWidget.topLevelItem(0).child(1)  # line
            line_num = self.parent_is_line(current)

            if line_num:
                result = QMessageBox.question(None, 'Delete line', '\nDo you want to insert line %d？' % (line_num),
                                              QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if result == QtWidgets.QMessageBox.Yes:
                    jf = self.config["example_json"]
                    parent.insertChild(line_num - 1, self.load(jf))
                    self.change_color()
                    self.treeWidget.expandAll()
                    for i in range(parent.childCount()):
                        parent.child(i).setText(0, str(i + 1))
            else:
                QtWidgets.QMessageBox.warning(
                    None, 'NoData', '\nPlease select the line node! Try again.', QtWidgets.QMessageBox.Ok)
        except Exception as e:
            self.error_exception(e)
            QtWidgets.QMessageBox.warning(
                None, 'NoData', '\nPlease select the line node! Try again.', QtWidgets.QMessageBox.Ok)

    def create_line(self):

        try:
            clist = self.treeWidget.findItems(
                'line', Qt.MatchContains | Qt.MatchRecursive, 0)
            parent = clist[0]
            # parent = self.treeWidget.topLevelItem(0).child(1)
            line_num = parent.childCount()+1
            result = QMessageBox.question(None, 'Delete line', '\nDo you want to create line %d？' % (line_num),
                                          QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if result == QtWidgets.QMessageBox.Yes:

                jf = self.config["example_json"]
                self.load(jf, parent)
                self.change_color()
                self.treeWidget.expandAll()

                for i in range(parent.childCount()):
                    parent.child(i).setText(0, str(i + 1))
        except Exception as e:
            self.error_exception(e)
            QtWidgets.QMessageBox.information(
                None, 'NoData', '\nNo Data! Try again.', QtWidgets.QMessageBox.Ok)

    def delete_line(self):

        try:
            current = self.treeWidget.currentItem()
            clist = self.treeWidget.findItems(
                'line', Qt.MatchContains | Qt.MatchRecursive, 0)
            parent = clist[0]
            # parent = self.treeWidget.topLevelItem(0).child(1) # line
            line_num = self.parent_is_line(current)

            if line_num:
                result = QMessageBox.question(None, 'Delete line', '\nDo you want to delete line %d？' % (line_num),
                                              QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if result == QtWidgets.QMessageBox.Yes:
                    child = parent.child(line_num-1)
                    parent.removeChild(child)
                    for i in range(parent.childCount()):
                        parent.child(i).setText(0, str(i+1))
            else:
                QMessageBox.warning(
                    None, 'NoData', '\nPlease select the line node! Try again.', QtWidgets.QMessageBox.Ok)

        except Exception as e:
            self.error_exception(e)

            QMessageBox.warning(
                None, 'NoData', '\nPlease select the line node! Try again.', QtWidgets.QMessageBox.Ok)

    def parent_is_line(self, item):
        if item.parent().text(0) == 'line':
            return int(item.text(0))
        else:
            return self.parent_is_line(item.parent())
        return False

    def data_check(self):

        try:
            toplevel = self.treeWidget.topLevelItem(0)
            current_json = self.genJson(toplevel)

            if self.oring_json != current_json:

                result = QMessageBox.question(self, 'The document has been modified.',
                                              '\nDo you want to save your changes?',
                                              QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
                if result == QMessageBox.Save:
                    filename = self.json_name.text().split(':')[1]
                    jf = self.genJson(self.treeWidget.topLevelItem(0))
                    with open(self.json_dir + '/' + filename, 'w', encoding='utf8') as outfile:
                        json.dump(jf, outfile, ensure_ascii=False,
                                  indent=4, separators=(',', ': '))

                    self.readjson(filename)
                    return True
                elif result == QMessageBox.Discard:
                    return True
                else:
                    return False
            return True

        except Exception as e:
            self.error_exception(e)

    def jsonchange(self, num):

        current = self.json_list.currentRow()
        total = self.json_list.count()

        current += num

        if current >= 0 and current < total:

            if (self.data_check()):

                item = self.json_list.item(current)
                item.setSelected(True)
                self.jsonlist(item.text())
                self.json_list.repaint()

    def jsonclicked(self):

        current_json = self.json_name.text().split(':')[1]
        select_json = self.json_list.currentItem().text()
        if select_json != current_json and self.data_check():
            # print(select_json,current_json)
            self.jsonlist(select_json)
            self.json_list.repaint()
        else:
            for i in range(self.json_list.count()):
                item = self.json_list.item(i)
                if current_json == item.text():
                    item.setSelected(True)
                    break

    def jsonlist(self, select_json):

        self.readjson(select_json)
        self.json_name.setText('Json   Name:%s' % (select_json))

        img = ''
        for file in self.img_file:
            # json_key = '_'.join( select_json.split('.')[0].split('_')[0:3])
            json_key = select_json.split('.')[0]
            if json_key in file:
                img = file
                break

        self.order_name.setText('Order Name:%s' % (img))
        self.order_name.repaint()
        self.readimg(img)

    def orderchange(self, num):

        current = int(self.img_count.text().split('/')[0])
        total = int(self.img_count.text().split('/')[1])

        current += num

        if current > 0 and current <= total:

            try:
                self.img_count.setText('%d/%d' % (current, total))
                img_file = self.order_name.text().split(':')[1]
                img_index = self.img_file.index(img_file)
                self.order_name.setText('Order Name:%s' %
                                        (self.img_file[img_index + num]))
                self.order_name.repaint()
                self.readimg(self.img_file[img_index + num])

            except Exception as e:
                self.error_exception(e)
                QtWidgets.QMessageBox.warning(
                    None, 'Fail', '\nPlease check the path of json', QtWidgets.QMessageBox.Ok)

    def imgpath(self):
        self.pdf_file = []
        self.msgBox = QMessageBox()
        shutil.rmtree('./tmp', ignore_errors=True)

        fdir = QtWidgets.QFileDialog.getExistingDirectory(
            None, 'folder name', './')

        try:
            if fdir != '':

                self.statusBar.showMessage('Image path:%s' % (fdir), 0)

                self.pdf_file = [f for f in os.listdir(
                    fdir) if not f.startswith('.')]
                if not os.path.exists('./tmp'):
                    os.mkdir('./tmp')

                self.msgBox.setText('\nExtracting images from PDF...\n')
                self.msgBox.setWindowFlags(
                    Qt.CustomizeWindowHint | Qt.WindowTitleHint)
                self.msgBox.addButton(QMessageBox.Ok)
                self.msgBox.button(QMessageBox.Ok).hide()
                self.msgBox.show()

                for f in self.pdf_file:

                    self.msgBox.setText(
                        '\nExtracting images from PDF...\n%s' % (f))
                    loop = QEventLoop()
                    QTimer.singleShot(100, loop.quit)
                    loop.exec_()
                    fpath = '%s/%s' % (fdir, f)
                    doc = fitz.open(fpath)
                    pages = PdfFileReader(
                        open(fpath, "rb"), strict=False).numPages
                    for i in range(0, pages):
                        page = doc.loadPage(i)  # number of page
                        zoom_x = 3  # (1.33333333-->1056x816)   (2-->1584x1224)
                        zoom_y = 3
                        mat = fitz.Matrix(zoom_x, zoom_y).preRotate(0)
                        pix = page.getPixmap(matrix=mat, alpha=False)
                        output = "./tmp/{}_{}.png".format(
                            f.split('.')[0], i)
                        pix.writePNG(output)
                self.msgBox.setText(
                    '\nExtracting images from PDF...\nCompleted!!')
                self.msgBox.button(QMessageBox.Ok).show()
                self.msgBox.button(QMessageBox.Ok).animateClick(1*1000)
                self.img_dir = './tmp'
                self.img_file = [f for f in os.listdir(
                    self.img_dir) if not f.startswith('.')]
                self.img_file.sort()

                # self.img_key =  ['_'.join( f.split('.')[0].split('_')[0:3] ) for f in self.img_file]
                self.img_key = ['_'.join(f.split('.')[0].split('_')[
                                         0:-1]) for f in self.img_file]
                # print(self.img_key)
                self.readimg(self.img_file[0])

        except Exception as e:
            self.error_exception(e)
            QtWidgets.QMessageBox.warning(
                None, 'Fail', '\nFailed to load PDF, Try again！', QtWidgets.QMessageBox.Ok)
            self.msgBox.hide()
            self.imgpath()

    def readimg(self, _img):

        try:
            self.img_view.setPhoto(QtGui.QPixmap(
                '%s/%s' % (self.img_dir, _img)))
            self.order_name.setText("Order Name:%s" % (_img))
            self.order_name.repaint()
            self.statusBar.showMessage('Order Name:%s' % (_img), 0)

        except Exception as e:
            self.error_exception(e)
            QtWidgets.QMessageBox.warning(
                None, 'Fail', '\nImage Error, Try again！', QtWidgets.QMessageBox.Ok)
            self.imgpath()

    def jsonpath(self):

        if self.img_dir != '':
            self.json_file = []
            self.json_list.clear()
            self.json_list.repaint()
            self.json_dir = QtWidgets.QFileDialog.getExistingDirectory(
                None, 'folder name', '')

            try:
                if self.json_dir != '':

                    self.statusBar.showMessage(
                        'Json path:%s' % (self.json_dir), 0)
                    self.json_file = [f for f in os.listdir(
                        self.json_dir) if not f.startswith('.')]
                    self.json_file.sort()
                    # self.json_key = ['_'.join( f.split('.')[0].split('_')[0:3] ) for f in self.json_file]
                    self.json_key = [f.split('.')[0] for f in self.json_file]

                    error_lst = ''
                    for key in self.json_key:
                        if key not in self.img_key:
                            error_lst += key
                            error_lst += '\n'

                    if error_lst != '':
                        # print(error_lst)
                        QtWidgets.QMessageBox.information(None, 'Json  Error', '\nJson files not match, Try again...\n%s' % (
                            error_lst), QtWidgets.QMessageBox.Ok)
                        self.json_file = []
                        self.json_list.clear()
                        self.json_list.repaint()
                        return True
                    # print(self.json_file)

                    self.json_name.setText(
                        'Json   Name:%s' % (self.json_file[0]))
                    self.json_name.repaint()

                    for item in self.json_file:
                        self.json_list.addItem(str(item))

                    self.readjson(self.json_file[0])
                    self.jsonlist(self.json_file[0])

                    self.treeWidget.customContextMenuRequested.connect(
                        self.openMenu)

            except Exception as e:
                errMsg = self.error_exception(e)

                QtWidgets.QMessageBox.information(
                    None, 'Exception', errMsg, QtWidgets.QMessageBox.Ok)

        else:
            QtWidgets.QMessageBox.information(
                None, 'Json path Error', '\nPlease setting the path of image first!', QtWidgets.QMessageBox.Ok)

    def load(self, value, parent=None, sort=False):

        rootItem = QTreeWidgetItem(parent)
        # rootItem.setText(0, "content")

        if isinstance(value, dict):
            items = (
                sorted(value.items())
                if sort else value.items()
            )

            for key, value in items:
                child = self.load(value, rootItem)
                child.setText(0, key)
                rootItem.addChild(child)
                rootItem.setText(2, 'dict')

        elif isinstance(value, list):
            for index, value in enumerate(value):
                child = self.load(value, rootItem)
                child.setText(0, str(index+1))
                rootItem.addChild(child)
                rootItem.setText(2, 'list')

        else:
            type_name = type(value).__name__
            rootItem.setText(1, str(value))
            rootItem.setText(2, type_name)
            # rootItem.setFlags(rootItem.flags()|QtCore.Qt.ItemIsEditable)
        return rootItem

    def readjson(self, _json):
        # setting the number of same png
        count = 0

        # js_key = '_'.join(_json.split('.')[0].split('_')[0:3])
        js_key = _json.split('.')[0]
        for file in self.img_file:
            if js_key in file:
                count += 1

        if count > 0:
            self.img_count.setText('1/%d' % (count))

            self.json_name.setText('Json   Name:%s' % (_json))
            json_index = self.json_file.index(
                self.json_name.text().split(':')[1])
            self.json_list.item(json_index).setSelected(True)
            self.json_list.setCurrentRow(json_index)

            self.treeWidget.clear()
            path = self.json_dir + '/' + _json
            # print(path)

            self.oring_json = json.load(open(path, encoding='utf8'))

            self.load(self.oring_json, self.treeWidget)
            self.change_color()
            self.treeWidget.expandAll()

            self.addrlist()

        else:

            QtWidgets.QMessageBox.information(
                None, 'Json Error', '\nJson files not match, Try again!', QtWidgets.QMessageBox.Ok)
            self.jsonpath()

    def addrlist(self):

        self.SHIP_TO.clear()
        self.BILL_TO.clear()
        self.DELIVER_TO.clear()

        # showup the mapping path
        df = self.df_addr
        file_name = self.json_list.currentItem().text().split('_')
        # name = file_name[0]+'@'+file_name[1]
        cust_key = self.config["default"]["cust_key"]
        ou_key = self.config["default"]["ou_key"]
        cust_id = file_name[cust_key]
        ou_id = file_name[ou_key]
        # print(cust_id,ou_id,'==============')

        addr_list = ['SHIP_TO', 'BILL_TO', 'DELIVER_TO']

        for use_code in addr_list:
            addr = df[(df['cust_id'] == cust_id) & (
                df['ou_id'] == ou_id) & (df['address_type'] == use_code)]
            # print(addr)
            mylist = getattr(self, use_code)

            for item in addr['address']:
                mylist.addItem(str(item))
            mylist.repaint()

    def set_currency_view(self, view):
        items = []
        df_currency = self.dsudb.get_table('currency')

        self.model = QtGui.QStandardItemModel(self)
        self.proxy = QSortFilterProxyModel(self)
        self.model.setHorizontalHeaderLabels(df_currency.columns)

        for idx, row in df_currency.iterrows():
            items = [QtGui.QStandardItem(field) for field in row]
            self.model.appendRow(items)

        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterKeyColumn(self.model.columnCount())

        view.horizontalHeader()
        view.setModel(self.proxy)
        view.setSortingEnabled(True)
        view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        for c in range(view.horizontalHeader().count()):
            view.horizontalHeader().setSectionResizeMode(c, QHeaderView.Stretch)

        view.horizontalHeader().setStretchLastSection(True)

    def set_custitem_view(self, view):

        text = self.customer_search.text()
        column = self.comboBox.currentText()

        query = 'SELECT * FROM cust_part_no WHERE {} LIKE \"%{}%\" LIMIT 100'.format(
            column, text)

        # self.model = QSqlQueryModel(self)
        # self.model.setQuery(query, self.db)
        # self.model.removeRow(0)
        df = self.dsudb.query(query)
        self.model = PandasModel(df)

        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterKeyColumn(self.model.columnCount()-1)

        view.horizontalHeader()
        view.setModel(self.proxy)
        view.setSortingEnabled(True)
        view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        for c in range(view.horizontalHeader().count()):
            view.horizontalHeader().setSectionResizeMode(c, QHeaderView.Stretch)

        view.horizontalHeader().setStretchLastSection(True)

    def set_wpgitem_view(self, view):

        text = self.wpgitem_customer_search.text()

        query = 'SELECT * FROM wpg_item WHERE wpg_part_no LIKE \"%{}%\" LIMIT 100'.format(
            text)

        # self.model = QSqlQueryModel(self)
        # self.model.setQuery(query, self.db)
        # self.model.removeRow(0)
        df = self.dsudb.query(query)
        self.model = PandasModel(df)

        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterKeyColumn(self.model.columnCount()-1)

        view.horizontalHeader()
        view.setModel(self.proxy)
        view.setSortingEnabled(True)
        view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        for c in range(view.horizontalHeader().count()):
            view.horizontalHeader().setSectionResizeMode(c, QHeaderView.Stretch)

        view.horizontalHeader().setStretchLastSection(True)

    def closeEvent(self, event):
        summary = 'Confirm Exit'
        question = '\nAre you sure you want to exit ?'
        result = QMessageBox.question(
            self, summary, question, QMessageBox.Yes | QMessageBox.No)

        event.ignore()

        if result == QtWidgets.QMessageBox.Yes:
            event.accept()
            self.dsudb.close()
            shutil.rmtree('./tmp', ignore_errors=True)


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('setting/logo.png'))
    app.setApplicationName("Order Editor")
    app.setStyle('Fusion')

    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(15, 15, 15))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QtGui.QPalette.Highlight,
                     QtGui.QColor(45, 82, 116).lighter())
    palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)

    app.setPalette(palette)
    Mywin = MyMainWindow()
    Mywin.show()
    start_msg = QMessageBox()
    star_info = ("\nDSU OrderEditor {}").format(Mywin.version)
    start_msg.setIconPixmap(QPixmap("setting/logo.png").scaled(
        QSize(50, 50), Qt.KeepAspectRatio))
    start_msg.setText(star_info)
    start_msg.addButton("Okay", QMessageBox.YesRole).animateClick(3*1000)
    start_msg.show()
    # QMessageBox.information(None, 'INFO', star_info, QtWidgets.QMessageBox.Ok)

    shutil.rmtree('./tmp', ignore_errors=True)
    sys.exit(app.exec_())
