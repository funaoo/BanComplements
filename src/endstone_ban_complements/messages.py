def render(template: str, staff: str = "", date: str = "", reason: str = "", time_left: str = "Never") -> str:
    return (
        template.replace("{STAFF}", staff)
        .replace("{DATE}", date)
        .replace("{REASON}", reason)
        .replace("{TIME}", time_left)
    )
