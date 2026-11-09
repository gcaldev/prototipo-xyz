from datetime import datetime
from zoneinfo import ZoneInfo

from common.config import TIMEZONE

ZONE = ZoneInfo(TIMEZONE)


def now():
    return datetime.now(ZONE)


def display_date():
    return now().strftime("%d-%m-%Y")


def audit_timestamp():
    return now().isoformat()
