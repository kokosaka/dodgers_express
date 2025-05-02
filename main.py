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


def send_email(outcome):
    if outcome == "win":
        subject = "🎉 Dodgers Victory Alert! 🎉"
        body = """
        <html>
          <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
            <h2 style="color: #005A9C;">🎉 Home Run News! 🎉</h2>
            <p>The <strong>Dodgers</strong> crushed it at <em>home</em> yesterday!</p>
            <p style="font-size: 1.2em;">💙⚾️ Time to break out the peanuts and Cracker Jack! ⚾️💙</p>
            <hr />
          </body>
        </html>
        """
    elif outcome == "loss":
        subject = "😢 Dodgers Game Loss Update"
        body = """
        <html>
          <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
            <h2 style="color: #C41E3A;">💔 Tough Luck, Dodgers 💔</h2>
            <p>Unfortunately, the <strong>Dodgers</strong> didn't win yesterday.</p>
            <p style="font-size: 1.2em;">But hey, there's always the next game! 💪</p>
            <hr />
          </body>
        </html>
        """
    else:
        subject = "🤷‍♂️ No Dodgers Game Yesterday"
        body = """
        <html>
          <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
            <h2 style="color: #9E9E9E;">No Game Yesterday? 🤷‍♂️</h2>
            <p>It looks like there was no game for the <strong>Dodgers</strong> yesterday.</p>
            <p style="font-size: 1.2em;">We'll catch them next time!</p>
            <hr />
          </body>
        </html>
        """

    # Create the email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    # Text version (fallback for non-HTML clients)
    text = "The Dodgers game result: " + subject

    # HTML version
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(body, "html")

    msg.attach(part1)
    msg.attach(part2)

    # Send the email
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)


def main():
    result = check_dodgers_result()
    print(result)
    if result is True:
        print("Dodgers win yesterday.")
        send_email("win")
    elif result is False:
        print("Dodgers did not win yesterday.")
        send_email("loss")
    else:
        print("No game was found yesterday.")
        send_email("none")


if __name__ == "__main__":
    main()
