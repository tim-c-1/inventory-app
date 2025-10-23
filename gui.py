from PyQt6.QtCore import QModelIndex, Qt, QAbstractTableModel, QSize
from PyQt6.QtWidgets import QApplication, QHeaderView, QMainWindow, QVBoxLayout, QTabWidget, QLineEdit, QComboBox, QGridLayout, QLabel, QButtonGroup, QRadioButton, QWidget, QFileDialog, QPushButton, QCheckBox, QHBoxLayout, QTableView, QDialog, QDialogButtonBox, QMessageBox, QMenu, QMenuBar
from PyQt6.QtGui import QCloseEvent, QIcon, QAction
import sys, os
import pandas as pd
from main import Item
import main, gsheet_update
from typing import Any
import pickle

basedir = os.path.dirname(__file__)

try:
    from ctypes import windll # only exists on windows
    myappid = 'com.github.tim-c-1.inventorysystem.version1'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory")
        self.resize(700, 300)

        # set up config and help windows
        self.cw = None 
        self.hw = None

        # initialize data dictionary objects
        main.Item.Inventory = main.loadInventory() 

        self.central_widget = QWidget()
        self.layout_1 = QVBoxLayout()

        self.table = QTableView()
        self.user_input_widget = UserInputWidget(self)
        
        # set up table model
        data = self.readInventory()        
        MainWindow.model = TableModel(data)
        self.table.setModel(MainWindow.model)

        # menu bar and actions must be created after widgets containing used methods
        self._createActions()
        self._createMenuBar()

        # build the structure
        # self.setCentralWidget(self.user_input_widget)
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.layout_1)

        self.layout_1.addWidget(self.table)
        self.layout_1.addWidget(self.user_input_widget)
        
    def _createMenuBar(self) -> None:
        menuBar: QMenuBar | None = self.menuBar()
        fileMenu = QMenu("&File", self)
        g_sheet_menu = QMenu("&Google Sheet use", self)
        helpMenu = QMenu("&Help", self)
        if menuBar: 
            menuBar.addMenu(fileMenu)
            menuBar.addMenu(g_sheet_menu)
            menuBar.addMenu(helpMenu)
            
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.saveExitAction)

        g_sheet_menu.addAction(self.configAction)
        g_sheet_menu.addAction(self.push_to_google_action)
        helpMenu.addAction(self.helpAction)

    def _createActions(self) -> None:
        self.saveAction = QAction("&Save", self)
        self.saveExitAction = QAction("Save and &exit", self)
        self.configAction = QAction("&Config google sheets", self)
        self.helpAction = QAction("&Help", self)
        self.push_to_google_action = QAction("&Push to google sheets", self)

        self.saveAction.triggered.connect(self.user_input_widget.save_inventory)
        self.saveExitAction.triggered.connect(self.saveAndExit)
        self.configAction.triggered.connect(self.configWindow)
        self.helpAction.triggered.connect(self.helpWindow)
        self.push_to_google_action.triggered.connect(self.user_input_widget.push_to_google)

    def configWindow(self) -> None:
        if self.cw is None:
            self.cw = configMenu()
        self.cw.show()

    def helpWindow(self) -> None:
        if self.hw is None:
            self.hw = helpMenu()
        self.hw.show()

    def readInventory(self) -> pd.DataFrame:
        inv: dict = main.loadInventory()
        return main.unpackInventory(inv)
    
    def deleteSelectedRow(self) -> None:
        selected_rows = sorted(list(set(index.row() for index in self.table.selectedIndexes())))
        if not selected_rows:
            QMessageBox.information(self, "no selection.", "please select a row to delete.")
            
        else:
            for row in selected_rows:
                index: QModelIndex = self.model.index(row, 0)
                item_name : str | None = self.model.data(index, Qt.ItemDataRole.DisplayRole)
                deleteCheck = QMessageBox.warning(self, "Delete Row", f"Are you sure you want to delete {item_name} permanently? This action cannot be undone.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
                if item_name and deleteCheck == QMessageBox.StandardButton.Yes:
                    del main.Item.Inventory[item_name]
            self.model.resetData()

    def saveAndExit(self) -> None:
        self.user_input_widget.save_inventory()
        sys.exit()

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        saveCheck = QMessageBox.information(self, "save?", "do you want to save before closing?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if saveCheck == QMessageBox.StandardButton.Yes:
            self.user_input_widget.save_inventory()
        return super().closeEvent(a0)
    
class TableModel(QAbstractTableModel):
    def __init__(self, data: pd.DataFrame) -> None:
        super().__init__()
        self._data = data

    def data(self, index, role=Qt.ItemDataRole.DisplayRole) -> str | None:
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole:
                value = self._data.iloc[index.row(), index.column()]
                return str(value)
        
    def rowCount(self, index: QModelIndex) -> int:
        return self._data.shape[0]
    
    def columnCount(self, index: QModelIndex) -> int:
        return self._data.shape[1]

    def headerData(self, col, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._data.columns[col]

    def resetData(self) -> None:
        self.beginResetModel()
        new_data = main.unpackInventory(main.Item.Inventory)
        self._data = new_data
        self.endResetModel()

class UserInputWidget(QWidget):
    def __init__(self, parent: MainWindow):
        super().__init__(parent)
        self.main_window = parent

        # make buttons
        self.new_item_btn = QPushButton("New Item")
        self.delete_item_btn = QPushButton("Delete Item")
        self.edit_item_btn = QPushButton("Edit Item")
        self.save_inv_btn = QPushButton("Save")
        self.check_out_btn = QPushButton("Check Out Item")
        self.check_in_btn = QPushButton("Check In Item")
        self.push_to_google_btn = QPushButton("Push to Google Sheets")

        # add user hints
        self.new_item_btn.setToolTip("create new inventory item")

        # connect buttons
        self.new_item_btn.pressed.connect(self.new_item_btn_pressed)
        self.delete_item_btn.pressed.connect(self.delete_row)
        self.save_inv_btn.pressed.connect(self.save_inventory)
        self.check_out_btn.pressed.connect(self.check_out_item)
        self.check_in_btn.pressed.connect(self.check_in_item)
        self.edit_item_btn.pressed.connect(self.edit_item)
        self.push_to_google_btn.pressed.connect(self.push_to_google)
        self.input_layout = QGridLayout()
        
        # input_layout.setContentsMargins(5,0,0,0)
        
        self.input_layout.addWidget(self.edit_item_btn, 1, 0)
        self.input_layout.addWidget(self.new_item_btn, 0, 0)
        self.input_layout.addWidget(self.delete_item_btn, 0, 1)
        self.input_layout.addWidget(self.save_inv_btn, 1, 1)
        self.input_layout.addWidget(self.check_out_btn, 2, 0)
        self.input_layout.addWidget(self.check_in_btn, 2, 1)
        self.input_layout.addWidget(self.push_to_google_btn, 3, 0)
        
        self.setLayout(self.input_layout)

    def new_item_btn_pressed(self) -> None:
        dlg = NewItemDialog()
        dlg.exec()

    def save_inventory(self) -> None:
        main.saveInventory()
        QMessageBox.information(self, "saved", "inventory saved")

    def check_out_item(self) -> None:
        dlg = CheckOutDialog()
        dlg.exec()
    
    def check_in_item(self) -> None:
        dlg = CheckInDialog()
        dlg.exec()

    def delete_row(self) -> None:
        if self.main_window:
            self.main_window.deleteSelectedRow()

    def edit_item(self) -> None:
         if self.main_window:
            selected_rows = sorted(list(set(index.row() for index in self.main_window.table.selectedIndexes())))
            if not selected_rows:
                QMessageBox.information(self, "no selection.", "no row selected, please select something to edit.")
            else:
                selected_row = selected_rows[0]
                index: QModelIndex = self.main_window.model.index(selected_row, 0)
                item_name: str | None = self.main_window.model.data(index, Qt.ItemDataRole.DisplayRole)
                if item_name is not None: 
                    dlg = EditItemDialog(item_name)
                    dlg.exec()

    def push_to_google(self) -> None:
        
        spreadsheet = configMenu().loadConfig()
        if spreadsheet is None or spreadsheet == "":
            QMessageBox.information(self, "no config saved", "save config settings to use this feature.")
        else:
            try:
                inv = main.unpackInventory(main.Item.Inventory)
                self.main_window.user_input_widget.save_inventory()
                gsheet_update.updateInvSheet(inv, spreadsheet)
                QMessageBox.information(self, "push successful", "inventory was pushed to google sheets.")
            except:
                configMenu().authenticationSetup()
        
class NewItemDialog(QDialog):
    def __init__(self) -> None:
            super().__init__()
            self.setWindowTitle("create new item")

            btn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            self.buttonBox = QDialogButtonBox(btn)
            self.buttonBox.accepted.connect(self.accept)
            self.buttonBox.rejected.connect(self.reject)

            self.name = QLineEdit()
            self.amount = QLineEdit()
            self.maxAmount = QLineEdit()
            self.cost = QLineEdit()
            self.source = QLineEdit()

            # placeholder text and tooltips
            self.name.setPlaceholderText("Name")
            self.amount.setPlaceholderText("Amount")
            self.maxAmount.setPlaceholderText("Max Amount")
            self.cost.setPlaceholderText("Cost")
            self.source.setPlaceholderText("Source")

            self.maxAmount.setToolTip("if different than current amount")

            formWidget = QGridLayout()
            formWidget.addWidget(self.name)
            formWidget.addWidget(self.amount)
            formWidget.addWidget(self.maxAmount)
            formWidget.addWidget(self.cost)
            formWidget.addWidget(self.source)

            layout = QVBoxLayout()
            layout.addLayout(formWidget)
            layout.addWidget(self.buttonBox)
            self.setLayout(layout)
    def accept(self) -> None:
        try:
            try:
                maxAmount = float(self.maxAmount.text())
                print(f"max is {maxAmount}")
            except:
                print("max amount changed to current")
                maxAmount = float(self.amount.text()) # assign field to current amount if not entered.
            if float(self.amount.text()) > maxAmount:
                QMessageBox.information(self, "invalid amount", "current amount cannot be greater than max amount")
                print("current amount cannot be greater than max amount.")
            elif maxAmount <= 0:
                QMessageBox.information(self, "invalid amount" , "max amount must be greater than zero")
                print("max amount must be greater than zero.")
            elif float(self.amount.text()) < 0:
                QMessageBox.information(self, "invalid amount", "current amount cannot be less than zero.")
                print("current amount cannot be less than zero.")
            elif float(self.cost.text()) < 0:
                QMessageBox.information(self, "invalid cost", "item cost cannot be less than zero")
                print("item cost cannot be less than zero.")
            else:
                args = [self.name.text(), float(self.amount.text()), maxAmount, float(self.cost.text()), self.source.text()]
                if args:
                    main.createNewItem(*args)
                    MainWindow.model.resetData()
                return super().accept()
        except ValueError:
            QMessageBox.information(self, "invalid number", "number fields must be a number")
            print("number fields must be a number")

class CheckOutDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("check out items")

        btn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(btn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.item_name = QComboBox(self)
        self.item_amount = QLineEdit()

        self.item_amount.setPlaceholderText("Amount to check out")

        self.item_name.setEditable(True)
        self.item_name.addItems(main.Item.Inventory.keys())
        self.item_name.lineEdit().setPlaceholderText("Name") # pyright: ignore[reportOptionalMemberAccess]
        self.item_name.setCurrentIndex(-1)

        layout = QVBoxLayout()
        layout.addWidget(self.item_name)
        layout.addWidget(self.item_amount)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
    
    def accept(self) -> None:
        try:
            args: list = [self.item_name.currentText(), float(self.item_amount.text())]
            inv = main.Item.Inventory
            if args:
                if self.item_name.currentText() in inv:

                    item: Item = inv[self.item_name.currentText()]

                    if item.current_amount >= float(self.item_amount.text()) and item.current_amount > 0:
                        main.checkOutItem(*args)
                        MainWindow.model.resetData()
                        return super().accept()
                    
                    else:
                        QMessageBox.information(self, "invalid amount", f"not enough {item.name} to check out. there are only {item.current_amount} left. checkout failed.")
                        print(f"not enough {item.name} to check out. there are only {item.current_amount} left. checkout failed.")
                else:
                    QMessageBox.information(self, "invalid item name", f"{self.item_name.currentText()} does not exist.")
                    print(f"{self.item_name.currentText()} does not exist.")

        except ValueError:
            QMessageBox.information(self, "invalid number", "number fields must be a number")
            print("number fields must be a number")

class CheckInDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("check in items")

        btn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(btn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.item_name = QComboBox()
        self.item_amount = QLineEdit()
        self.max_increase = QCheckBox("Increase max amount?")

        # placeholder text and tooltips
        self.item_amount.setPlaceholderText("Amount to check in")
        self.item_name.setEditable(True)
        self.item_name.addItems(main.Item.Inventory.keys())
        self.item_name.lineEdit().setPlaceholderText("Name") # pyright: ignore[reportOptionalMemberAccess]
        self.item_name.setCurrentIndex(-1)

        self.max_increase.setToolTip("increases max to current plus new checked in items.")

        layout = QVBoxLayout()

        layout.addWidget(self.item_name)
        layout.addWidget(self.item_amount)
        layout.addWidget(self.max_increase)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def accept(self) -> None:
        try:
            args: list = [self.item_name.currentText(), float(self.item_amount.text()), self.max_increase.isChecked()]
            inv: dict = main.Item.Inventory
            new_amount: float = args[1]
            if args:
                if self.item_name.currentText() in inv:
                    item: Item = inv[self.item_name.currentText()]
                    # if new_amount < item.current_amount: 
                        # print("new amount not valid. if you want to decrease current amount, use the checkout button.")
                    if (new_amount + item.current_amount) > item.total_amount and not self.max_increase.isChecked() == True:
                        QMessageBox.information(self,"too many items", f"there are already {item.current_amount} out of {item.total_amount} {item.name}s. If you want to increase the amount, please check the corresponding box.")
                        print(f"there are already {item.current_amount} out of {item.total_amount} {item.name}s. new amount not valid. if you want to increase the amount, please check the corresponding box.")
                    elif (new_amount + item.current_amount) < item.total_amount and self.max_increase.isChecked() == True:
                        
                        QMessageBox.information(self, "invalid amount", f"{new_amount} not enough to increase max. please edit max using the edit button.")
                        print("not enough items to increase max, please edit max amount using edit button.")
                        MainWindow.model.resetData()
                
                    else:    
                        main.checkInItem(*args)
                        MainWindow.model.resetData()
                        return super().accept()
                else:
                    QMessageBox.information(self, "invalid item name", f"{self.item_name.currentText()} does not exist.")
        except ValueError:
            QMessageBox.information(self, "invalid number", "number fields must be a number")
            print("number fields must be a number")        

class EditItemDialog(QDialog):
    def __init__(self, item_name: str) -> None:
        super().__init__()
        self.setWindowTitle("edit item")
        label = QLabel(f"Editing attributes of {item_name}")
        self.item_name = item_name
        
        # set up dialog buttons
        btn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(btn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # get current item attributes
        item: Item = main.Item.Inventory[item_name]
        item_cost: float = item.cost
        current_amount: float = item.current_amount
        total_amount: float = item.total_amount
        item_source: str = item.source

        # display current item attributes
        self.name = QLineEdit(self.item_name)
        self.cost = QLineEdit(str(item_cost))
        self.amt = QLineEdit(str(current_amount))
        self.max = QLineEdit(str(total_amount))
        self.source = QLineEdit(item_source)

        # add labels to side of input fields
        name_label = QLabel("item name")
        amt_label = QLabel("current amount")
        max_label = QLabel("total amount")
        cost_label = QLabel("item cost")
        source_label = QLabel("item source")

        # add everything to layout
        layout = QGridLayout()
        layout.addWidget(label, 0, 0, 1, 2)
        layout.addWidget(self.name, 1, 1)
        layout.addWidget(name_label, 1, 0)
        layout.addWidget(self.amt, 2, 1)
        layout.addWidget(amt_label, 2, 0)
        layout.addWidget(self.max, 3, 1)
        layout.addWidget(max_label, 3, 0)
        layout.addWidget(self.cost, 4, 1)
        layout.addWidget(cost_label, 4, 0)
        layout.addWidget(self.source, 5, 1)
        layout.addWidget(source_label, 5, 0)
        layout.addWidget(self.buttonBox, 6, 0, 1, 2)

        # set layout in view
        self.setLayout(layout)
       
    def accept(self) -> None:
        try:
            # validate new values
            new_name: str = self.name.text()
            new_cost: float = float(self.cost.text())
            new_amount: float = float(self.amt.text())
            new_total: float = float(self.max.text())
            new_source: str = self.source.text()

            if new_amount > new_total:
                QMessageBox.information(self, "invalid amount", "current amount cannot be greater than max amount")
                print("max amount cannot be less than current amount.")
            elif new_amount < 0:
                QMessageBox.information(self, "invalid amount", "current amount cannot be less than zero.")
                print("current amount cannot be less than zero.")
            elif new_cost < 0:
                QMessageBox.information(self, "invalid cost", "item cost cannot be less than zero")
                print("item cost cannot be less than zero.")
            elif new_total <= 0:
                QMessageBox.information(self, "invalid amount" , "max amount must be greater than zero")
                print("max amount must be greater than zero.")
            else:
                editCheck = QMessageBox.information(self, "", f"are you sure you'd like to update {self.item_name}'s attributes?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
                if editCheck == QMessageBox.StandardButton.Yes:
                    # make edits
                    if new_name != self.item_name: # if the new name is different, change the dict key
                        main.Item.Inventory[new_name] = main.Item.Inventory[self.item_name]
                        main.Item.Inventory[new_name].name = new_name
                        main.Item.Inventory[new_name].cost = new_cost
                        main.Item.Inventory[new_name].current_amount = new_amount
                        main.Item.Inventory[new_name].total_amount = new_total
                        main.Item.Inventory[new_name].source = new_source
                        del main.Item.Inventory[self.item_name]
                        MainWindow.model.resetData()
                        return super().accept()
                    else:
                        main.Item.Inventory[self.item_name].cost = new_cost
                        main.Item.Inventory[self.item_name].current_amount = new_amount
                        main.Item.Inventory[self.item_name].total_amount = new_total
                        main.Item.Inventory[self.item_name].source = new_source
                        MainWindow.model.resetData()
                        return super().accept()                        
        except ValueError:
            QMessageBox.information(self, "invalid number", "number fields must be a number")
            print("number fields must be a number")
        
class configMenu(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Config")
        self.resize(100, 50)

        sheet_name_label = QLabel("google sheet name")
        self.sheet_name = QLineEdit()
        self.sheet_name.setPlaceholderText("google sheet name")
        self.sheet_name.setToolTip("this must be the exact name of your google sheet\nI recommend copy/pasting")
        self.save_config_btn = QPushButton("Save config settings")
        self.test_config_btn = QPushButton("Test config")

        self.save_config_btn.pressed.connect(self.saveConfig)
        self.test_config_btn.pressed.connect(self.authenticationSetup)

        # load config
        if os.path.exists('./g_config.pkl'):
            # can expand this to an array that unpacks to multiple vars if needed
            try:
                self.sheet_name.setText(self.loadConfig())
            except:
                os.remove('./g_config.pkl')
                QMessageBox.information(self, "config load error", "config load error. removed bad config file.\nplease save a new one.")
        
        # need to add method for creating authentication folder, credential file, collecting sheet information
        # # method should check if auth folder exists -> if not: create -> check if credentials file exists -> if not: display help page on creating? -> 
        # # then take desired sheet name and authenticate. 
        # could also collect info about when to archive a sheet
        # # gsheet would check date, copy current information to a new sheet titled archive_[mm/yyyy], then update main sheet

        layout = QGridLayout()
        layout.addWidget(sheet_name_label, 1, 0)
        layout.addWidget(self.sheet_name, 1, 1)
        layout.addWidget(self.save_config_btn, 2, 0)
        layout.addWidget(self.test_config_btn, 2, 1)

        self.setLayout(layout)

    def authenticationSetup(self) -> None:
        if not os.path.exists('./authentication/'):
            os.mkdir('authentication')
        if not os.path.exists('./authentication/credentials.json'):
            # display setup how-to
            QMessageBox.information(self, "no credentials found", "contact the developer for credentials.\nwhen given, place the json file in authentication folder.")
        else:
            try:
                gc = gsheet_update.authUser()
                if gc is not None: 
                    QMessageBox.information(self, "Auth success", "Auth succeeded.")
                else:
                    raise Exception
            except Exception as e:
                QMessageBox.information(self, "Auth failed", f"Auth failed. Exception: {e}")            

    def saveConfig(self) -> None:
        with open('g_config.pkl', 'wb') as f:
            pickle.dump(self.sheet_name.text(), f, pickle.HIGHEST_PROTOCOL)
        QMessageBox.information(self, "saved.", "saved config settings.")

    def loadConfig(self) -> Any:
        with open('g_config.pkl', 'rb') as f:
            return pickle.load(f)

class helpMenu(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Help")
        self.resize(300, 300)

        self.body = QLabel("this is some help text.\nnow the help text is on a new line.")

        self.contents = QLabel("1. Introduction\n2. Adding an item\n3. Deleting an item\n4. Checking items in/out")

        # this should probably just load a text/md file and display it? 
        # and the file can live with the whole package and be opened outside of the application

        layout = QGridLayout()
        layout.addWidget(self.body)

        self.setLayout(layout)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()