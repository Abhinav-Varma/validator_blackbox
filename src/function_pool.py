import json

with open("gstin_state_codes_india.json", "r") as f:
    GST_STATE_CODE_MAP = json.load(f)


def CONCATENATE(a: str, b: str) -> str:
    return f"{a} {b}"


def CAPITALIZE(value: str) -> str:
    return value.capitalize()


def JOIN(*args: str) -> str:
    return "".join(args)


def GST_STATE_NAME(gstin: str) -> str:
    if not gstin or len(gstin) < 2:
        return ""
    return GST_STATE_CODE_MAP.get(gstin[:2], "")


def GST_DETAILS_ALL(records: list) -> list:
    output = []
    for r in records:
        gst = r.get("gst_number")
        if not gst or len(gst) < 12:
            continue

        output.append({
            "gst_number": gst,
            "pan_number": gst[2:12],
            "state_name": GST_STATE_CODE_MAP.get(gst[:2], "")
        })
    return output
