from PyQt6.QtCore import QModelIndex, Qt, QAbstractTableModel, QSize
from PyQt6.QtWidgets import QApplication, QHeaderView, QMainWindow, QVBoxLayout, QTabWidget, QLineEdit, QComboBox, QGridLayout, QLabel, QButtonGroup, QRadioButton, QWidget, QFileDialog, QPushButton, QCheckBox, QHBoxLayout, QTableView, QDialog, QDialogButtonBox, QMessageBox
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
        self.user_input_widget = UserInputWidget(self)
        
        # set up table model
        data = self.readInventory()        
        MainWindow.model = TableModel(data)
        self.table.setModel(MainWindow.model)
        
        # rowLabels: QHeaderView | None = self.table.verticalHeader()
        # if rowLabels:
        #     rowLabels.setVisible(False)

       
        # build the structure
        # self.setCentralWidget(self.user_input_widget)
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.layout_1)

        self.layout_1.addWidget(self.table)
        self.layout_1.addWidget(self.user_input_widget)
        

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

        # add user hints
        self.new_item_btn.setToolTip("create new inventory item")

        # connect buttons
        self.new_item_btn.pressed.connect(self.new_item_btn_pressed)
        self.delete_item_btn.pressed.connect(self.delete_row)
        self.save_inv_btn.pressed.connect(self.save_inventory)
        self.check_out_btn.pressed.connect(self.check_out_item)
        self.check_in_btn.pressed.connect(self.check_in_item)
        self.edit_item_btn.pressed.connect(self.edit_item)

        self.input_layout = QGridLayout()
        
        # input_layout.setContentsMargins(5,0,0,0)
        
        self.input_layout.addWidget(self.edit_item_btn, 1, 0)
        self.input_layout.addWidget(self.new_item_btn, 0, 0)
        self.input_layout.addWidget(self.delete_item_btn, 0, 1)
        self.input_layout.addWidget(self.save_inv_btn, 1, 1)
        self.input_layout.addWidget(self.check_out_btn, 2, 0)
        self.input_layout.addWidget(self.check_in_btn, 2, 1)
        
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
                print("current amount cannot be greater than max amount.")
            elif maxAmount <= 0:
                print("max amount must be greater than zero.")
            elif float(self.cost.text()) < 0:
                print("item cost cannot be less than zero.")
            else:
                args = [self.name.text(), float(self.amount.text()), maxAmount, float(self.cost.text()), self.source.text()]
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

        self.item_name = QLineEdit()
        self.item_amount = QLineEdit()

        # placeholder text
        self.item_name.setPlaceholderText("Name")
        self.item_amount.setPlaceholderText("Amount to check out")

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

class CheckInDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("check in items")

        btn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(btn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.item_name = QLineEdit()
        self.item_amount = QLineEdit()
        self.max_increase = QCheckBox("Increase max amount?")

        # placeholder text and tooltips
        self.item_name.setPlaceholderText("Name")
        self.item_amount.setPlaceholderText("Amount to check in")

        self.max_increase.setToolTip("increases max to current plus new checked in items.")

        layout = QVBoxLayout()

        layout.addWidget(self.item_name)
        layout.addWidget(self.item_amount)
        layout.addWidget(self.max_increase)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def accept(self) -> None:
        try:
            args: list = [self.item_name.text(), float(self.item_amount.text()), self.max_increase.isChecked()]
            inv: dict = main.Item.Inventory
            new_amount: float = args[1]
            if args:
                if self.item_name.text() in inv:
                    item: Item = inv[self.item_name.text()]
                    # if new_amount < item.current_amount: 
                        # print("new amount not valid. if you want to decrease current amount, use the checkout button.")
                    if (new_amount + item.current_amount) > item.total_amount and not self.max_increase.isChecked() == True:
                        print(f"there are already {item.current_amount} out of {item.total_amount} {item.name}s. new amount not valid. if you want to increase the amount, please check the corresponding box.")
                    elif (new_amount + item.current_amount) < item.total_amount and self.max_increase.isChecked() == True:
                        main.checkInItem(args[0], args[1])
                        print("not enough items to increase max, please edit max amount using edit button.")
                        MainWindow.model.resetData()
                        return super().accept()
                    else:    
                        main.checkInItem(*args)
                        MainWindow.model.resetData()
                        return super().accept()
        except ValueError:
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
                print("max amount cannot be less than current amount.")
            elif new_amount < 0:
                print("current amount cannot be less than zero.")
            elif new_cost < 0:
                print("item cost cannot be less than zero.")
            elif new_total <= 0:
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
            print("number fields must be a number")
        


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()