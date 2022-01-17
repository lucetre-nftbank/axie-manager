# Imports
import math
import time

# > Standard library
import requests
import datetime
import json

# 3rd party dependencies
import pandas as pd
import gspread
import gspread_dataframe as gd

# Local files
from helper import ws_df, add_worksheet, gc
from winrate import get_winrate
from overview import update_sheet


def get_stats(spreadsheet_name, worksheet_name):
    """
    Reads the scholars from the Scholars spreadsheet
    Writes the scholars info in Scholar Stats + Manager name
    """

    print(f"Getting scholar stats at {datetime.datetime.now()}")

    today = datetime.datetime.today()

    scholar_info = get_scholars(spreadsheet_name, worksheet_name)
    managers = set(scholar_info["Manager"].tolist())

    # Get all addresses and join together as a string seperated by commas
    together = ",".join(scholar_info["Address"].tolist())

    # Call all addresses at once and retreive json
    try:
        response = requests.get(
            "https://game-api.axie.technology/api/v1/" + together
        ).json()
    except Exception as e:
        print(e)
        return

    df = pd.DataFrame.from_dict(response, orient='index')

    # Reset index and rename old index as addresses
    df = df.rename_axis("Address").reset_index()

    # Convert to datetime and string
    df["cache_last_updated"] = pd.to_datetime(
        df["cache_last_updated"], unit="ms"
    ).dt.strftime("%m-%d, %H:%M")
    df["last_claim"] = pd.to_datetime(df["last_claim"], unit="s").dt.strftime("%m-%d")
    df["next_claim"] = pd.to_datetime(df["next_claim"], unit="s").dt.strftime("%m-%d")

    df = df.rename(
        columns={
            "cache_last_updated": "Updated On",
            "in_game_slp": "Game SLP",
            "ronin_slp": "Ronin SLP",
            "total_slp": "Total SLP",
            "lifetime_slp": "Lifetime SLP",
            "rank": "Rank",
            "mmr": "MMR",
            "last_claim": "Last Claim",
            "next_claim": "Next Claim",
        }
    )
    
    # Add managers to df
    df = pd.merge(
        df, scholar_info[["Manager", "Address"]], left_index=False, right_index=False
    )

    # Add date
    df["Date"] = today

    for manager in managers:
        # Set variables for overview
        daily_slp = 0
        total_slp = 0
        total_lifetime = 0
        total_scholar_share = 0

        scholar_dict = {}
        scholar_dict["Date"] = today

        # Open the spreadsheet
        try:
            manager_sheet = f"{manager}"
            print(f"\nManager {manager}")
            sheet = gc.open(manager_sheet)

        # If the spreadsheet does not exist, create it in folder specified in auth.json
        except gspread.exceptions.SpreadsheetNotFound:
            with open("auth.json") as f:
                data = json.load(f)
            sheet = gc.create(manager_sheet, data["folder_id"])

        # Get scholars corresponding with this managers
        scholar_names = df.loc[df["Manager"] == manager]["name"].tolist()

        # Update every scholar
        for i, scholar_name in enumerate(scholar_names):
            if scholar_name == None:
                print(f"Skipping unregistered scholar...")
                continue
                
            print(f"Updating {scholar_name}'s stats", end=' - ')
            
            # Get the row from the df
            scholar_df = df.loc[df["name"] == scholar_name]
            
            # Set local variables
            try:
                address = scholar_df["Address"].tolist()[0]
            except Exception:
                # Skip this scholar
                continue
                
            # New Scholar Name
            scholar_name = scholar_info.loc[scholar_info["Address"] == address]["Scholar Name"].tolist()[0]    
            
            print(scholar_df['Updated On'].values[0])
            # Remove clutter
            scholar_df = scholar_df[
                [
                    "Date",
                    "Game SLP",
                    "Ronin SLP",
                    "Total SLP",
                    "Lifetime SLP",
                    "Rank",
                    "MMR",
                    "Last Claim",
                    "Next Claim",
                    "Updated On",
                ]
            ].set_index("Date")

            # Open a specific worksheet, worksheet for every account
            try:
                ws = sheet.worksheet(scholar_name)

            # If it does not exist, make one
            except gspread.exceptions.WorksheetNotFound:
                ws = add_worksheet(scholar_name, manager_sheet)

            # Get the existing worksheet as dataframe
            existing = ws_df(ws)

            # Add win data of today, disabled for now
            # df = pd.concat([df, get_winrate(address)], axis=1)

            # Combine the dataframes
            combined = existing.append(scholar_df)

            # Do calculations
            combined["SLP Diff"] = combined["Game SLP"].diff()

            # SLP Today cannot be negative
#             combined.loc[combined["SLP Diff"] < 0, "SLP Diff"] = 0
            # combined["SLP Today"][combined["SLP Today"] < 0] = 0

            # Catch NaN
            criterion = "Game SLP"
            gained = 0 if math.isnan(combined.tail(1)[criterion].tolist()[0]) else combined.tail(1)[criterion].tolist()[0]
                
            # Reorder columns
            combined = combined[['SLP Diff', 'Game SLP', 'Ronin SLP', 'Total SLP', 'Lifetime SLP', 'MMR', 'Rank', 'Last Claim', 'Next Claim', 'Updated On']]

            # Upload it to worksheet
            gd.set_with_dataframe(ws, combined, include_index=True)

            # Update variables for Overview
            daily_slp += gained

            new_slp = scholar_df["Game SLP"].tolist()[0]
            total_slp += new_slp
            
            total_lifetime += scholar_df["Lifetime SLP"].tolist()[0]

            # Read the scholar split, using account address
#             split = scholar_info.loc[scholar_info["Address"] == address][
#                 "Scholar Share"
#             ].tolist()[0]
            split = 0.4
            total_scholar_share += split * new_slp

            # Save this in the dict
            scholar_dict[scholar_name] = gained
            
            if (i+1) % 10 == 0:
                time.sleep(20)

        # Scholar Overview shows everyone's daily SLP
        update_sheet(
            "Scholar Overview",
            pd.DataFrame([scholar_dict]).set_index("Date"),
            manager_sheet,
        )
        print(f"Updated {manager}'s overview")
        time.sleep(20)


def get_scholars(spreadsheet_name, worksheet_name):
    """Simple function to read the "Scholars" worksheet and return the dataframe"""

    # Open the worksheet of the specified spreadsheet
    ws = gc.open(spreadsheet_name).worksheet(worksheet_name)
    scholar_info = (
        gd.get_as_dataframe(ws).dropna(axis=0, how="all").dropna(axis=1, how="all")
    )

    # Replace ronin: with 0x for API
    scholar_info["Address"] = scholar_info["Address"].str.replace("ronin:", "0x")

    return scholar_info
