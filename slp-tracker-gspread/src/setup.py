# Standard libraries
import json
import gspread
from main import update

# Login using the .json file
gc = gspread.service_account(filename="auth.json")

def create_scholars_sheet():
    """Create a new Scholars spreadsheet"""
    try:
        sheet = gc.open("Stats")
        print("Found existing Scholar Stats spreadsheet")
    except gspread.exceptions.SpreadsheetNotFound:
        with open("auth.json") as f:
            data = json.load(f)
            sheet= gc.create("Stats", data["folder_id"])
            print("Creating Scholar Stats spreadsheet")
        
    # Create the worksheets
    try:
        ws = sheet.worksheet("Scholars")
        print("Found existing Scholars worksheet")
    # If it does not exist, make one
    except gspread.exceptions.WorksheetNotFound:
        ws = gc.open("Stats").add_worksheet(title="Scholars", rows="100", cols="20")
        print("Creating Scholars worksheet")

    # Add the default first row
    ws.update(
        "A1:F1",
        [
            [
                "Manager",
                "Scholar Name",
                "Address",
            ]
        ],
    )

if __name__ == "__main__":
    # Create the Scholars spreadsheet + worksheet
    create_scholars_sheet()
    
    print("Please fill in the information in the Scholars worksheet, located in Scholar Stats spreadsheet")

    print("If you filled in the information, please run: python src/main.py to update the Scholar Stats sheet")