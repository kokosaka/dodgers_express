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


def send_email(result: GameResult | None):
    # if result is None:
    #     template_path = "templates/no_game.html"
    #     subject = "⚾️ No Dodgers Game Yesterday ⚾️"
    #     image_path = "static/dodgers_no_game.png"
    #     image_cid = "no_game"
    if result["won"] and result["is_home"]:
        template_path = "templates/dodgers_home_win.html"
        subject = "🎉 Dodgers Home Victory! 🎉"
        image_path = "static/dodgers_express_win.png"
        image_cid = "home_win"
    # elif result["won"] and not result["is_home"]:
    #     template_path = "templates/dodgers_away_win.html"
    #     subject = "🎉 Dodgers Away Victory! 🎉"
    #     image_path = "static/dodgers_away_win.png"
    #     image_cid = "away_win"
    # else:
    #     template_path = "templates/dodgers_loss.html"
    #     subject = "💔 Dodgers Lost Yesterday 💔"
    #     image_path = "static/dodgers_loss.png"
    #     image_cid = "loss"

    # Read and inject CID into template
    with open(template_path, "r") as file:
        email_body = file.read().replace("{{IMAGE_CID}}", image_cid)

    # Prepare message
    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = ", ".join(email_to_list)

    msg_alternative = MIMEMultipart("alternative")
    msg.attach(msg_alternative)
    msg_alternative.attach(MIMEText(email_body, "html"))

    # Attach image
    if os.path.exists(image_path):
        with open(image_path, "rb") as img:
            image = MIMEImage(img.read())
            image.add_header("Content-ID", f"<{image_cid}>")
            msg.attach(image)

    # Send email
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg, to_addrs=email_to_list)


def main():
    result = check_dodgers_result()
    print(result, f"Dodger Game Result {get_yesterday_date()}")
    send_email({'is_home': True, 'won': True})


if __name__ == "__main__":
    main()
