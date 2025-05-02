import requests
import smtplib
import os
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

TEAM_NAME = "Los Angeles Dodgers"
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")


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
                    is_home = team["homeAway"] == "home"
                    won = team.get("winner", False)

                    if is_home and won:
                        return True  # Dodgers won a home game
                    elif is_home and not won:
                        return False  # Dodgers lost a home game
        except Exception as e:
            print("Error parsing event:", e)

    return None  # No home game was found yesterday


def send_email(result):
    # Read the HTML template based on the result
    if result is True:
        with open("templates/dodgers_win.html", "r") as file:
            email_body = file.read()
        subject = "🎉 Dodgers Victory Alert! 🎉"
    elif result is False:
        with open("templates/dodgers_loss.html", "r") as file:
            email_body = file.read()
        subject = "💔 Dodgers Lost Yesterday 💔"
    else:
        with open("templates/no_game.html", "r") as file:
            email_body = file.read()
        subject = "⚾️ No Dodgers Game Yesterday ⚾️"

    msg = MIMEMultipart()
    msg["Subject"] = subject  # Updated subject based on result
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.attach(MIMEText(email_body, "html"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)


def main():
    result = check_dodgers_result()
    print(result, f"Dodger Game Result {get_yesterday_date()}")
    send_email(result)


if __name__ == "__main__":
    main()
