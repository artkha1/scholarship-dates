# https://medium.com/@vince.shields913/reading-google-sheets-into-a-pandas-dataframe-with-gspread-and-oauth2-375b932be7bf
# https://developers.google.com/calendar/v3/reference/events

import logging
import os
from datetime import timedelta

import gspread
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()

CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE")
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")

if not all([CREDENTIALS_FILE, CALENDAR_ID, SHEET_NAME]):
    raise ValueError("Missing required environment variables.")


# Logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Google API setup

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/calendar",
]

credentials = Credentials.from_service_account_file(
    CREDENTIALS_FILE,
    scopes=SCOPES
)

gc = gspread.authorize(credentials)

worksheet = gc.open(SHEET_NAME).sheet1

calendar_service = build(
    "calendar",
    "v3",
    credentials=credentials
)


# Load spreadsheet data 
data = worksheet.get_all_values()
headers = data.pop(0)

scholarships = pd.DataFrame(data, columns=headers)
scholarships.replace(r'^\s*$', np.nan, regex=True, inplace=True)  # replace whitespace with NaN

# Convert date columns
date_columns = ["Deadline", "Winner \nAnnounced"]

for col in date_columns:
    scholarships[col] = pd.to_datetime(
        scholarships[col],
        errors="coerce"
    )

# Event creation (all-day event)
def create_event(name,date):
    if pd.isna(date):
        return None

    event = {
        "summary": name,
        "start": {
            "date": date.strftime("%Y-%m-%d")
        },
        "end": {
            "date": (
                date + timedelta(days=1)
            ).strftime("%Y-%m-%d")
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {
                    "method": "popup",
                    "minutes": 24 * 60  # remind 1 day before
                }
            ]
        }
    }

    created_event = (
        calendar_service.events()
        .insert(
            calendarId=CALENDAR_ID,
            body=event
        )
        .execute()
    )
    
    return created_event
    # 'primary' calendarId accesses the service account's calendar
    

def push_dates(row):
    if pd.isna(row['Event created']):  # if event wasn't created 
        scholarship_name = row['Scholarship Name']
        try:
            create_event(scholarship_name + ' Deadline', row['Deadline'])  # create deadline event
            logging.info(f"Created deadline event for {scholarship_name}")
            if not pd.isna(row['Winner \nAnnounced']):  # if winner announced date is recorded
                create_event(scholarship_name + ' winners announced', row['Winner \nAnnounced'])  # create winner announced event
                logging.info(f"Created winners announced event for {scholarship_name}")
        except Exception as e:
            logging.error(
                f"Failed processing "
                f"'{scholarship_name}': {e}"
            )

scholarships.apply(push_dates,axis=1)

event_created_col = headers.index('Event created') + 1

event_created_cells = worksheet.range(
    2,
    event_created_col,
    len(scholarships) + 1,
    event_created_col
)  # Event Created column

for cell in event_created_cells:
    cell.value = 'Y'
worksheet.update_cells(event_created_cells)  # change all values in the Event Created column to 'Y'