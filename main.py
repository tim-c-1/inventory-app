from tabulate import tabulate
from typing import Self
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
    dItem: str = input("enter name of item to delete: ")
    check: str = input(f"are you sure you want to delete {dItem}? This action is permanent and cannot be undone. (y/n): ").lower()
    if dItem in Item.Inventory:
        if check == "y":
            del Item.Inventory[dItem]
        else:
            print("delete aborted.")
    else:
        print(f"{dItem} does not exist. Try viewing the inventory to see all items.")

def checkOutItem() -> None:
    cItem: str = input("which item are you checking out?: ")
    cAmount: float = float(input("amount to check out: "))
    if cItem in Item.Inventory:
        item: Item = Item.Inventory[cItem] # use "item" as reference to item in inventory
        if item.amount >= cAmount and item.amount > 0:
            item.amount = item.amount - cAmount
            print(f"successfully checked out {cAmount} of {cItem}.")
            if item.amount == 0:
                item.availability = False # check for updated availability when checking out item 
        else:
            print(f"not enough {cItem} to check out. there are only {item.amount} left. checkout failed.")
    else:
        print(f"{cItem} does not exist!")

def viewInventory() -> None:
    table: list = list()
    for key, item in Item.Inventory.items():
        table.append([key, item.amount, ("yes" if item.availability  else "no")])
    print(tabulate(table, headers=['Name', 'Amount', 'Available?']))

# CLI loop
loop = True
for n in range(50): print("-",sep=' ', end='', flush=True)
print("\nWelcome to the inventory system.\n")
while loop:
    for n in range(50): print("-",sep=' ', end='', flush=True)
    selection: str = input("\nWhat would you like to do?\n"\
                        "(N)ew item\n"\
                        "(D)elete item\n"\
                        "(C)heck out items\n"\
                        "(V)iew inventory\n"\
                        "(E)xit\n"\
                        ).lower() # get user selection, accept any case
    if selection == "n" or selection == "new":
        createNewItem() # create new item
    elif selection == "d" or selection == "delete":
        deleteItem() # delete item function
    elif selection == "c" or selection == "check":
        checkOutItem() # make call to checkout function
    elif selection == "v" or selection == "view":
        viewInventory()
    elif selection == "e" or selection == "exit":
        loop = False