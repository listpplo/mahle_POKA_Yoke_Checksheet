# IMPORTING ALL THE LIBRARIES
import sys
import os
import csv
from PyQt6 import QtGui, QtWidgets, QtCore
from test import Ui_MainWindow
from datetime import date , datetime, time
from time import sleep
from threading import Thread
import logging
from colorlog import ColoredFormatter

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

# ********************************************************************
# DATE-TIME SERVICE
def DateAndTime(self):

    AShift : time = time(hour=6,minute=0, second=0)
    BShift : time = time(hour=14,minute=30, second=0)
    CShift : time = time(hour=22,minute=30, second=0)
    initial_load : bool = True
    _A : bool = False
    _B : bool = False
    _C : bool = False
    self._popup : bool = False 

    while self.run_dateTimeService:
        self.date_current = date.today()
        self.time_current = datetime.now().strftime("%H:%M:%S")
        self.time.display(self.time_current)
        self.label_date.display(f"{self.date_current}")
        current_time = datetime.now().time()
        if AShift > current_time or CShift < current_time and initial_load: 
            self.shift = "C"
            initial_load = False
            log.info("Initial Shift Change -- C")
            _A = True
        if AShift < current_time < BShift and initial_load:
            self.shift = "A"
            initial_load = False
            log.info("Initial Shift Change -- A")
            _B = True
        if BShift < current_time < CShift and initial_load:
            self.shift = "B"
            initial_load = False
            log.info("Initial Shift Change -- B")
            _C = True 

        if not initial_load : 
            if AShift > current_time or CShift > current_time and _B: 
                self.shift = "C"
                _C = True
                _A = False
                _B = False
                log.info(" Shift Change -- C")
                self._popup = True
            if AShift < current_time < BShift and _C:
                self.shift = "A"
                _A = True
                _B = False
                _C = False
                log.info("Shift Change -- A")
                self._popup = True
            if BShift < current_time < CShift and _A:
                self.shift = "B"
                _B = True
                _A = False
                _C = False 
                log.info("Shift Change -- B")
                self._popup  = True

        self.table.setHorizontalHeaderLabels(["Poke Yoke","Station", "Type", "Verification Method",f"SHIFT : {self.shift}"])

        if not self._adminstrator:
            self.comboBox.setCurrentText(self.shift)
            self.dateEdit.setDate(QtCore.QDate.currentDate())
        sleep(1)

# ***************************************************************************
class LoginDialog(QtWidgets.QDialog):
    def __init__(self, a):
        super().__init__()

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

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username == "admin" and password == "admin":
            QtWidgets.QMessageBox.information(self, "Login Successful", "Welcome, {}!".format(username))
            self.accept()  # Close the login dialog
        else:
            QtWidgets.QMessageBox.warning(self, "Login Failed", "Invalid username or password. Please try again.")



# ***************************************************************************
# MAIN WINDOW CLASS FOR THE PROGRAM
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super().__init__()
        self.setupUi(self)
        self.tabWidget_5.tabBar().hide()

        # Setting up variables 
        self.load_initial_conditions : bool = False
        self.isFullScreen : bool = False
        self.date_current : str = ""
        self.time_current : str = ""
        self.run_dateTimeService : bool = True 
        self.shift : str = "" 
        self._adminstrator :bool = False

        # SETTING UP BUTTONS ACTIONS
        self.exit.clicked.connect(self.app_exit)
        self.full.clicked.connect(self.fullscreen)
        self.addPage.clicked.connect(self.addpage)
        self.updatePage_1.clicked.connect(self.updatePage)
        self.home_window.clicked.connect(self.homePage)
        self.settingsPage.clicked.connect(self.settingWindow)
        self.save_button_2.clicked.connect(self.save_conditions)
        self.pushButton_2.clicked.connect(self.save_data_checklist)
        self.pushButton.clicked.connect(self.openFile)

        self.label_6.setPixmap(QtGui.QPixmap("assets\logos\logo.PNG").scaled(50,50))
        self.label_7.setPixmap(QtGui.QPixmap("assets\logos\mahle.png").scaled(90,40))

        # SETTING UP HOME PAGE
        self.initial_index()

        self.tabWidget_5.setContentsMargins(0,0,0,0)
        self.setContentsMargins(0,0,0,0)

        # GENERATING MAIN TABLE
        self.gererate_main_table()

        # GENERATING ADD CONDITION TABLE 
        self.generate_add_condi_table()

        # LOADING MAIN TABLE INITIALLY
        self.load_data_main_table()

        # LOADING THE UPDATE TABLE GENERATOR
        self.update_table_generator()

        # SETTING UP DATE AND TIME SERVICE
        self.DateTime = Thread(target= lambda : DateAndTime(self))
        self.DateTime.start()

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
        self.pushButton.setDisabled(False)
        self.label_admin = QtWidgets.QLabel()
        self.label_admin.setStyleSheet("color:red;\n"
                                        "font-size:20px;\n")
        self.verticalLayout_checksheet.addWidget(self.label_admin)
        self.verticalLayout_checksheet.addWidget(self.check_sheet_table)
        for row in range(self.check_sheet_table.rowCount()):
            self.check_sheet_table.setRowHeight(row,15)
        self.check_sheet_table.setEditTriggers(QtWidgets.QTableWidget.EditTrigger.NoEditTriggers)
        self.pushButton.setDisabled(True)
        self.check_sheet_table.setHorizontalHeaderLabels(["Poka Yoke","Station","Type","Verification Method","Condition"])

    # ****************************************************************************
    def generate_add_condi_table(self) -> None:

        # TABLE FOR ADDING ADITIONAL CONDITIONS
        log.info("Table Add Condition Started")
        self.table_add_condition = QtWidgets.QTableWidget(40,4, parent = self.add_frame)
        self.table_add_condition.setHorizontalHeaderLabels(["Poka Yoke","Station","Type","Verification Method"])
        self.table_add_condition.setColumnWidth(0, 860)
        self.table_add_condition.setColumnWidth(3,200)

        # SETTING UP THE ROW HEIGHT 
        for row in range(0,self.table_add_condition.rowCount()):
            self.table_add_condition.setRowHeight(row,15)

        # ADDING WIDGET TO THE VERTICAL LAYOUT
        self.verticalLayout_4.addWidget(self.table_add_condition)
        self.verticalLayout_4.addLayout(self.horizontalLayout_6)
        

    # ****************************************************************************
    def gererate_main_table(self) -> None:
        log.debug("Main Table Started")
        self.verticalLayout_A = QtWidgets.QVBoxLayout(self.widget_5)
        self.verticalLayout_A.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_A.setSpacing(2)
        self.verticalLayout_A.setObjectName("verticalLayout_A")
        self.table = QtWidgets.QTableWidget(parent = self.widget_5)
        self.table.setColumnCount(5)
        self.table.setColumnWidth(3,200)
        self.table.setEditTriggers(QtWidgets.QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setColumnWidth(0,780)
        self.label_date = QtWidgets.QLCDNumber(parent=self.widget_5)
        self.label_date.setDigitCount(8)
        self.date_name  = QtWidgets.QLabel(parent=self.widget_5)
        self.date_name.setText("Date")

        for row in range(0,self.table.rowCount()):
            self.table.setRowHeight(row,25)
        self.horizontalLayout_belowTitle = QtWidgets.QHBoxLayout()
        self.horizontalLayout_belowTitle.setContentsMargins(0,2,0,2)

        self.label_date.setStyleSheet("font:20px;\n"
                                      "color:white;\n"
                                      "background-color:blue;\n"
                                      "border:1px soild black;\n")
        
        self.date_name.setStyleSheet("font:20px;\n"
                                      "background-color:yellow;\n"
                                      "border:1px soild black;\n"
                                      "border-radius:20px;\n")
        
        self.time_name = QtWidgets.QLabel(parent=self.widget_5)
        self.time_name.setText("Time")
        self.time_name.setStyleSheet("font:20px;\n"
                                      "background-color:yellow;\n"
                                      "border:1px soild black;\n")
        
        self.time = QtWidgets.QLCDNumber(parent=self.widget_5)
        self.time.setDigitCount(8)
        self.time.setStyleSheet("font:20px;\n"
                                "color:white;\n"
                                "background-color:blue;\n"
                                "border:1px soild black;\n")
        
        
        self.date_name.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.time_name.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        

        self.horizontalLayout_belowTitle.addWidget(self.date_name)
        self.horizontalLayout_belowTitle.addWidget(self.label_date)
        self.horizontalLayout_belowTitle.addWidget(self.time_name)
        self.horizontalLayout_belowTitle.addWidget(self.time)

        self.verticalLayout_A.addLayout(self.horizontalLayout_belowTitle)
        self.verticalLayout_A.addWidget(self.table)


    # ****************************************************************************
    def openFile(self):
        ...

    # ****************************************************************************
    # Saving the checklist form
    def save_data_checklist(self) -> None:
        data : str = []

        for row in range(self.check_sheet_table.rowCount()):
            combo_box_widget = self.check_sheet_table.cellWidget(row, 4)  
            selected_item = combo_box_widget.currentText()
            data.append(selected_item)

        print(data)

    # ****************************************************************************
    def load_data_checksheet(self) -> None:
        if self._adminstrator:
            self.label_admin.setText("You are Admin ... ")
            self.pushButton.setEnabled(True)
            
        if not self._adminstrator:
            self.label_admin.setText("")

        log.debug("Loading Data in the checklist")
        with open("csv/Poka-yoke-list.csv") as file:
            try:
                reader = csv.reader(file)
            except Exception as e:
                log.critical("Unable to find the conditon CSV file")

            row_number : int = 0
            l : int = 0

            for data in reader:
                l+=1
                
            self.check_sheet_table.setRowCount(l)
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
                                self.check_sheet_table.setItem(row_number,col_num, item)
                            except Exception as e:
                                log.debug(f"Error -- {e}")
                        else:
                            pass
                        col_num +=1

                    item_combo = QtWidgets.QComboBox()
                    item_combo.addItems(["Yes", "No"])
                    self.check_sheet_table.setCellWidget(row_number,4,item_combo)
                    row_number +=1
                self.check_sheet_table.update()

    # ****************************************************************************
    # FUNCTION TO ADD DATA TO THE MAIN TABLE
    def load_data_main_table(self) -> None :
        log.debug('Loading Data In The Main Table')
        with open("csv/Poka-yoke-list.csv") as file:
            try:
                reader = csv.reader(file)
            except Exception as e:
                log.critical("Unable to find the conditon CSV file")
            
            l : int = 0

            for data in reader:
                l += 1
                
            self.table.setRowCount(l)
            
        with open("csv/Poka-yoke-list.csv") as file:
            try:
                reader = csv.reader(file)
            except Exception as e:
                log.critical("Unable to find the conditon CSV file")

            row_number : int = 0
            
            for row in reader:
                col_num : int = 0
                for data in row:
                    try:
                        item = QtWidgets.QTableWidgetItem(data)
                        self.table.setItem(row_number,col_num, item) 
                    except Exception as e:
                        log.debug(f"Error -- {e}")
                    col_num +=1
                row_number +=1
            self.table.update()
    
    # ****************************************************************************

    # FUNCTION TO ADD DATA TO ADD CONDITION TABLE
    def load_conditions_add_table(self) -> None:
        log.debug("Loading The add Condition Table Data 👍")
        with open("csv/Poka-yoke-list.csv") as file:
            reader = csv.reader(file)
            row_nummber : int = 0
            for row in reader:
                col_num : int = 0
                for data in row:
                    try:
                        item = QtWidgets.QTableWidgetItem(data)
                        self.table_add_condition.setItem(row_nummber,col_num, item) 
                    except Exception as e:
                        log.debug(f"Error -- {e}")
                    col_num +=1
                row_nummber +=1
        self.table_add_condition.update()

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
            with open("csv/Poka-yoke-list.csv","w", newline='') as file:
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
                self.label_admin.setText("")
                self.pushButton.setEnabled(False)
        else:
            log.debug("Closing Applicaton")
            self.close()
    # ****************************************************************************
    # FULL SCREEN MODE
    def fullscreen(self) -> None:
        if not self.isFullScreen:
            self.showFullScreen()
            self.isFullScreen =True
            log.info("Full Screen Mode Enabled")
        else :
            self.showMaximized()
            self.isFullScreen = False
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
            else:
                event.ignore()
# ****************************************************************************
# Starting main app
log.info("App Started")
app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()