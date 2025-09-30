from tabulate import tabulate
# create method for creating objects of items
    # every item should have name, amount, availability (based on amount), cost(optional), item source
    # should each item hold individual objects or just have an amount attribute

# display function should tabulate the inventory items
# you should be able to check out a custom amount of items, not to exceed the amount available
# you should be able to edit the item's attributes

Inventory = set()

class Item: 
    def __init__(self, name, amount):
        self.name: str = name
        self.amount: float = amount
        self.availability: bool = True if amount > 0 else False
        Inventory.add(self)


def newItem() -> Item:
    name = input("item name: ")
    amount = float(input("Item amount: "))
    return Item(name, amount)




# CLI loop
loop = ""
for n in range(50): print("-",sep=' ', end='', flush=True)
while loop is not "Exit":
    selection = input("\nwelcome to the inventory system.\n"\
                        "What would you like to do?\n"\
                        "(N)ew item\n"\
                        "(D)elete item\n"\
                        "(V)iew inventory\n"\
                        "(E)xit\n"\
                        ).lower()
    if selection == "n" or selection == "new":
        item = newItem()
    elif selection == "v" or selection == "view":
        table = []
        for i in Inventory:
            table.append([i.name, i.amount, ("yes" if i.availability  else "no")])
        print(tabulate(table, headers=['Name', 'Amount', 'Available?']))
            # print(tabulate([[i.name, i.amount, ("yes" if i.availability  else "no")]], headers=['Name', 'Amount', 'Available?']))
    elif selection == "e" or selection == "exit":
        loop = "Exit"