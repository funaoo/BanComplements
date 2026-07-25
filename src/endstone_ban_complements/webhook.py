import json
import threading
import urllib.error
import urllib.request


def send_embed(url: str, title: str, fields: list[tuple[str, str]], logger=None) -> None:
    if not url:
        return

    payload = json.dumps(
        {
            "embeds": [
                {
                    "title": title,
                    "fields": [{"name": name, "value": str(value), "inline": True} for name, value in fields],
                }
            ]
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (BanComplements)"},
        method="POST",
    )

    def _dispatch() -> None:
        try:
            urllib.request.urlopen(request, timeout=5)
        except urllib.error.HTTPError as error:
            if logger is not None:
                logger.error(f"[BanComplements] Webhook HTTP {error.code}: {error.read().decode('utf-8', 'ignore')}")
        except Exception as error:
            if logger is not None:
                logger.error(f"[BanComplements] Webhook request failed: {error}")

    threading.Thread(target=_dispatch, daemon=True).start()
