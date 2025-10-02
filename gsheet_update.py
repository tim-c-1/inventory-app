import gspread
from pandas import DataFrame

def updateInvSheet(inv: DataFrame) -> None:
    
    gc = gspread.oauth()

    sh = gc.open("InvTest")

    worksheet = sh.get_worksheet(0)

    worksheet.update([inv.columns.values.tolist()] + inv.values.tolist())