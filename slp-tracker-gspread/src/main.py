import threading

# Local files
from scholars import get_stats


def update():
    # Do this every 1 hour (minimum)
    threading.Timer(3600, update).start()

    spreadsheet = "Stats"
    worksheet = "Scholars"
    get_stats(spreadsheet, worksheet)



if __name__ == "__main__":

    # Update the spreadsheet
    update()

    # Delete every worksheet in Scholar Stats unless last_claim is later than now
