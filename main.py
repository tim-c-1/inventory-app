# from tabulate import tabulate
# create method for creating objects of items
    # every item should have name, amount, availability (based on amount), cost(optional), item source
    # should each item hold individual objects or just have an amount attribute

# display function should tabulate the inventory items
# you should be able to check out a custom amount of items, not to exceed the amount available
# you should be able to edit the item's attributes

class Item: 
    Inventory: dict = dict()
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


# CLI loop
loop = ""
for n in range(50): print("-",sep=' ', end='', flush=True)
while loop:
    selection: str = input("\nwelcome to the inventory system.\n"\
                        "What would you like to do?\n"\
                        "(N)ew item\n"\
                        "(D)elete item\n"\
                        "(V)iew inventory\n"\
                        "(E)xit\n"\
                        ).lower()
    if selection == "n" or selection == "new":
        createNewItem() # create new item
    elif selection == "d" or selection == "delete":
        dItem = input("enter name of item to delete: ")
        if dItem in Item.Inventory:
            del Item.Inventory[dItem]
    elif selection == "v" or selection == "view":
        table: list = list()
        for i in Item.Inventory:
            table.append([i.name, i.amount, ("yes" if i.availability  else "no")])
        # print(tabulate(table, headers=['Name', 'Amount', 'Available?']))
    elif selection == "e" or selection == "exit":
        loop = False