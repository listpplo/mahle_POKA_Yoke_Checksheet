# IMPORTING ALL THE LIBRARIES
import sys
import os
import csv
from PyQt6 import QtGui, QtWidgets, QtCore
from test2 import Ui_MainWindow
from datetime import date , datetime, time
from time import sleep
from threading import Thread
import logging
from colorlog import ColoredFormatter
import pymcprotocol as pymc

# ********************************************************************
# CREATING LOGGER
log = logging.getLogger('example_logger')
log.setLevel(logging.DEBUG)
formatter = ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)

ch = logging.StreamHandler()
ch.setFormatter(formatter)
log.addHandler(ch)

# ********************************************************************

# LOADING SETTINGS FILE FOR PLC COMMUNICATION
global ip
global port
global DR1
global DR2
try:
    with open("csv/settings.csv") as file:
        reader = csv.reader(file)
        for data in reader:
            ip = data[0]
            port = int(data[1])
            DR1 = data[2]
            DR2 = data[3]

except Exception as e:
    log.critical(f"Unable to load the settings file -- {e}")

# ********************************************************************
# DATE-TIME SERVICE
def DateAndTime(self):

    AShift : time = time(hour=6,minute=0, second=0)
    BShift : time = time(hour=14,minute=30, second=0)
    CShift : time = time(hour=22,minute=30, second=0)
    initial_load : bool = False
    counter : int = 0
    _A : bool = True
    _B : bool = True
    _C : bool = True

    while self.run_dateTimeService:
        self.date_current = date.today()
        self.time_current = datetime.now().strftime("%H:%M:%S")
        self.time.display(self.time_current)
        self.time_production.display(self.time_current)
        self.label_date.display(f"{self.date_current}")
        self.label_date_production.display(f"{self.date_current}")
        current_time = datetime.now().time()
        
        if not initial_load : 
            if AShift > current_time or CShift < current_time and _B: 
                self.shift = "C"
                _C = True
                _A = False
                _B = False
                self.load_data_main_table()
                log.info(" Shift Change -- C")
                self._popup = True
            if AShift < current_time < BShift and _C:
                self.shift = "A"
                _A = True
                _B = False
                _C = False
                self.load_data_main_table()
                log.info("Shift Change -- A")
                self._popup = True
            if BShift < current_time < CShift and _A:
                self.shift = "B"
                _B = True
                _A = False
                _C = False
                self.load_data_main_table() 
                log.info("Shift Change -- B")
                self._popup  = True

        self.table.setHorizontalHeaderLabels(["Poke Yoke","Station", "Type", "Verification Method",f"SHIFT : {self.shift}"])
        self.header_font = self.table.horizontalHeader()
        self.header_font.font().setPointSize(20)
        if not self._adminstrator:
            self.comboBox.setCurrentText(self.shift)
            self.dateEdit.setDate(QtCore.QDate.currentDate())

        if self.checkBox.isChecked():
            if counter == 10:
                self.stackedWidget_5.setCurrentIndex(1)
            if counter == 20:
                self.stackedWidget_5.setCurrentIndex(0)
            if counter == 21:
                counter = 0 
            counter +=1

        sleep(1)
       
# ***************************************************************************

def plc_data_gather(self):

    try:
        plc = pymc.Type3E()
        plc.connect(ip, port)
    except Exception as e:
        log.critical(f"Unable To Connect To PLC Reason -- {e}")
        self.label_23.setText("Unable To Connect To PLC")
        self.label_23.setStyleSheet("background-color:red;\n"
                                    "color:white;\n")

    while self._go_plc :
        self.lcdNumber_2.display(0)
        try:
            with open("csv/target.csv") as file:
                reader = csv.reader(file)
                for data in reader:
                    target1 = int(data[1])
                    target2 = int(data[2])
        except Exception as e:
            target = 0
            log.debug(e)
    
        self.lcdNumber.display(target1)
        self.lcdNumber_2.display(target2)
        try:
            plc.connect(ip, port)
            self.label_23.setText("")
            self.label_23.setStyleSheet("background-color:None;\n"
                                    "color:white;\n")
        except Exception as e:
            log.critical(f"Unable To Connect To PLC Reason -- {e}")
        
        if plc._is_connected:
            count1 = plc.batchread_wordunits(headdevice=DR1, readsize=1)[0]
            count2 = plc.batchread_bitunits(headdevice=DR2, readsize=1)[0]
        else:
            count1 = 0
            count2 = 0
        self.lcdNumber_3.display(count1)
        self.lcdNumber_4.display(count2)

        sleep(5)

# ***************************************************************************
class LoginDialog(QtWidgets.QDialog):
    def __init__(self, a):
        super().__init__()
        self.a = a

        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 300, 150)

        layout = QtWidgets.QVBoxLayout(self)
        self.layout_id = QtWidgets.QHBoxLayout()
        self.layout_passwd = QtWidgets.QHBoxLayout()
        
        self.id = QtWidgets.QLabel(self)
        self.id.setText("ID              : ")
        self.username_input = QtWidgets.QLineEdit(self)
        self.username_input.setPlaceholderText("Username")
        self.layout_id.addWidget(self.id)
        self.layout_id.addWidget(self.username_input)
        layout.addLayout(self.layout_id)

        self.passwd = QtWidgets.QLabel(self)
        self.passwd.setText("Password : ")
        self.password_input = QtWidgets.QLineEdit(self)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.layout_passwd.addWidget(self.passwd)
        self.layout_passwd.addWidget(self.password_input)
        layout.addLayout(self.layout_passwd)

        login_button = QtWidgets.QPushButton("Login", self)
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button)

    def login(self,a):
        username = self.username_input.text()
        password = self.password_input.text()

        if username == "admin" and password == "admin":
            QtWidgets.QMessageBox.information(self, "Login Successful", "Welcome, {}!".format(username))
            self.accept()  # Close the login dialog
            icon2 = QtGui.QIcon()
            icon2.addPixmap(QtGui.QPixmap("assets/icons/login.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
            self.a.addPage.setIcon(icon2)
            self.a.lineEdit_2.setDisabled(False)
            self.a.lineEdit_3.setDisabled(False)
            self.a.lineEdit_6.setDisabled(False)
            self.a.lineEdit_10.setDisabled(False)
        else:
            QtWidgets.QMessageBox.warning(self, "Login Failed", "Invalid username or password. Please try again.")

# ***************************************************************************
# MAIN WINDOW CLASS FOR THE PROGRAM
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super().__init__()

        self.setupUi(self)
        self.tabWidget_5.tabBar().hide()
        self.stackedWidget_5.setCurrentIndex(0)
        self.checkBox.setChecked(True)
        
        # Setting up variables 
        self.load_initial_conditions : bool = False
        self.isFullScreen : bool = False
        self.date_current : str = ""
        self.time_current : str = ""
        self.run_dateTimeService : bool = True 
        self.shift : str = "" 
        self._adminstrator : bool = False
        self._popup : bool = False
        self._go_plc : bool = True

        # SETTING UP BUTTONS ACTIONS
        self.exit.clicked.connect(self.app_exit)
        self.full.clicked.connect(self.fullscreen)
        self.addPage.clicked.connect(self.addpage)
        self.updatePage_1.clicked.connect(self.updatePage)
        self.home_window.clicked.connect(self.homePage)
        self.settingsPage.clicked.connect(self.settingWindow)
        self.save_button_2.clicked.connect(self.save_conditions)
        self.pushButton_2.clicked.connect(self.save_data_checklist)
        self.pushButton_5.clicked.connect(lambda : self.stackedWidget_5.setCurrentIndex(1))
        self.pushButton_6.clicked.connect(lambda : self.stackedWidget_5.setCurrentIndex(1))
        self.pushButton_3.clicked.connect(lambda : self.stackedWidget_5.setCurrentIndex(0))
        self.pushButton_4.clicked.connect(lambda : self.stackedWidget_5.setCurrentIndex(0))
        self.save_button_3.clicked.connect(self.save_settings)

        # SETTING UP LOGOS
        self.label_6.setPixmap(QtGui.QPixmap("assets\logos\logo.PNG").scaled(50,50))
        self.label_7.setPixmap(QtGui.QPixmap("assets\logos\mahle.png").scaled(90,40))

        # DISABLING PLC PARAMETERS
        self.lineEdit_2.setDisabled(True)
        self.lineEdit_3.setDisabled(True)
        self.lineEdit_6.setDisabled(True)
        self.lineEdit_10.setDisabled(True)

        # SETTING UP HOME PAGE
        self.initial_index()

        self.tabWidget_5.setContentsMargins(0,0,0,0)
        self.setContentsMargins(0,0,0,0)

        # GENERATING MAIN TABLE
        self.gererate_main_table()

        # GENERATING ADD CONDITION TABLE 
        self.generate_add_condi_table()

        # LOADING THE UPDATE TABLE GENERATOR
        self.update_table_generator()

        self.generate_production_page()

        # SETTING UP DATE AND TIME SERVICE
        self.DateTime = Thread(target= lambda : DateAndTime(self))
        self.DateTime.start()

        self.plc_comm = Thread(target= lambda : plc_data_gather(self))
        self.plc_comm.start()

    # ****************************************************************************
    def generate_production_page(self):
        self.label_date_production = QtWidgets.QLCDNumber(parent=self.frame_update_5)
        self.label_date_production.setDigitCount(8)
        self.date_name_production  = QtWidgets.QLabel(parent=self.frame_update_5)
        self.date_name_production.setText("Date")
        self.horizontalLayout_belowTitle_production = QtWidgets.QHBoxLayout()
        self.horizontalLayout_belowTitle_production.setContentsMargins(0,2,0,2)
        
        self.label_date_production.setStyleSheet("font:20px;\n"
                                      "color:white;\n"
                                      "background-color:blue;\n"
                                      "border:1px soild black;\n")
        
        self.date_name_production.setStyleSheet("font:20px;\n"
                                      "background-color:yellow;\n"
                                      "border:1px soild black;\n"
                                      )
        
        self.time_name_production = QtWidgets.QLabel(parent=self.frame_update_5)
        self.time_name_production.setText("Time")
        self.time_name_production.setStyleSheet("font:20px;\n"
                                      "background-color:yellow;\n"
                                      "border:1px soild black;\n")
        
        self.time_production = QtWidgets.QLCDNumber(parent=self.frame_update_5)
        self.time_production.setDigitCount(8)
        self.time_production.setStyleSheet("font:20px;\n"
                                "color:white;\n"
                                "background-color:blue;\n"
                                "border:1px soild black;\n")
        
        
        self.date_name_production.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.time_name_production.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        self.date_name_production.setMinimumHeight(50)
        self.horizontalLayout_belowTitle_production.addWidget(self.date_name_production)
        self.horizontalLayout_belowTitle_production.addWidget(self.label_date_production)
        self.horizontalLayout_belowTitle_production.addWidget(self.time_name_production)
        self.horizontalLayout_belowTitle_production.addWidget(self.time_production)
        self.verticalLayout_7.addLayout(self.horizontalLayout_belowTitle_production)
        self.verticalLayout_7.addWidget(self.frame_6)

    # ****************************************************************************
    def update_table_generator(self) -> None:
        log.info("Generate Update Table Started")
        self.verticalLayout_checksheet = QtWidgets.QVBoxLayout()
        self.frame_5.setLayout(self.verticalLayout_checksheet)
        self.check_sheet_table = QtWidgets.QTableWidget(parent = self.frame_5)
        self.frame_5.setContentsMargins(0,0,0,0)
        self.check_sheet_table.setColumnCount(5)
        self.check_sheet_table.setColumnWidth(0,720)
        self.check_sheet_table.setColumnWidth(3,200)
        self.check_sheet_table.setWordWrap(True)
        self.check_sheet_table.resizeRowsToContents()
        font = QtGui.QFont()
        font.setPointSize(12)
        self.check_sheet_table.setFont(font)
        # self.pushButton.setDisabled(False)
        self.label_admin = QtWidgets.QLabel()
        self.label_admin.setStyleSheet("color:red;\n"
                                        "font-size:20px;\n")
        self.verticalLayout_checksheet.addWidget(self.label_admin)
        self.verticalLayout_checksheet.addWidget(self.check_sheet_table)
        for row in range(self.check_sheet_table.rowCount()):
            self.check_sheet_table.setRowHeight(row,15)
        self.check_sheet_table.setEditTriggers(QtWidgets.QTableWidget.EditTrigger.NoEditTriggers)
        header = self.check_sheet_table.horizontalHeader()
        for col in range(self.check_sheet_table.columnCount()):
            header_item = self.check_sheet_table.horizontalHeaderItem(col)
            if header_item is not None:
                header_item.setFont(QtGui.QFont("Arial", 20))
        self.check_sheet_table.setHorizontalHeaderLabels(["Poka Yoke","Station","Type","Verification Method","Condition"])

    # ****************************************************************************
    def generate_add_condi_table(self) -> None:
        # TABLE FOR ADDING ADITIONAL CONDITIONS
        log.info("Table Add Condition Started")
        self.table_add_condition = QtWidgets.QTableWidget(40,4, parent = self.add_frame)
        self.table_add_condition.setColumnWidth(0, 860)
        self.table_add_condition.setColumnWidth(3,200)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.table_add_condition.setFont(font)
        self.table_add_condition.setWordWrap(True)
        self.table_add_condition.resizeRowsToContents()

        # SETTING UP THE ROW HEIGHT 
        for row in range(0,self.table_add_condition.rowCount()):
            self.table_add_condition.setRowHeight(row,25)

        # ADDING WIDGET TO THE VERTICAL LAYOUT
        self.verticalLayout_4.addWidget(self.table_add_condition)
        self.verticalLayout_4.addLayout(self.horizontalLayout_6)
        self.save_button_2.setStyleSheet("QPushButton {\n"
"            background-color:rgb(0, 170, 0); \n"
"            border: 1px solid black;\n"
"            border-radius:20px;\n"
"        }\n"
"        QPushButton:hover {\n"
"            background-color: rgb(85, 255, 0);\n"
"        }")
       
        

    # ****************************************************************************
    def gererate_main_table(self) -> None:
        log.debug("Main Table Started")
        self.verticalLayout_A = QtWidgets.QVBoxLayout(self.frame_update_5)
        self.verticalLayout_A.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_A.setSpacing(2)
        self.verticalLayout_A.setObjectName("verticalLayout_A")
        self.table = QtWidgets.QTableWidget(parent = self.frame_update_5)
        self.table.setColumnCount(5)
        self.table.setColumnWidth(3,200)
        self.table.resizeRowsToContents()
        self.table.setWordWrap(True)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.table.setFont(font)
        self.table.setEditTriggers(QtWidgets.QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setColumnWidth(0,780)
        self.label_date = QtWidgets.QLCDNumber(parent=self.frame_update_5)
        self.label_date.setDigitCount(8)
        # font = QtGui.QFont()
        # font.setPointSize(20)
        # self.label_date.setFont(font)
        self.date_name  = QtWidgets.QLabel(parent=self.frame_update_5)
        self.date_name.setText("Date")
        self.table.setHorizontalHeaderLabels(["Poke Yoke","Station", "Type", "Verification Method","Condition"])

        for row in range(0,self.table.rowCount()):
            self.table.setRowHeight(row,25)

        header = self.table.horizontalHeader()
        for col in range(self.table.columnCount()):
            header_item = self.table.horizontalHeaderItem(col)
            if header_item is not None:
                header_item.setFont(QtGui.QFont("Arial", 14)) 

        self.horizontalLayout_belowTitle = QtWidgets.QHBoxLayout()
        self.horizontalLayout_belowTitle.setContentsMargins(0,2,0,2)

        self.label_date.setStyleSheet("font:50px;\n"
                                      "color:white;\n"
                                      "background-color:blue;\n"
                                      "border:1px soild black;\n")
        
        self.date_name.setStyleSheet("font:20px;\n"
                                      "background-color:yellow;\n"
                                      "border:1px soild black;\n")
        
        self.time_name = QtWidgets.QLabel(parent=self.frame_update_5)
        self.time_name.setText("Time")
        self.time_name.setStyleSheet("font:20px;\n"
                                      "background-color:yellow;\n"
                                      "border:1px soild black;\n")
        
        self.time = QtWidgets.QLCDNumber(parent=self.frame_update_5)
        self.time.setDigitCount(8)
        self.time.setStyleSheet("font:20px;\n"
                                "color:white;\n"
                                "background-color:blue;\n"
                                "border:1px soild black;\n")
        
        
        self.date_name.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.time_name.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        self.date_name.setMinimumHeight(50)
        self.horizontalLayout_belowTitle.addWidget(self.date_name)
        self.horizontalLayout_belowTitle.addWidget(self.label_date)
        self.horizontalLayout_belowTitle.addWidget(self.time_name)
        self.horizontalLayout_belowTitle.addWidget(self.time)

        
        # self.horizontalLayout_test.addWidget(self.button_left)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout(self.frame_update_5)
        self.horizontalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_11.setSpacing(0)
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")

        self.horizontalLayout_11.addWidget(self.pushButton_5, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.horizontalLayout_11.addWidget(self.table)
        self.horizontalLayout_11.addWidget(self.pushButton_6, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        self.verticalLayout_A.addLayout(self.horizontalLayout_belowTitle)
        self.verticalLayout_A.addLayout(self.horizontalLayout_11)
        self.indicator = QtWidgets.QLabel()
        self.verticalLayout_A.addWidget(self.indicator)
        self.frame_update_5.setLayout(self.verticalLayout_A)
                

    # ****************************************************************************
    # Saving the settings
    def save_settings(self):
        _is_saved = True
        lst : list = []
        lst.append(self.lineEdit_2.text())
        lst.append(int(self.lineEdit_3.text()))
        lst.append(self.lineEdit_6.text())
        lst.append(self.lineEdit_10.text())

        with open("csv/settings.csv","w+",newline="") as file:
            writer = csv.writer(file)
            writer.writerow(lst)
        
        lst.clear()

        lst.append(date.today())
        lst.append(self.spinBox.value())
        lst.append(self.spinBox_2.value())
        lst.append(self.shift)

        with open("csv/target.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(lst)

    # ****************************************************************************

    def load_data_settings(self):
        try:
            with open("csv/target.csv") as file:
                reader = csv.reader(file)
                for item in reader:
                    self.spinBox.setValue(int(item[1]))
                    self.spinBox_2.setValue(int(item[2]))
            
            with open("csv/settings.csv") as file:
                reader = csv.reader(file)
                for item in reader:
                    self.lineEdit_2.setText(item[0])
                    self.lineEdit_3.setText(item[1])
                    self.lineEdit_6.setText(item[2])
                    self.lineEdit_10.setText(item[3])
        except Exception as e:
            log.critical(e)


    # ****************************************************************************
    # Saving the checklist form
    def save_data_checklist(self) -> None:
        log.info("Saving the Values form checklist")
        data =  []

        for row in range(self.check_sheet_table.rowCount()):
            data_temp =  []
            for coloumn in range(self.check_sheet_table.columnCount()):
                if coloumn > 3:
                    combo_box_widget = self.check_sheet_table.cellWidget(row, 4)  
                    selected_item = combo_box_widget.currentText()
                    data_temp.append(selected_item)
                else:
                    item = self.check_sheet_table.item(row, coloumn)
                    if item is None:
                        data_temp.append("")
                    else:
                        data_temp.append(item.text())

            data.append(data_temp)

        year = self.dateEdit.date().year()
        month = self.dateEdit.date().month()
        date_1  = self.dateEdit.date().toPyDate()

        dir = os.listdir()
        folder = [items for items in dir if os.path.isdir(items)]
        if "csv" in folder:
            log.critical("CSV Folder Found")
        else:
            os.mkdir("csv")
            log.debug("Making csv Folder")

        os.chdir("csv")

        dir = os.listdir()
        folder = [items for items in dir if os.path.isdir(items)]
        if f"{year}" in folder:
            log.debug("Folder Found Year")
        else:
            log.critical("Unable to find Year Folder")
            log.info("Making Folder ... ")
            os.mkdir(f"{year}")
        
        os.chdir(f"{year}")
        dir = os.listdir()
        folder = [item for item in dir if os.path.isdir(item)]
        if f"{month}" in folder:
            log.debug("Folder Found Month")
        else:
            log.critical("Unable to find Year Folder")
            log.info("Making Folder ... ")
            os.mkdir(f"{month}")

        with open(f"{month}/{date_1}-{self.shift}.csv","w+", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(data)
            log.info("Data Saved From Checklist")
        
        
        os.chdir("..")
        os.chdir("..")

    # ****************************************************************************
    def load_data_checksheet(self) -> None:
        if self._adminstrator:
            self.label_admin.setText("You are Admin ... You Can Edit Previous Data ")
            
        if not self._adminstrator:
            self.label_admin.setText("You Can Only Edit The Current Data ...")

        log.debug("Loading Data in the checklist")
        try:
            with open("csv/Poka-yoke-list.csv") as file:
                try:
                    reader = csv.reader(file)
                except Exception as e:
                    log.critical("Unable to find the conditon CSV file")

                row_number : int = 0
                l : int = 0

                for data in reader:
                    l+=1
        except Exception as e:
            log.critical(e)


        font = QtGui.QFont()
        font.setPointSize(12)
        self.check_sheet_table.setRowCount(l)
        self.check_sheet_table.setFont(font)
        try:
            with open("csv/Poka-yoke-list.csv") as file:
                try:
                    reader = csv.reader(file)
                except Exception as e:
                    log.critical(e)

                for row in reader:
                    col_num : int = 0
                    for data in row:
                        if data != "":
                            try:
                                item = QtWidgets.QTableWidgetItem(data)
                                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                                self.check_sheet_table.setItem(row_number,col_num, item)
                            except Exception as e:
                                log.debug(f"Error -- {e}")
                        else:
                            pass
                        col_num +=1

                    item_combo = QtWidgets.QComboBox()
                    item_combo.addItems(["N/A","OK", "NG"])
                    item_combo.setStyleSheet("font-size:15px;")
                    self.check_sheet_table.setCellWidget(row_number,4,item_combo)
                    row_number +=1
                
                self.check_sheet_table.setWordWrap(True)
                self.check_sheet_table.update()
        except Exception as e:
            log.critical(e)

    # ****************************************************************************
    # FUNCTION TO ADD DATA TO THE MAIN TABLE
    def load_data_main_table(self) -> None :
        log.debug('Loading Data In The Main Table')
        year = datetime.now().year
        month = datetime.now().month
        date_current = date.today()
        shift = self.shift
        try:
            with open(f"csv/{year}/{month}/{date_current}-{shift}.csv") as file:
                try:
                    reader = csv.reader(file)
                except Exception as e:
                    log.critical("Unable to find the conditon CSV file")
                
                l : int = 0

                for data in reader:
                    l += 1
                    
                self.table.setRowCount(l)

            with open(f"csv/{year}/{month}/{date_current}-{shift}.csv") as file:
                try:
                    reader = csv.reader(file)
                except Exception as e:
                    log.critical("Unable to find the conditon CSV file")

                row_number : int = 0
                
                for row in reader:
                    col_num : int = 0
                    for data in row:
                        try:
                            if col_num == 4:
                                if data == "OK":
                                    item = QtWidgets.QTableWidgetItem(data)
                                    item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                                    item.setBackground(QtGui.QColor(0,255,0))
                                    self.table.setItem(row_number,col_num, item)
                                elif data == "NG":
                                    item = QtWidgets.QTableWidgetItem(data)
                                    item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                                    item.setBackground(QtGui.QColor(255,0,0))
                                    self.table.setItem(row_number,col_num, item)
                                else :
                                    item = QtWidgets.QTableWidgetItem(data)
                                    item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                                    item.setBackground(QtGui.QColor(255,255,0))
                                    self.table.setItem(row_number,col_num, item)  
                            else:
                                item = QtWidgets.QTableWidgetItem(data)
                                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                                self.table.setItem(row_number,col_num, item)

                        except Exception as e:
                            log.debug(f"Error -- {e}")
                        col_num +=1
                    row_number +=1

            self.table.setWordWrap(True)
            # self.table.resizeRowsToContents()
            self.table.update()
            self.indicator.setText("")
            self.indicator.setStyleSheet("background-color:None;\n"
                                         "color:white;\n")
        except Exception as e:
            log.critical(e)
            self.table.clear()
            self.label_23.setStyleSheet("font-size:12px;\n"
                                        "background-color:red;\n"
                                         "color:white;\n")
            self.indicator.setText(f"Please Update The Data Of {date_current} Of Shift {shift}")
            self.indicator.setStyleSheet("font-size:12px;\n"
                                        "background-color:red;\n"
                                         "color:white;\n")
    
    # ****************************************************************************

    # FUNCTION TO ADD DATA TO ADD CONDITION TABLE
    def load_conditions_add_table(self) -> None:
        header = self.table_add_condition.horizontalHeader()
        for col in range(self.table_add_condition.columnCount()):
            header_item = self.table_add_condition.horizontalHeaderItem(col)
            if header_item is not None:
                header_item.setFont(QtGui.QFont("Arial", 12))
        self.table_add_condition.setHorizontalHeaderLabels(["Poka Yoke","Station","Type","Verification Method"])
        log.debug("Loading The add Condition Table Data 👍")
        with open("csv/Poka-yoke-list.csv") as file:
            reader = csv.reader(file)
            row_nummber : int = 0
            
            for row in reader:
                col_num : int = 0
                for data in row:
                    try:
                        item = QtWidgets.QTableWidgetItem(data)
                        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                        self.table_add_condition.setItem(row_nummber,col_num, item) 
                    except Exception as e:
                        log.debug(f"Error -- {e}")
                    col_num +=1
                row_nummber +=1

        self.table_add_condition.update()
        self.table_add_condition.setWordWrap(True)

    # ****************************************************************************
    # SAVING CONDITIONS FROM THE SAVE TABLE
    def save_conditions(self) -> None:
        lst_main : str = []
        for row in range(self.table_add_condition.rowCount()):
            lst_data : str = []
            for column in range(self.table_add_condition.columnCount()):
                value = self.table_add_condition.item(row, column)
                if value is not None and value != "":
                    lst_data.append(value.text()) 
            if lst_data == [""] or lst_data == ["",""] or lst_data == ["","",""] or lst_data == ["","","",""] :
                pass
            else:
                lst_main.append(lst_data)

        try:
            with open("csv/Poka-yoke-list.csv","w+", newline='') as file:
                writer = csv.writer(file)
                for data in lst_main:
                    if data != []:
                        writer.writerow(data) 
            log.info("Additional Condition Saved 😊")
        except Exception as e:
            log.critical(f"Unable To Save Additional Conditions 😢 -- Reason -- {e}")    
        
        # LOADING THE UPDATED VAUES ON SAVING IN THE MAIN TABLE
        self.load_conditions_add_table()
        self.table_add_condition.update()   
        
    # ****************************************************************************
    # APP EXIT
    def app_exit(self) -> None:
        if self._adminstrator:
            logout = QtWidgets.QMessageBox.question(self,
                                         "Logout",
                                         "Want To Logout",
                                         QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.Cancel)
            if logout == QtWidgets.QMessageBox.StandardButton.Ok:
                self._adminstrator = False 
                self.label_admin.setText("You Can Only Edit The Current Data ...")
                icon3 = QtGui.QIcon()
                icon3.addPixmap(QtGui.QPixmap("assets/icons/icons8-login-64.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
                self.addPage.setIcon(icon3)
                self.addPage.setIconSize(QtCore.QSize(40,40))
                self.homePage()
                self.lineEdit_2.setDisabled(True)
                self.lineEdit_3.setDisabled(True)
                self.lineEdit_6.setDisabled(True)
                self.lineEdit_10.setDisabled(True)

        else :
            log.debug("Closing Applicaton")
            self.close()

    # ****************************************************************************
    # FULL SCREEN MODE
    def fullscreen(self) -> None:
        if not self.isFullScreen:
            self.showFullScreen()
            self.isFullScreen =True
            self.full.setStyleSheet("background-color:rgb(224, 98, 255);\n")
            log.info("Full Screen Mode Enabled")
        else :
            self.showMaximized()
            self.isFullScreen = False
            self.full.setStyleSheet("QPushButton {\n"
"            background-color:rgb(160, 132, 232); \n"
"            border: None;\n"
"            padding:4px;\n"
"        }\n"
"        QPushButton:hver {\n"
"            \n"
"    background-color:rgb(224, 98, 255);\n"
"        }")
            log.info("Maximised Mode is Enabled")

    # ****************************************************************************
    # SETTING UP INITIAL INDEX
    def initial_index(self) -> None:
        self.tabWidget_5.setCurrentIndex(0)
        self.home_window.setStyleSheet("background-color:rgb(224, 98, 255);\n")
        self.addPage.setStyleSheet("QPushButton {\n"
"            background-color:rgb(160, 132, 232); \n"
"            border: None;\n"
"            padding:4px;\n"
"        }\n"
"        QPushButton:hver {\n"
"            \n"
"    background-color:rgb(224, 98, 255);\n"
"        }")
        self.updatePage_1.setStyleSheet("QPushButton {\n"
"            background-color:rgb(160, 132, 232); \n"
"            border: None;\n"
"            padding:4px;\n"
"        }\n"
"        QPushButton:hover {\n"
"            \n"
"    background-color:rgb(224, 98, 255);\n"
"        }")
        self.settingsPage.setStyleSheet("QPushButton {\n"
"            background-color:rgb(160, 132, 232); \n"
"            border: None;\n"
"            padding:4px;\n"
"        }\n"
"        QPushButton:hover {\n"
"            \n"
"    background-color:rgb(224, 98, 255);\n"
"        }")
        self.frame_3.update()
        log.info("Initial Index Change")
    
    # ****************************************************************************
    # ADD PAGE TAB WIDGET
    def addpage(self) -> None:
        self.tabWidget_5.setCurrentIndex(1)
        self.addPage.setStyleSheet("background-color:rgb(224, 98, 255);\n")
        self.updatePage_1.setStyleSheet("QPushButton {\n"
"            background-color:rgb(160, 132, 232); \n"
"            border: None;\n"
"            padding:4px;\n"
"        }\n"
"        QPushButton:hover {\n"
"            \n"
"    background-color:rgb(224, 98, 255);\n"
"        }")
        self.settingsPage.setStyleSheet("QPushButton {\n"
"            background-color:rgb(160, 132, 232); \n"
"            border: None;\n"
"            padding:4px;\n"
"        }\n"
"        QPushButton:hover {\n"
"            \n"
"    background-color:rgb(224, 98, 255);\n"
"        }")
        self.home_window.setStyleSheet("QPushButton {\n"
"            background-color:rgb(160, 132, 232); \n"
"            border: None;\n"
"            padding:4px;\n"
"        }\n"
"        QPushButton:hover {\n"
"            \n"
"    background-color:rgb(224, 98, 255);\n"
"        }")
        
        self.frame_3.update()
        if not self._adminstrator:
            self.table_add_condition.clear()
            self.login = LoginDialog(self)
            if self.login.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                self.load_conditions_add_table()
                self._adminstrator = True
            else:
                self.homePage()
        log.info("Changing To Add Page")
    
    # ****************************************************************************
    # UPDATE PAGE TAB WIDGET
    def updatePage(self) -> None:
        self.tabWidget_5.setCurrentIndex(2)
        log.info("Changing To Update Page")
        self.updatePage_1.setStyleSheet("background-color:rgb(224, 98, 255);\n")
        self.settingsPage.setStyleSheet("QPushButton {\n"
"            background-color:rgb(160, 132, 232); \n"
"            border: None;\n"
"            padding:4px;\n"
"        }\n"
"        QPushButton:hover {\n"
"            \n"
"    background-color:rgb(224, 98, 255);\n"
"        }")
        self.home_window.setStyleSheet("QPushButton {\n"
"            background-color:rgb(160, 132, 232); \n"
"            border: None;\n"
"            padding:4px;\n"
"        }\n"
"        QPushButton:hover {\n"
"            \n"
"    background-color:rgb(224, 98, 255);\n"
"        }")
        self.addPage.setStyleSheet("QPushButton {\n"
"            background-color:rgb(160, 132, 232); \n"
"            border: None;\n"
"            padding:4px;\n"
"        }\n"
"        QPushButton:hover {\n"
"            \n"
"    background-color:rgb(224, 98, 255);\n"
"        }")
        self.frame_3.update()
        self.load_data_checksheet()

    # ****************************************************************************
    # HOME PAGE TAB WIDGET
    def homePage(self) -> None:
        self.tabWidget_5.setCurrentIndex(0)
        self.load_data_main_table()
        self.home_window.setStyleSheet("background-color:rgb(224, 98, 255);\n")
        self.settingsPage.setStyleSheet("QPushButton {\n"
"            background-color:rgb(160, 132, 232); \n"
"            border: None;\n"
"            padding:4px;\n"
"        }\n"
"        QPushButton:hover {\n"
"            \n"
"    background-color:rgb(224, 98, 255);\n"
"        }")
        self.updatePage_1.setStyleSheet("QPushButton {\n"
"            background-color:rgb(160, 132, 232); \n"
"            border: None;\n"
"            padding:4px;\n"
"        }\n"
"        QPushButton:hover {\n"
"            \n"
"    background-color:rgb(224, 98, 255);\n"
"        }")
        self.addPage.setStyleSheet("QPushButton {\n"
"            background-color:rgb(160, 132, 232); \n"
"            border: None;\n"
"            padding:4px;\n"
"        }\n"
"        QPushButton:hover {\n"
"            \n"
"    background-color:rgb(224, 98, 255);\n"
"        }")
        self.frame_3.update()
        log.info("Changing To Home Page")

    # ****************************************************************************
    # SETTING WINDOW TAB WIDGET
    def settingWindow(self) -> None :
        self.tabWidget_5.setCurrentIndex(3)
        self.load_data_settings()
        self.settingsPage.setStyleSheet("background-color:rgb(224, 98, 255);\n")
        self.updatePage_1.setStyleSheet("QPushButton {\n"
"            background-color:rgb(160, 132, 232); \n"
"            border: None;\n"
"            padding:4px;\n"
"        }\n"
"        QPushButton:hover {\n"
"            \n"
"    background-color:rgb(224, 98, 255);\n"
"        }")
        self.home_window.setStyleSheet("QPushButton {\n"
"            background-color:rgb(160, 132, 232); \n"
"            border: None;\n"
"            padding:4px;\n"
"        }\n"
"        QPushButton:hover {\n"
"            \n"
"    background-color:rgb(224, 98, 255);\n"
"        }")
        self.addPage.setStyleSheet("QPushButton {\n"
"            background-color:rgb(160, 132, 232); \n"
"            border: None;\n"
"            padding:4px;\n"
"        }\n"
"        QPushButton:hover {\n"
"            \n"
"    background-color:rgb(224, 98, 255);\n"
"        }")
        self.frame_3.update()
        log.info("ChanginTo Settings Page")

    # ****************************************************************************
    def closeEvent(self, event):
            close_msg = QtWidgets.QMessageBox()
            close_msg.setBaseSize(400,300)
            close_msg.setWindowTitle("Quit")
            close_msg.setText("Want To Quit ? ")
            font = QtGui.QFont()
            font.setPointSize(12)
            close_msg.setFont(font)
            close_msg.addButton(QtWidgets.QMessageBox.StandardButton.Ok)
            close_msg.addButton(QtWidgets.QMessageBox.StandardButton.Cancel)
            if close_msg.exec() == QtWidgets.QMessageBox.StandardButton.Ok:
                event.accept()
                self.run_dateTimeService = False 
                self._go_plc = False
            else:
                event.ignore()
# ****************************************************************************
# Starting main app
log.info("App Started")
app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()