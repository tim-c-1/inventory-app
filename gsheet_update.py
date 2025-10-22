import gspread
from pandas import DataFrame
import os
import json
import datetime

def authUser() -> gspread.Client: # may not need this? it checks the expiration time in the auth_user token, but if gspread auto refreshes then won't need
    # there's gotta be a native way to pass the refresh token from credentials.json in the event of an expired token...

    credentials = 'authentication/credentials.json'
    auth = 'authentication/authorized_user.json'
    with open(auth, 'r') as f:
        token = json.load(f)
    expiry = token['expiry']
    expiry_formatted = expiry[:10] + ' ' + expiry[11:-1]
    exp_time = datetime.datetime.strptime(expiry_formatted, "%Y-%m-%d %H:%M:%S")
    now = datetime.datetime.now()
    if exp_time < now:
        os.remove(auth)
        gc = gspread.oauth(credentials_filename=credentials, authorized_user_filename=auth)
    else:
        gc = gspread.oauth(credentials_filename=credentials, authorized_user_filename=auth)

    return gc

def updateInvSheet(inv: DataFrame, spreadsheet: str) -> None:
    credentials = 'authentication/credentials.json'
    auth = 'authentication/authorized_user.json'

    # gc = authUser()
    gc = gspread.oauth(credentials_filename=credentials, authorized_user_filename=auth)
    sh = gc.open(spreadsheet)
    worksheet = sh.get_worksheet(0)
    worksheet.update([inv.columns.values.tolist()] + inv.values.tolist())
    # try:
    #     gc = gspread.oauth(credentials_filename=credentials, authorized_user_filename=auth)

    #     sh = gc.open(spreadsheet)

    #     worksheet = sh.get_worksheet(0)

    #     worksheet.update([inv.columns.values.tolist()] + inv.values.tolist())
    # except:
    #     os.remove(auth)
        
    #     gc = gspread.oauth(credentials_filename=credentials, authorized_user_filename=auth)

    #     sh = gc.open(spreadsheet)

    #     worksheet = sh.get_worksheet(0)

    #     worksheet.update([inv.columns.values.tolist()] + inv.values.tolist())


