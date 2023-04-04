
from flask import Flask, jsonify
from flask_cors import CORS

import os.path
import datetime
import json

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError




import time

last_updated = 0


app = Flask(__name__)
CORS(app)
data = None
irk = 0

def update_stars():
    print("updating stars")
    x = datetime.datetime.now()
    hr = x.strftime("%H")
    mins = x.strftime("%M")
    current_time = f"{hr}:{mins}"
    day = x.strftime("%d")
    month = x.strftime("%m")
    yr = x.strftime("%y")
    current_date = f"{yr}{month}{day}"
    global data
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    starsheet = '1o_iQTCkG0dOi8KPxptfgKvzo7It8w5w33ACTJj9rN5A'
    range_upcoming = 'Upcoming Stars by Time!A2:A'
    range_active = 'Dropped Stars (30m-120m)!A2:A'
    star_data = {"Active": [], "Upcoming": []}
    creds = None
    print("checking token.json...")
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        print(creds)
    # If there are no (valid) credentials available, do fucking nothing


    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()

        result_upcoming = sheet.values().get(spreadsheetId=starsheet,
                                    range=range_upcoming).execute()
        values_upcoming = result_upcoming.get('values', [])


        result_active = sheet.values().get(spreadsheetId=starsheet,
                                    range=range_active).execute()
        values_active = result_active.get('values', [])

       # if not (values_upcoming or values_active):
       #     print('No data found.')
      #      return

        for row in values_upcoming:
            star_data['Upcoming'].append(row[0])
        for row in values_active:
            star_data['Active'].append(row[0])

    except HttpError as err:
        print(err)
    data = star_data
    print(type(data))
    print(type(star_data))
    log_file = star_data.copy()
    print(log_file)
    print(type(log_file))
    log_entry = {"date": current_date, "Time": current_time, "data": log_file}
    print(log_entry)
    with open("logs.json", 'a') as f:
        json.dump(log_entry, f)
        f.write('\n')



@app.route('/data', methods=['GET'])
def get_stars():
    global last_updated
    if not data or time.time() - last_updated > 300:
        update_stars()
        last_updated = time.time()
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)


