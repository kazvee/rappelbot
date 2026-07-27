from datetime import datetime
from zoneinfo import ZoneInfo
import json
import time
import os

import requests
from dotenv import load_dotenv


load_dotenv()


try:
    TIMEZONE = ZoneInfo(
        os.getenv("TIMEZONE", "UTC")
    )

except Exception as e:
    print("Invalid timezone:", e)
    raise SystemExit(1)


BROADCAST_RECIPIENT = os.getenv(
    "BROADCAST_RECIPIENT",
    "ALL"
)


try:
    with open("config.json") as f:
        config = json.load(f)

except Exception as e:
    print("Failed to load config:", e)
    raise SystemExit(1)


def wait_for_gotify():

    print("Waiting for Gotify...")

    for attempt in range(12):

        try:
            requests.get(
                config["gotify_url"],
                timeout=5
            )

            print("Gotify is ready")
            return

        except requests.exceptions.RequestException:

            print(
                f"Gotify unavailable ({attempt + 1}/12)"
            )

            time.sleep(5)

    print(
        "Gotify did not respond, continuing anyway"
    )


def send_notification(user, title, message, priority=10):

    token = (
        config
        .get("users", {})
        .get(user, {})
        .get("token")
    )

    if not token:

        print(
            "Missing token for user:",
            user
        )

        return


    try:

        response = requests.post(
            f'{config["gotify_url"]}/message?token={token}',
            data={
                "title": title,
                "message": message,
                "priority": priority
            },
            timeout=10
        )

        response.raise_for_status()

        print(
            "Sent to",
            user,
            response.status_code
        )


    except requests.exceptions.RequestException as e:

        print(
            "Notification failed:",
            user,
            e
        )


def send_to_recipient(recipient, title, message, priority=10):

    if recipient == "ALL":

        for user in config.get("users", {}):

            send_notification(
                user,
                title,
                message,
                priority
            )

    else:

        send_notification(
            recipient,
            title,
            message,
            priority
        )


def send_startup_notification():

    now = datetime.now(TIMEZONE)

    timestamp = now.strftime(
        "%Y-%m-%d %H:%M:%S %Z"
    )

    print(
        "Sending startup notification..."
    )

    send_to_recipient(
        BROADCAST_RECIPIENT,
        "RappelBot Started",
        f"💫 RappelBot started successfully.\n\nTime: {timestamp}",
        10
    )


def should_send(reminder):

    now = datetime.now(TIMEZONE)

    if reminder.get("time") != now.strftime("%H:%M"):

        return False


    repeat = reminder.get(
        "repeat",
        "none"
    )


    if repeat == "daily":

        return True


    if repeat == "weekdays":

        return now.weekday() < 5


    if repeat in (
        "weekly",
        "biweekly"
    ):

        start_date = datetime.strptime(
            reminder["date"],
            "%Y-%m-%d"
        ).date()


        days_since = (
            now.date() - start_date
        ).days


        if days_since < 0:

            return False


        if repeat == "weekly":

            return days_since % 7 == 0


        if repeat == "biweekly":

            return days_since % 14 == 0



    if repeat == "quarterly":

        start_date = datetime.strptime(
            reminder["date"],
            "%Y-%m-%d"
        ).date()


        months_since = (
            (now.year - start_date.year) * 12
            + now.month
            - start_date.month
        )


        return (
            months_since >= 0
            and months_since % 3 == 0
            and now.day == start_date.day
        )



    if repeat == "yearly":

        start_date = datetime.strptime(
            reminder["date"],
            "%Y-%m-%d"
        ).date()


        return (
            now.month == start_date.month
            and now.day == start_date.day
        )



    if repeat == "none":

        return (
            now.strftime("%Y-%m-%d")
            == reminder.get("date")
        )


    return False


print(
    "RappelBot starting..."
)


wait_for_gotify()


try:

    send_startup_notification()


except Exception as e:

    print(
        "Startup notification failed:",
        e
    )


last_sent = set()


while True:

    now = datetime.now(TIMEZONE)

    now_time = now.strftime("%H:%M")
    now_date = now.strftime("%Y-%m-%d")


    print(
        "Checking reminders:",
        now_time
    )


    try:

        with open("reminders.json") as f:

            reminders = json.load(f)


    except Exception as e:

        print(
            "Failed to load reminders:",
            e
        )

        time.sleep(10)

        continue



    for reminder in reminders:


        required_fields = [
            "id",
            "recipient",
            "title",
            "message"
        ]


        if not all(
            field in reminder
            for field in required_fields
        ):

            print(
                "Invalid reminder:",
                reminder
            )

            continue



        reminder_key = (
            f"{reminder['id']}-"
            f"{now_date}-"
            f"{now_time}"
        )


        if reminder_key in last_sent:

            continue



        if should_send(reminder):

            print(
                "SENDING:",
                reminder["id"]
            )


            send_to_recipient(
                reminder["recipient"],
                reminder["title"],
                reminder["message"],
                reminder.get("priority", 10)
            )


            last_sent.add(
                reminder_key
            )


    time.sleep(10)