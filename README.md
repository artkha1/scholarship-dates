# Scholarship Dates to Google Calendar

This project automates the process of adding scholarship deadlines and announcement dates to your Google Calendar. The data is sourced from a Google Sheets document, and the application uses the Google Sheets API and Google Calendar API to perform the integration.

## Overview

The script reads scholarship dates from a Google Sheets document and creates events in Google Calendar based on these dates. It handles deadlines and winner announcement dates.

## Features

- Reads scholarship information from a Google Sheets document.
- Adds scholarship deadlines and winner announcement dates to Google Calendar.

## Prerequisites

- Python 3.x
- Google Cloud credentials with access to Google Sheets API and Google Calendar API
- Required Python libraries:
  - `gspread`
  - `oauth2client`
  - `pandas`
  - `numpy`
  - `google-api-python-client`

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/scholarship-dates.git
   cd scholarship-dates
