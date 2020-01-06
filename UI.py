# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class PhotoViewer(QtWidgets.QGraphicsView):
    photoClicked = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30,30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def hasPhoto(self):
        return not self._empty

    # def fitInView(self, scale=True):
    #     rect = QtCore.QRectF(self._photo.pixmap().rect())
    #     if not rect.isNull():
    #         self.setSceneRect(rect)
    #         if self.hasPhoto():
    #             unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
    #             self.scale(1 / unity.width(), 1 / unity.height())
    #             viewrect = self.viewport().rect()
    #             scenerect = self.transform().mapRect(rect)
    #             factor = min(viewrect.width() / scenerect.width(),
    #                          viewrect.height() / scenerect.height())
    #             self.scale(factor, factor)
    #         self._zoom = 0

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())
        self.fitInView(self._photo)

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView(self._photo)
            else:
                self._zoom = 0

    def toggleDragMode(self):
        if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event):
        if self._photo.isUnderMouse():
            self.photoClicked.emit(self.mapToScene(event.pos()).toPoint())
        super(PhotoViewer, self).mousePressEvent(event)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("Order Editor")
        MainWindow.resize(1440, 803)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setContentsMargins(5, 5, 5, 5)
        self.horizontalLayout.setSpacing(1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.imagelayout = QtWidgets.QHBoxLayout()
        self.imagelayout.setObjectName("imagelayout")
        # self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        # self.scrollArea.setWidgetResizable(True)
        # self.scrollArea.setObjectName("scrollArea")
        # self.scrollAreaWidgetContents = QtWidgets.QWidget()
        # self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 711, 740))
        # self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        # self.scrollAreaContentsLayout = QtWidgets.QHBoxLayout(self.scrollAreaWidgetContents)
        # self.scrollAreaContentsLayout.setContentsMargins(0, 0, 0, 0)
        # self.scrollAreaContentsLayout.setObjectName("scrollAreaContentsLayout")
        # self.img_view = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.img_view.sizePolicy().hasHeightForWidth())
        # self.img_view.setSizePolicy(sizePolicy)
        # self.img_view.setText("")
        # self.img_view.setScaledContents(True)
        # self.img_view.setAlignment(QtCore.Qt.AlignCenter)
        # self.img_view.setObjectName("img_view")
        # self.scrollAreaContentsLayout.addWidget(self.img_view)
        # self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        # self.imagelayout.addWidget(self.scrollArea)
        self.img_view = PhotoViewer(self)
        self.imagelayout.addWidget(self.img_view)
        self.horizontalLayout.addLayout(self.imagelayout)
        self.editorlayout = QtWidgets.QHBoxLayout()
        self.editorlayout.setObjectName("editorlayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.json_tab = QtWidgets.QWidget()
        self.json_tab.setObjectName("json_tab")
        self.json_tabLayout = QtWidgets.QVBoxLayout(self.json_tab)
        self.json_tabLayout.setContentsMargins(0, 0, 0, 0)
        self.json_tabLayout.setSpacing(5)
        self.json_tabLayout.setObjectName("json_tabLayout")
        self.jsonLayout_top = QtWidgets.QVBoxLayout()
        self.jsonLayout_top.setContentsMargins(5, -1, 5, -1)
        self.jsonLayout_top.setSpacing(0)
        self.jsonLayout_top.setObjectName("jsonLayout_top")
        self.order_nameLayout = QtWidgets.QHBoxLayout()
        self.order_nameLayout.setContentsMargins(-1, 5, -1, 0)
        self.order_nameLayout.setSpacing(20)
        self.order_nameLayout.setObjectName("order_nameLayout")
        self.order_name = QtWidgets.QLabel(self.json_tab)
        self.order_name.setObjectName("order_name")
        self.order_nameLayout.addWidget(self.order_name)
        self.prev_btn = QtWidgets.QPushButton(self.json_tab)
        self.prev_btn.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.prev_btn.sizePolicy().hasHeightForWidth())
        self.prev_btn.setSizePolicy(sizePolicy)
        self.prev_btn.setMinimumSize(QtCore.QSize(0, 0))
        self.prev_btn.setMaximumSize(QtCore.QSize(30, 15))
        self.prev_btn.setObjectName("prev_btn")
        self.order_nameLayout.addWidget(self.prev_btn)
        self.img_count = QtWidgets.QLabel(self.json_tab)
        self.img_count.setAlignment(QtCore.Qt.AlignCenter)
        self.img_count.setObjectName("img_count")
        self.order_nameLayout.addWidget(self.img_count)
        self.next_btn = QtWidgets.QPushButton(self.json_tab)
        self.next_btn.setMaximumSize(QtCore.QSize(30, 15))
        self.next_btn.setObjectName("next_btn")
        self.order_nameLayout.addWidget(self.next_btn)
        self.order_nameLayout.setStretch(0, 40)
        self.order_nameLayout.setStretch(2, 1)
        self.order_nameLayout.setStretch(3, 1)
        self.jsonLayout_top.addLayout(self.order_nameLayout)
        self.json_nameLayout = QtWidgets.QHBoxLayout()
        self.json_nameLayout.setSpacing(0)
        self.json_nameLayout.setObjectName("json_nameLayout")
        self.json_name = QtWidgets.QLabel(self.json_tab)
        self.json_name.setObjectName("json_name")
        self.json_nameLayout.addWidget(self.json_name)
        self.jsonLayout_top.addLayout(self.json_nameLayout)
        self.jsonLayout_top.setStretch(0, 1)
        self.jsonLayout_top.setStretch(1, 1)
        self.json_tabLayout.addLayout(self.jsonLayout_top)
        self.jsonLayout_center = QtWidgets.QGridLayout()
        self.jsonLayout_center.setContentsMargins(5, 0, 5, 0)
        self.jsonLayout_center.setSpacing(5)
        self.jsonLayout_center.setObjectName("jsonLayout_center")
        self.treeWidget = QtWidgets.QTreeWidget(self.json_tab)
        self.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeWidget.setAcceptDrops(False)
        self.treeWidget.setDragDropOverwriteMode(False)
        self.treeWidget.setDragDropMode(QtWidgets.QAbstractItemView.NoDragDrop)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.header().setDefaultSectionSize(250)
        self.jsonLayout_center.addWidget(self.treeWidget, 0, 0, 2, 1)
        self.save_btn = QtWidgets.QPushButton(self.json_tab)
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.save_btn.setFont(font)
        self.save_btn.setObjectName("save_btn")
        self.jsonLayout_center.addWidget(self.save_btn, 2, 0, 1, 1)
        self.json_list = QtWidgets.QListWidget(self.json_tab)
        self.json_list.setObjectName("json_list")
        self.jsonLayout_center.addWidget(self.json_list, 0, 1, 3, 1)
        self.jsonLayout_center.setColumnStretch(0, 6)
        self.jsonLayout_center.setColumnStretch(1, 3)
        self.json_tabLayout.addLayout(self.jsonLayout_center)
        self.jsonLayout_bottom = QtWidgets.QGridLayout()
        self.jsonLayout_bottom.setContentsMargins(5, -1, 5, 5)
        self.jsonLayout_bottom.setHorizontalSpacing(5)
        self.jsonLayout_bottom.setVerticalSpacing(0)
        self.jsonLayout_bottom.setObjectName("jsonLayout_bottom")
        self.SHIP_TO = QtWidgets.QListWidget(self.json_tab)
        self.SHIP_TO.setObjectName("SHIP_TO")
        self.jsonLayout_bottom.addWidget(self.SHIP_TO, 1, 0, 1, 1)
        self.billaddr_label = QtWidgets.QLabel(self.json_tab)
        self.billaddr_label.setAlignment(QtCore.Qt.AlignCenter)
        self.billaddr_label.setObjectName("billaddr_label")
        self.jsonLayout_bottom.addWidget(self.billaddr_label, 0, 1, 1, 1)
        self.deliveraddr_label = QtWidgets.QLabel(self.json_tab)
        self.deliveraddr_label.setAlignment(QtCore.Qt.AlignCenter)
        self.deliveraddr_label.setObjectName("deliveraddr_label")
        self.jsonLayout_bottom.addWidget(self.deliveraddr_label, 0, 2, 1, 1)
        self.shipaddr_label = QtWidgets.QLabel(self.json_tab)
        self.shipaddr_label.setAlignment(QtCore.Qt.AlignCenter)
        self.shipaddr_label.setObjectName("shipaddr_label")
        self.jsonLayout_bottom.addWidget(self.shipaddr_label, 0, 0, 1, 1)
        self.BILL_TO = QtWidgets.QListWidget(self.json_tab)
        self.BILL_TO.setObjectName("BILL_TO")
        self.jsonLayout_bottom.addWidget(self.BILL_TO, 1, 1, 1, 1)
        self.DELIVER_TO = QtWidgets.QListWidget(self.json_tab)
        self.DELIVER_TO.setObjectName("DELIVER_TO")
        self.jsonLayout_bottom.addWidget(self.DELIVER_TO, 1, 2, 1, 1)
        self.jsonLayout_bottom.setColumnStretch(0, 3)
        self.jsonLayout_bottom.setColumnStretch(1, 3)
        self.jsonLayout_bottom.setColumnStretch(2, 3)
        self.jsonLayout_bottom.setRowStretch(0, 1)
        self.jsonLayout_bottom.setRowStretch(1, 10)
        self.json_tabLayout.addLayout(self.jsonLayout_bottom)
        self.json_tabLayout.setStretch(0, 1)
        self.json_tabLayout.setStretch(1, 10)
        self.json_tabLayout.setStretch(2, 4)
        self.tabWidget.addTab(self.json_tab, "")
        self.customeritem_tab = QtWidgets.QWidget()
        self.customeritem_tab.setObjectName("customeritem_tab")
        self.customeritem_tabLayout = QtWidgets.QVBoxLayout(self.customeritem_tab)
        self.customeritem_tabLayout.setContentsMargins(5, 5, 5, 5)
        self.customeritem_tabLayout.setObjectName("customeritem_tabLayout")
        self.customeritemLayout_top = QtWidgets.QHBoxLayout()
        self.customeritemLayout_top.setContentsMargins(-1, 5, -1, -1)
        self.customeritemLayout_top.setObjectName("customeritemLayout_top")
        self.search_label = QtWidgets.QLabel(self.customeritem_tab)
        self.search_label.setObjectName("search_label")
        self.customeritemLayout_top.addWidget(self.search_label)
        self.customer_search = QtWidgets.QLineEdit(self.customeritem_tab)
        self.customer_search.setObjectName("customer_search")
        self.customeritemLayout_top.addWidget(self.customer_search)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.customeritemLayout_top.addItem(spacerItem)
        self.customer_load_btn = QtWidgets.QPushButton(self.customeritem_tab)
        self.customer_load_btn.setObjectName("customer_load_btn")
        self.customeritemLayout_top.addWidget(self.customer_load_btn)
        self.customeritem_tabLayout.addLayout(self.customeritemLayout_top)
        self.customer_view = QtWidgets.QTableView(self.customeritem_tab)
        self.customer_view.setObjectName("customer_view")
        self.customeritem_tabLayout.addWidget(self.customer_view)
        self.tabWidget.addTab(self.customeritem_tab, "")
        self.currency_tab = QtWidgets.QWidget()
        self.currency_tab.setObjectName("currency_tab")
        self.currency_tabLayout = QtWidgets.QHBoxLayout(self.currency_tab)
        self.currency_tabLayout.setContentsMargins(5, 5, 5, 5)
        self.currency_tabLayout.setObjectName("currency_tabLayout")
        self.currency_view = QtWidgets.QTableView(self.currency_tab)
        self.currency_view.setObjectName("currency_view")
        self.currency_tabLayout.addWidget(self.currency_view)
        self.tabWidget.addTab(self.currency_tab, "")
        self.editorlayout.addWidget(self.tabWidget)
        self.horizontalLayout.addLayout(self.editorlayout)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1440, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.menuFile.setTearOffEnabled(False)
        self.menuFile.setObjectName("menuFile")
        self.menuControl = QtWidgets.QMenu(self.menubar)
        self.menuControl.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.menuControl.setObjectName("menuControl")
        MainWindow.setMenuBar(self.menubar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.actionOpen_Image = QtWidgets.QAction(MainWindow)
        self.actionOpen_Image.setCheckable(False)
        self.actionOpen_Image.setObjectName("actionOpen_Image")
        self.actionOpen_Json = QtWidgets.QAction(MainWindow)
        self.actionOpen_Json.setObjectName("actionOpen_Json")
        self.action_Close = QtWidgets.QAction(MainWindow)
        self.action_Close.setObjectName("action_Close")
        self.actionNext_Page = QtWidgets.QAction(MainWindow)
        self.actionNext_Page.setObjectName("actionNext_Page")
        self.actionPrev_Page = QtWidgets.QAction(MainWindow)
        self.actionPrev_Page.setObjectName("actionPrev_Page")
        self.action_Save = QtWidgets.QAction(MainWindow)
        self.action_Save.setObjectName("action_Save")
        self.actionDelete_line = QtWidgets.QAction(MainWindow)
        self.actionDelete_line.setObjectName("actionDelete_line")
        self.menuFile.addAction(self.actionOpen_Image)
        self.menuFile.addAction(self.actionOpen_Json)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.action_Save)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.action_Close)
        self.menuControl.addAction(self.actionPrev_Page)
        self.menuControl.addAction(self.actionNext_Page)
        self.menuControl.addSeparator()
        self.menuControl.addAction(self.actionDelete_line)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuControl.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Order Editor"))
        self.order_name.setText(_translate("MainWindow", "Order Name:"))
        self.prev_btn.setText(_translate("MainWindow", "←"))
        self.prev_btn.setShortcut(_translate("MainWindow", "Left"))
        self.img_count.setText(_translate("MainWindow", "0/0"))
        self.next_btn.setText(_translate("MainWindow", "→"))
        self.next_btn.setShortcut(_translate("MainWindow", "Right"))
        self.json_name.setText(_translate("MainWindow", "Json   Name:"))
        self.treeWidget.headerItem().setText(0, _translate("MainWindow", "key"))
        self.treeWidget.headerItem().setText(1, _translate("MainWindow", "value"))
        self.save_btn.setText(_translate("MainWindow", "&Save Json"))
        self.save_btn.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.billaddr_label.setText(_translate("MainWindow", "billAddr"))
        self.deliveraddr_label.setText(_translate("MainWindow", "deliverAddr"))
        self.shipaddr_label.setText(_translate("MainWindow", "shipAddr"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.json_tab), _translate("MainWindow", "Json editor"))
        self.search_label.setText(_translate("MainWindow", "Search:"))
        self.customer_load_btn.setText(_translate("MainWindow", "Load Data"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.customeritem_tab), _translate("MainWindow", "Customer item"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.currency_tab), _translate("MainWindow", "Currency"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuControl.setTitle(_translate("MainWindow", "Control"))
        self.actionOpen_Image.setText(_translate("MainWindow", "Open Image"))
        self.actionOpen_Image.setShortcut(_translate("MainWindow", "Ctrl+I"))
        self.actionOpen_Json.setText(_translate("MainWindow", "Open Json"))
        self.actionOpen_Json.setShortcut(_translate("MainWindow", "Ctrl+J"))
        self.action_Close.setText(_translate("MainWindow", "Clsoe"))
        self.actionNext_Page.setText(_translate("MainWindow", "Next Page"))
        self.actionNext_Page.setShortcut(_translate("MainWindow", "Down"))
        self.actionPrev_Page.setText(_translate("MainWindow", "Prev Page"))
        self.actionPrev_Page.setShortcut(_translate("MainWindow", "Up"))
        self.action_Save.setText(_translate("MainWindow", "Save"))
        self.action_Save.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionDelete_line.setText(_translate("MainWindow", "Delete line"))
        self.actionDelete_line.setShortcut(_translate("MainWindow", "Ctrl+D"))



