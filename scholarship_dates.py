#https://medium.com/@vince.shields913/reading-google-sheets-into-a-pandas-dataframe-with-gspread-and-oauth2-375b932be7bf
#https://developers.google.com/calendar/v3/reference/events

import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import pandas as pd
import numpy as np
from datetime import timedelta

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/calendar']

CREDENTIALS_FILE = 'scholarship-dates-63e61857065e.json'
CALENDAR_ID = 'timkhaiet@gmail.com'

credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scope)


gc = gspread.authorize(credentials)

wks = gc.open("Scholarship Application Organizer (Red = apply early, Orange = Last Year's Deadline)").sheet1  # worksheet

data = wks.get_all_values()
headers = data.pop(0)

scholarships = pd.DataFrame(data, columns=headers)
scholarships.replace(r'^\s*$', np.nan, regex=True, inplace=True)  # replace whitespace with NaN

scholarships['Winner \nAnnounced'] = pd.to_datetime(scholarships['Winner \nAnnounced'], errors='coerce')
scholarships['Deadline'] = pd.to_datetime(scholarships['Deadline'], errors='coerce')

service = build('calendar', 'v3', credentials=credentials)

def create_event(name,date):
    event = {
      'summary': name,
      'start': {'date': date.strftime('%Y-%m-%d')},
      'end': {'date': (date+timedelta(days=1)).strftime('%Y-%m-%d')},  
      'reminders': {
        'useDefault': False,
        'overrides': [{'method': 'popup', 'minutes': 24 * 60}]  # remind 1 day before
      },
    }
    return service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    # 'primary' calendarId accesses the service account's calendar
    

def push_dates(row):
    if pd.isna(row['Event created']):  # if event wasn't created yet
        create_event(row['Scholarship Name'] + ' Deadline', row['Deadline'])  # create deadline event
        if not pd.isna(row['Winner \nAnnounced']):  # if winner announced date is recorded
            create_event(row['Scholarship Name'] + ' winners announced', row['Winner \nAnnounced'])  # create winner announced event

scholarships.apply(push_dates,axis=1)

event_created_cells = wks.range(f'J2:J{len(scholarships)+1}')  # Event Created column
for cell in event_created_cells:
    cell.value = 'Y'
wks.update_cells(event_created_cells)  # change all values in the Event Created column to 'Y'