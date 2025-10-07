from PyQt6.QtCore import QModelIndex, Qt, QAbstractTableModel, QSize
from PyQt6.QtWidgets import QApplication, QHeaderView, QMainWindow, QVBoxLayout, QTabWidget, QLineEdit, QComboBox, QGridLayout, QLabel, QButtonGroup, QRadioButton, QWidget, QFileDialog, QPushButton, QCheckBox, QHBoxLayout, QTableView, QDialog, QDialogButtonBox
from PyQt6.QtGui import QIcon
import sys, os
import pandas as pd
from main import Item
import main
from typing import Any

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("testing")
        self.resize(700, 300)
        # initialize data dictionary objects
        main.Item.Inventory = main.loadInventory() 

        self.central_widget = QWidget()
        self.layout_1 = QVBoxLayout()

        self.table = QTableView()
        self.user_input_widget = UserInputWidget()
        
        # set up table model
        data = self.readInventory()        
        MainWindow.model = TableModel(data)
        self.table.setModel(MainWindow.model)
        
        rowLabels: QHeaderView | None = self.table.verticalHeader()
        if rowLabels:
            rowLabels.setVisible(False)

       
        # build the structure
        # self.setCentralWidget(self.user_input_widget)
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.layout_1)

        self.layout_1.addWidget(self.table)
        self.layout_1.addWidget(self.user_input_widget)
        

    def readInventory(self) -> pd.DataFrame:
        inv: dict = main.loadInventory()
        return main.unpackInventory(inv)

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
    def __init__(self):
        super().__init__()

        # make buttons
        self.new_item_btn = QPushButton("New Item")
        self.delete_item_btn = QPushButton("Delete Item")
        self.edit_item_btn = QPushButton("Edit Item")
        self.save_inv_btn = QPushButton("Save")
        self.check_out_btn = QPushButton("Check Out Item")

        # add user hints
        self.new_item_btn.setToolTip("create new inventory item")

        # connect buttons
        self.new_item_btn.pressed.connect(self.new_item_btn_pressed)
        self.save_inv_btn.pressed.connect(self.save_inventory)
        self.check_out_btn.pressed.connect(self.check_out_item)

        self.input_layout = QGridLayout()
        
        # input_layout.setContentsMargins(5,0,0,0)
        
        self.input_layout.addWidget(self.edit_item_btn, 1, 0)
        self.input_layout.addWidget(self.new_item_btn, 0, 0)
        self.input_layout.addWidget(self.delete_item_btn, 0, 1)
        self.input_layout.addWidget(self.save_inv_btn, 1, 1)
        self.input_layout.addWidget(self.check_out_btn, 2, 0)
        
        self.setLayout(self.input_layout)

    def new_item_btn_pressed(self) -> None:
        dlg = NewItemDialog()
        dlg.exec()

    def save_inventory(self) -> None:
        main.saveInventory()
        dlg = SaveInventoryMessage()
        dlg.exec()

    def check_out_item(self) -> None:
        dlg = CheckOutDialog()
        dlg.exec()
        pass

class NewItemDialog(QDialog):
    def __init__(self) -> None:
            super().__init__()
            self.setWindowTitle("create new item")

            btn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            self.buttonBox = QDialogButtonBox(btn)
            self.buttonBox.accepted.connect(self.accept)
            self.buttonBox.rejected.connect(self.reject)

            self.name = QLineEdit("Name")
            self.amount = QLineEdit("Amount")
            self.maxAmount = QLineEdit("Max Amount")
            self.maxAmount.setToolTip("if different than current amount")
            self.cost = QLineEdit("Cost")
            self.source = QLineEdit("Item source")

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
            args = [self.name.text(), float(self.amount.text()), float(self.maxAmount.text()), float(self.cost.text()), self.source.text()]
            if args:
                main.createNewItem(*args)
                MainWindow.model.resetData()
            return super().accept()
        except ValueError:
            print("number fields must be a number")
        
class SaveInventoryMessage(QDialog):
    def __init__(self) -> None:
        super().__init__()

        btn = QDialogButtonBox.StandardButton.Ok
        self.btnBox = QDialogButtonBox(btn)
        self.btnBox.accepted.connect(self.accept)

        message = QLabel("Inventory saved.")

        layout = QVBoxLayout()
        layout.addWidget(message)
        layout.addWidget(self.btnBox)
        self.setLayout(layout)

class CheckOutDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("check out items")

        btn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(btn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.item_name = QLineEdit("Name")
        self.item_amount = QLineEdit("Amount to check out")

        layout = QVBoxLayout()
        layout.addWidget(self.item_name)
        layout.addWidget(self.item_amount)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
    
    def accept(self) -> None:
        try:
            args: list = [self.item_name.text(), float(self.item_amount.text())]
            inv = main.Item.Inventory
            if args:
                if self.item_name.text() in inv:

                    item: Item = inv[self.item_name.text()]

                    if item.current_amount >= float(self.item_amount.text()) and item.current_amount > 0:
                        main.checkOutItem(*args)
                        MainWindow.model.resetData()
                        return super().accept()
                    
                    else:
                        print(f"not enough {item.name} to check out. there are only {item.current_amount} left. checkout failed.")
                else:
                    print(f"{self.item_name.text()} does not exist.")

        except ValueError:
            print("number fields must be a number")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()