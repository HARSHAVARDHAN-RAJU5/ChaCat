from datetime import datetime

def check_reminders():
    now = datetime.now()
    hour = now.hour
    minute = now.minute

    if hour == 00 and minute == 0:
        return "sleep"

    if (hour == 13 and minute == 1) or (hour == 20 and minute == 1):
        return "food"

    if hour == 18 and minute == 1:
        return "grocery"

    if hour == 22 and minute == 1:
        return "bath"

    return None
