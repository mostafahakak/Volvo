import re
from urllib.parse import unquote


def parse_coord_loose(raw):
    if raw is None:
        return None
    s = str(raw).strip().replace("−", "-")
    if not s:
        return None
    m = re.search(r"[-+]?\d+(?:[.,]\d+)?", s)
    if m:
        s = m.group(0)
    if "," in s and "." not in s:
        s = s.replace(",", ".")
    try:
        return float(s.replace(" ", ""))
    except (TypeError, ValueError):
        return None


def _pair_is_valid(lat, lng):
    if lat is None or lng is None:
        return False
    if abs(lat) > 90 or abs(lng) > 180:
        return False
    if abs(lat) < 0.0001 and abs(lng) < 0.0001:
        return False
    return True


def lat_lng_from_maps_url(url):
    if not url:
        return None, None
    text = unquote(str(url).strip())

    def pair(a, b):
        lat = parse_coord_loose(a)
        lng = parse_coord_loose(b)
        if _pair_is_valid(lat, lng):
            return lat, lng
        return None, None

    m = re.search(r"@([-+]?\d+(?:[.,]\d+)?),([-+]?\d+(?:[.,]\d+)?)", text)
    if m:
        got = pair(m.group(1), m.group(2))
        if got[0] is not None:
            return got

    for pat in (
        r"[?&](?:q|query|ll|daddr)=([-+]?\d+(?:[.,]\d+)?)(?:%2C|,|\+)+([-+]?\d+(?:[.,]\d+)?)",
        r"!3d([-+]?\d+(?:[.,]\d+)?)!4d([-+]?\d+(?:[.,]\d+)?)",
    ):
        m = re.search(pat, text)
        if m:
            got = pair(m.group(1), m.group(2))
            if got[0] is not None:
                return got

    for m in re.finditer(r"([-+]?\d+(?:[.,]\d+)?)[,\s]+([-+]?\d+(?:[.,]\d+)?)", text):
        got = pair(m.group(1), m.group(2))
        if got[0] is not None:
            return got

    return None, None


def resolve_branch_lat_lng(branch):
    """Return (lat, lng) for a Branches row, using fields then maps_url."""
    lat = parse_coord_loose(getattr(branch, "latitude", None))
    lng = parse_coord_loose(getattr(branch, "langitude", None))

    if _pair_is_valid(lat, lng):
        return lat, lng

    if _pair_is_valid(lng, lat):
        return lng, lat

    from_url = lat_lng_from_maps_url(getattr(branch, "maps_url", None))
    if from_url[0] is not None:
        return from_url

    return None, None
