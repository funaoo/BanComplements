import time

UNITS = {"s": 1, "m": 60, "h": 3600, "d": 86400}


def parse_duration(text: str) -> int | None:
    text = text.strip().lower()
    if len(text) < 2 or text[-1] not in UNITS or not text[:-1].isdigit():
        return None
    return int(text[:-1]) * UNITS[text[-1]]


def format_remaining(expires_at: float) -> str:
    return format_seconds(expires_at - time.time())


def format_seconds(seconds: float) -> str:
    seconds = max(int(seconds), 0)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    return " ".join(parts)


def now_stamp() -> str:
    return time.strftime("%d/%m/%y %H:%M:%S")
