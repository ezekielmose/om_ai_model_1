import gspread
from oauth2client.service_account import ServiceAccountCredentials

SHEET_ID = "15JtixXapWqPBxtUVevN-0nSbUgKHU86Lj6p3Fmqd5Uc"


def connect_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json",
        scope
    )

    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).sheet1


def save_reel_summary(reel_url, duration, quality_result):

    sheet = connect_sheet()

    sheet.append_row([
        reel_url,
        duration,
        quality_result["score"],
        ", ".join(quality_result["flags"])
    ])
