from tabulate import tabulate
from typing import Self
import pickle
import os
import pandas as pd
import gsheet_update

"""
    This inventory program offers a simple desktop interferace to keep track of inventory and push changes to a google sheet for collaboration.
    main.py includes a rudimentary interface for using the inventory system from the command line.

    Copyright (C) 2025 Timothy Cooney

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

class Item: 
    Inventory: dict[str, Self] = dict()
    def __init__(self, name: str, total_amount: float, current_amount: float = 0, cost: float = 0, source: str ="") -> None:
        self.name: str = name
        self.current_amount: float = current_amount
        self.availability: bool = True if current_amount > 0 else False
        self.total_amount: float = total_amount
        self.cost: float = cost
        self.source: str = source
        Item.Inventory[self.name] = self

    # setter methods
    def updateCost(self, newCost: float) -> None:
        self.cost = newCost
    def updateSource(self, newSource: str) -> None:
        self.source = newSource
    def checkOut(self, amount: float) -> None:
        self.current_amount -= amount
        self.checkAvailability()
    def checkIn(self, amount: float) -> float:
        self.current_amount += amount
        self.checkAvailability()
        return self.current_amount
    def updateMaxAmount(self, new_max_amount: float) -> None:
        self.total_amount = new_max_amount
    def checkAvailability(self) -> None:
        if self.current_amount == 0: 
            self.availability = False
        elif self.current_amount > 0 and self.availability != True: 
            self.availability = True

def createNewItem(*args) -> Item | None:
    if args:
        name = args[0]
        amount = args[1]
        total_amount = args[2]
        cost = args[3]
        source = args[4]
        return Item(name, total_amount, amount, cost, source)
    else:
        name: str = input("item name: ")
        if "%s" % (name) not in Item.Inventory:
            # validate numeric inputs
            while True:
                try:
                    amount: float = float(input("Item amount: "))
                    total_equals_current_check = input("Is the total amount the same as the current amount? ([y]/n)").lower()
                    if total_equals_current_check == "n":
                        while True:
                            try:
                                total_amount: float = float(input("enter the total amount: "))
                                break
                            except ValueError:
                                print("Please enter a number.")
                    else:
                        total_amount = amount
                    break
                except ValueError:
                    print("Please enter a number.")


            while True:
                try:
                    cost: float = float(input("Item cost: "))
                    break
                except ValueError:
                    print("Please enter a number.")

            source: str = input("Item source: ")

            return Item(name, total_amount, amount, cost, source)
        
        else:
            print("item already exists!")

def deleteItem() -> None:
    item_to_delete: str = input("enter name of item to delete: ")
    check: str = input(f"are you sure you want to delete {item_to_delete}? This action is permanent and cannot be undone. (y/n): ").lower()
    if item_to_delete in Item.Inventory:
        if check == "y":
            del Item.Inventory[item_to_delete]
        else:
            print("delete aborted.")
    else:
        print(f"{item_to_delete} does not exist. Try viewing the inventory to see all items.")

def checkOutItem(*args) -> None:
    if args:
        item_to_checkout: str = args[0]
        checkout_amount: float = args[1]

        item:Item = Item.Inventory[item_to_checkout]
        item.checkOut(checkout_amount)

    else:
        item_to_checkout: str = input("item to check out: ")
        checkout_amount: float = float(input("amount to check out: "))
        if item_to_checkout in Item.Inventory:
            item: Item = Item.Inventory[item_to_checkout] # use "item" as reference to item in inventory
            if item.current_amount >= checkout_amount and item.current_amount > 0:
                item.checkOut(checkout_amount)
                print(f"successfully checked out {checkout_amount} of {item_to_checkout}.")
            else:
                print(f"not enough {item_to_checkout} to check out. there are only {item.current_amount} left. checkout failed.")
        else:
            print(f"{item_to_checkout} does not exist. Try viewing the inventory to see all items.")

def checkInItem(*args) -> None:
    if args:
        item_to_checkin: str = args[0]
        checkin_amount: float = args[1]
        increase_max_amount: bool = args[2]

        item: Item = Item.Inventory[item_to_checkin]
        newAmount = item.checkIn(checkin_amount)
        if increase_max_amount:
            item.updateMaxAmount(newAmount)
    else:
        item_to_checkin: str = input("item to check in: ")
        checkin_amount: float = float(input("amount to check in: "))
        if item_to_checkin in Item.Inventory:
            item: Item = Item.Inventory[item_to_checkin]
            item.checkIn(checkin_amount)
        else:
            print(f"{item_to_checkin} does not exist. Try viewing the inventory to see all items.")

def unpackInventory(inv: dict) -> pd.DataFrame:
    table: list = list()
    
    for key, item in inv.items():
        attributes = item.__dict__.copy()
        table.append(attributes)
    # print(tabulate(table, headers=['Name', 'Amount', 'Available?', 'Cost', 'Source']))
    return pd.DataFrame(table)

def adjustItemAttribute(attribute: str) -> None:
    selected_item: str = input("enter item name: ")
    if selected_item in Item.Inventory:
        item_to_adjust: Item = Item.Inventory[selected_item]
        if attribute == "cost":
            new_amount: float = float(input(f"enter new cost for {item_to_adjust}: "))
            item_to_adjust.updateCost(new_amount)
        elif attribute == "source":
            new_source: str = input(f"enter new source for {item_to_adjust}")
            item_to_adjust.updateSource(new_source)
    else:
        print(f"{selected_item} does not exist. Try viewing the inventory to see all items.")

def saveInventory() -> None:
    with open('Inventory.pkl', 'wb') as f:
        pickle.dump(Item.Inventory, f, pickle.HIGHEST_PROTOCOL)

def loadInventory():
    with open('Inventory.pkl', 'rb') as f:
        return pickle.load(f)
    
if __name__ == "__main__":
    # load existing on startup
    if os.path.exists('./Inventory.pkl'):
        Item.Inventory = loadInventory()

    # CLI loop
    loop = True
    for n in range(50): print("-",sep=' ', end='', flush=True)
    print("\nWelcome to the inventory system.\n")
    while loop:
        for n in range(50): print("-",sep=' ', end='', flush=True)
        selection: str = input("\nWhat would you like to do?\n"\
                            "(N)ew item\n"\
                            "(D)elete item\n"\
                            "Check (O)ut items\n"\
                            "Check (I)n items\n"
                            "(V)iew inventory\n"\
                            "Update item (c)ost\n"\
                            "Update Item (s)ource\n"\
                            "(E)xit\n"\
                            ).lower() # get user selection, accept any case
        if selection == "n" or selection == "new":
            item = createNewItem() # create new item
            print(f"{item} created.")
        elif selection == "d" or selection == "delete":
            deleteItem() # delete item function
        elif selection == "o" or selection == "out":
            checkOutItem() # make call to checkout function
        elif selection == "i" or selection == "in":
            checkInItem()
        elif selection == "v" or selection == "view":
            print(tabulate(unpackInventory(Item.Inventory), headers='keys',showindex=False, tablefmt='pipe', stralign='center', numalign='right'))  # pyright: ignore[reportArgumentType]
        elif selection == "c" or selection == "cost":
            adjustItemAttribute("cost") # run function to adjust attributes. 
        elif selection == "s" or selection == "source":
            adjustItemAttribute("source")
        elif selection == "e" or selection == "exit":
            loop = False

    save:bool = True if input("save inventory? ([y]/n)").lower() != "n" else False

    if save:
        # do save stuff
        saveInventory()
        push:bool = False if input("push updates to google? (y/[n])").lower() != "y" else True
        if push:
            inv = unpackInventory(Item.Inventory)
            gsheet_update.updateInvSheet(inv, "InvTest")