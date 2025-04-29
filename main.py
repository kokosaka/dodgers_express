import requests
import smtplib
import os
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

TEAM_NAME = "Los Angeles Dodgers"
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")  # App-specific password


def get_yesterday_date():
    return (datetime.now() - timedelta(days=1)).date()


def check_dodgers_result():
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={yesterday}"
    response = requests.get(url)
    data = response.json()
    for event in data.get("events", []):
        try:
            competition = event["competitions"][0]
            teams = competition["competitors"]

            for team in teams:
                if team["team"]["displayName"] == TEAM_NAME:
                    if team.get("winner"):
                        return True  # Dodgers won
                    else:
                        return False  # Dodgers lost
        except Exception as e:
            print("Error parsing event:", e)

    return None  # No game found


def send_email():
    msg = MIMEText("The Dodgers won yesterday! 🎉")
    msg["Subject"] = "Dodgers Victory Alert!"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)


def main():
    result = check_dodgers_result()
    print(result)
    if result is True:
        print("Dodgers win yesterday.")
        send_email()
    elif result is False:
        print("Dodgers did not win yesterday.")
    else:
        print("No game was found yesterday.")


if __name__ == "__main__":
    main()
