import gspread
import gspread_dataframe as gd
import pandas as pd

# Local files
from helper import ws_df, add_worksheet, gc, client


def update_sheet(ws_name, df, spreadsheet_name):
    """Updates the specified worksheet, using the data of df"""

    # Open the overview worksheet and make it a df
    try:
        ws = gc.open(spreadsheet_name).worksheet(ws_name)
    except gspread.exceptions.WorksheetNotFound:
        ws = add_worksheet(ws_name, spreadsheet_name)

    old_overview = ws_df(ws)

    # Overwrite whole sheet if it is empty
    if old_overview.empty:
        print("Empty existing dataframe for: " + ws_name)
        gd.set_with_dataframe(ws, df, include_index=True)

    # If that is not the case, get the old info
    else:
        # Last (and only) index of dataframe is today
        today = df.index[-1]

        if today in old_overview.index:
            # Overwrite index of today
            old_overview.loc[today] = df.loc[today]
            updated_overview = old_overview

        # Append dataframe to it
        else:
            updated_overview = old_overview.append(df)

        # Upload it to worksheet
        gd.set_with_dataframe(ws, updated_overview, include_index=True)

