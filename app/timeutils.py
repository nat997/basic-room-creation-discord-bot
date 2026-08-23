import re
from datetime import datetime, timedelta


def parse_time_input(text: str):
    now = datetime.now()
    text = text.lower().strip()

    if "mai" in text:
        m = re.search(r"(\d{1,2})[:h](\d{1,2})", text)
        if m:
            return datetime(now.year, now.month, now.day,
                            int(m.group(1)), int(m.group(2))) + timedelta(days=1)

    if "tối nay" in text:
        return datetime(now.year, now.month, now.day, 20, 0)

    if "pm" in text:
        try:
            hour = int(text.replace("pm", "").strip())
            return datetime(now.year, now.month, now.day, hour + 12, 0)
        except:
            pass

    if "tối" in text and "h" in text:
        try:
            hour = int(text.replace("h tối", "").strip())
            return datetime(now.year, now.month, now.day, hour, 0)
        except:
            pass

    m = re.search(r"(\d{1,2})[:h](\d{1,2})", text)
    if m:
        return datetime(now.year, now.month, now.day,
                        int(m.group(1)), int(m.group(2)))

    m = re.search(r"(\d{1,2})h", text)
    if m:
        return datetime(now.year, now.month, now.day, int(m.group(1)), 0)

    return None
