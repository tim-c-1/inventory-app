from tabulate import tabulate
from typing import Self
import pickle
import os
import pandas as pd
import gsheet_update
# create method for creating objects of items
    # every item should have name, amount, availability (based on amount), cost(optional), item source
    # should each item hold individual objects or just have an amount attribute

# display function should tabulate the inventory items
# you should be able to check out a custom amount of items, not to exceed the amount available
# you should be able to edit the item's attributes

class Item: 
    Inventory: dict[str, Self] = dict()
    def __init__(self, name: str, amount: float, cost: float = 0, source: str ="") -> None:
        self.name: str = name
        self.amount: float = amount
        self.availability: bool = True if amount > 0 else False
        self.cost: float = cost
        self.source: str = source
        Item.Inventory[self.name] = self

    # setter methods
    def updateCost(self, newCost: float) -> None:
        self.cost = newCost
    def updateSource(self, newSource: str) -> None:
        self.source = newSource
    def checkOut(self, amount: float) -> None:
        self.amount -= amount
        if self.amount == 0: self.availability = False
    def checkIn(self, amount: float) -> None:
        self.amount =+ amount
        if self.amount > 0 and self.availability != True: self.availability = True

def createNewItem() -> Item | None:
    name: str = input("item name: ")
    if "%s" % (name) not in Item.Inventory:
        # validate numeric inputs
        while True:
            try:
                amount: float = float(input("Item amount: "))
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

        return Item(name, amount, cost, source)
    
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

def checkOutItem() -> None:
    item_to_checkout: str = input("item to check out: ")
    checkout_amount: float = float(input("amount to check out: "))
    if item_to_checkout in Item.Inventory:
        item: Item = Item.Inventory[item_to_checkout] # use "item" as reference to item in inventory
        if item.amount >= checkout_amount and item.amount > 0:
            item.checkOut(checkout_amount)
            print(f"successfully checked out {checkout_amount} of {item_to_checkout}.")
        else:
            print(f"not enough {item_to_checkout} to check out. there are only {item.amount} left. checkout failed.")
    else:
        print(f"{item_to_checkout} does not exist. Try viewing the inventory to see all items.")

def checkInItem() -> None:
    item_to_checkin: str = input("item to check in: ")
    checkin_amount: float = float(input("amount to check in: "))
    if item_to_checkin in Item.Inventory:
        item: Item = Item.Inventory[item_to_checkin]
        item.checkIn(checkin_amount)
    else:
        print(f"{item_to_checkin} does not exist. Try viewing the inventory to see all items.")

def unpackInventory() -> pd.DataFrame:
    table: list = list()
    for key, item in Item.Inventory.items():
        table.append([key, item.amount, ("yes" if item.availability  else "no"), item.cost, item.source])
    
    # print(tabulate(table, headers=['Name', 'Amount', 'Available?', 'Cost', 'Source']))
    return pd.DataFrame(table, columns=["Name", "Amount", "Available?", "Cost", "Source"])

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
        print(tabulate(unpackInventory(), headers='keys',showindex=False, tablefmt='pipe', stralign='center', numalign='right')) # type: ignore
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
        inv = unpackInventory()
        gsheet_update.updateInvSheet(inv)