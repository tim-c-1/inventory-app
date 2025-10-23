import gspread
from pandas import DataFrame
import os
import json
import datetime

def authUser() -> gspread.Client | None: # may not need this? it checks the expiration time in the auth_user token, but if gspread auto refreshes then won't need
    # there's gotta be a native way to pass the refresh token from credentials.json in the event of an expired token...

    credentials = 'authentication/credentials.json'
    auth = 'authentication/authorized_user.json'
    try:
        with open(auth, 'r') as f:
            token = json.load(f)
        expiry = token['expiry']
        expiry_formatted = expiry[:10] + ' ' + expiry[11:-1]
        exp_time = datetime.datetime.strptime(expiry_formatted, "%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.now()
        if exp_time < now:
            os.remove(auth)
            gc = gspread.oauth(credentials_filename=credentials, authorized_user_filename=auth)
            return gc
        else:
            gc = gspread.oauth(credentials_filename=credentials, authorized_user_filename=auth)
            return gc
    except Exception:
        try:
            gc = gspread.oauth(credentials_filename=credentials, authorized_user_filename=auth)
            return gc
        except Exception as e:
            print(f"something went wrong, exception: {e}")
    

def updateInvSheet(inv: DataFrame, spreadsheet: str) -> None:

    gc = authUser()

    if gc is not None:
        sh = gc.open(spreadsheet)
        worksheet = sh.get_worksheet(0)
        worksheet.update([inv.columns.values.tolist()] + inv.values.tolist())
    else:
        print("gc returned as failed. check exception.")

def setupAuth(credentials, auth) -> gspread.Client:
    # for first time setup?
    gc = gspread.oauth(credentials_filename=credentials, authorized_user_filename=auth)
    return gc