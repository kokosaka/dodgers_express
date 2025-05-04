from typing import TypedDict
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
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
email_to_list = os.getenv("EMAIL_TO", "").split(",")
email_to_list = [email.strip() for email in email_to_list if email.strip()]


class GameResult(TypedDict):
    is_home: bool
    won: bool


def get_yesterday_date():
    return (datetime.now() - timedelta(days=1)).date()


def check_dodgers_result() -> GameResult | None:
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

                    return dict(is_home=is_home, won=won)

        except Exception as e:
            print("Error parsing event:", e)

    return None  # No home game was found yesterday


from email.mime.image import MIMEImage  # Add this at the top

from email.mime.image import MIMEImage


def send_email_individually(result: GameResult | None):
    if result["is_home"] and result["won"]:
        with open("templates/dodgers_home_win.html", "r") as file:
            email_body = file.read()
        subject = "🎉 Dodgers Victory Alert! 🎉"

        # Embed image using cid
        email_body = email_body.replace("{{IMAGE_CID}}", "image1")

        # Attach the image and create the message
        with open("static/dodgers_express_win.png", "rb") as img:
            image = MIMEImage(img.read())
            image.add_header("Content-ID", "<image1>")

        # Loop through each recipient and send individually
        for email in email_to_list:
            msg = MIMEMultipart("related")
            msg["Subject"] = subject
            msg["From"] = EMAIL_FROM
            msg["To"] = email  # Send individually to each email (single recipient)

            msg_alternative = MIMEMultipart("alternative")
            msg.attach(msg_alternative)
            msg_alternative.attach(MIMEText(email_body, "html"))

            # Attach the image
            msg.attach(image)

            # Send the email to this specific recipient
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(
                    EMAIL_FROM, email, msg.as_string()
                )  # Corrected sendmail

            print(f"email sent to {email}")


def main():
    result = check_dodgers_result()
    print(result, f"Dodger Game Result {get_yesterday_date()}")
    send_email_individually(result)


if __name__ == "__main__":
    main()
