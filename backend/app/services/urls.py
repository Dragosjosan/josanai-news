from urllib.parse import urlsplit


def display_domain(url: str) -> str:
    host = urlsplit(url).hostname or ""
    return host.removeprefix("www.")
