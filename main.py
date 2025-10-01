from tabulate import tabulate
from typing import Self
import pickle
import os
# create method for creating objects of items
    # every item should have name, amount, availability (based on amount), cost(optional), item source
    # should each item hold individual objects or just have an amount attribute

# display function should tabulate the inventory items
# you should be able to check out a custom amount of items, not to exceed the amount available
# you should be able to edit the item's attributes

class Item: 
    Inventory: dict[str, Self] = dict()
    def __init__(self, name: str, amount: float) -> None:
        self.name: str = name
        self.amount: float = amount
        self.availability: bool = True if amount > 0 else False
        Item.Inventory[self.name] = self


def createNewItem() -> Item | None:
    name = input("item name: ")
    amount = float(input("Item amount: "))
    if "%s" % (name) not in Item.Inventory:
        return Item(name, amount)
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
            item.amount -= checkout_amount
            print(f"successfully checked out {checkout_amount} of {item_to_checkout}.")
            if item.amount == 0:
                item.availability = False # check for updated availability when checking out item 
        else:
            print(f"not enough {item_to_checkout} to check out. there are only {item.amount} left. checkout failed.")
    else:
        print(f"{item_to_checkout} does not exist!")

def checkInItem() -> None:
    item_to_checkin: str = input("item to check in: ")
    checkin_amount: float = float(input("amount to check in: "))
    if item_to_checkin in Item.Inventory:
        item: Item = Item.Inventory[item_to_checkin]
        item.amount += checkin_amount


def viewInventory() -> None:
    table: list = list()
    for key, item in Item.Inventory.items():
        table.append([key, item.amount, ("yes" if item.availability  else "no")])
    print(tabulate(table, headers=['Name', 'Amount', 'Available?']))

def saveInventory() -> None:
    with open('Inventory.pickle', 'wb') as f:
        pickle.dump(Item.Inventory, f, pickle.HIGHEST_PROTOCOL)

def loadInventory():
    with open('Inventory.pickle', 'rb') as f:
        return pickle.load(f)

# load existing on startup
if os.path.exists('./Inventory.pickle'):
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
                        "(E)xit\n"\
                        ).lower() # get user selection, accept any case
    if selection == "n" or selection == "new":
        createNewItem() # create new item
    elif selection == "d" or selection == "delete":
        deleteItem() # delete item function
    elif selection == "o" or selection == "out":
        checkOutItem() # make call to checkout function
    elif selection == "i" or selection == "in":
        checkInItem()
    elif selection == "v" or selection == "view":
        viewInventory()
    elif selection == "e" or selection == "exit":
        loop = False

save:bool = True if input("save inventory? (y/n)").lower() == "y" else False
print(save)
if save:
    # do save stuff
    saveInventory()
    pass