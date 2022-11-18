from datetime import date 
import pandas as pd
from send_emails import send_email
from deta import app

# Public GoogleSheets url - not secure!
SHEET_ID = os.environ.get("SHEET_ID")

SHEET_NAME = "Sheet1"  
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"


def load_df(url):
    parse_dates = ["session_date"]
    df = pd.read_csv(url, parse_dates=parse_dates)
    return df

print(load_df(URL))


def query_data_and_send_emails(df):
    present = date.today()
    email_counter = 0
    for _, row in df.iterrows():
        if (present == row["session_date"].date()) and (row["rescheduled"] == "no"):
            send_email(
                subject=f'Reminder For Your Session Today at {row["session_time"]}',
                receiver_email=row["email"],
                name=row["name"],
                session_time=row["session_time"],
                student_name=row["student_name"],
                session_date=row["session_date"].strftime("%d, %b %Y"),  # example: 11, Aug 2022
                school_subject=row["school_subject"],
                zoom_link=row["zoom_link"],
            )
            email_counter += 1
    return f"Total Emails Sent: {email_counter}"

df = load_df(URL)
result = query_data_and_send_emails(df)
print(result)

# we can add another function which on Sunday evening visits the row['rescheduled'] and changes all of the 'yes' to 'no', fresh for the next week 

@app.lib.cron()
def cron_job(event):
    df = load_df(URL)
    result = query_data_and_send_emails(df)
    return result