import re


def collapse_phone_whitespace(s):
    if not s:
        return ""
    return "".join(s.split())


def normalize_phone_e164(s):
    """
    Normalize to E.164 for storage and lookup.

    Egypt typo only: +2001282... (extra 0 right after country code 20) → +201282...
    Do NOT strip the 0 in valid +2010... / +2011... mobiles (e.g. +201011240268).
    """
    d = collapse_phone_whitespace(s)
    if d.startswith("+200") and len(d) > 4:
        d = "+20" + d[4:]
    return d


def repair_egypt_mobile_stripped_zero(mobile):
    """
    Undo bad normalization that stored +2011240268 instead of +201011240268.
    Returns the corrected E.164 string, or None if not applicable.
    """
    if not mobile or not re.fullmatch(r"\+201\d{7}", mobile):
        return None
    national = mobile[3:]
    if len(national) != 8 or not national.startswith("1"):
        return None
    candidate = "+20" + "10" + national
    if len(candidate) == 13:
        return candidate
    return None
