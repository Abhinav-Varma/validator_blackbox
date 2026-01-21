import json
with open("gstin_state_codes_india.json","r") as f:
    GST_STATE_CODE_MAP=json.load(f)

def GST_DETAILS_FOR(gst_numbers, all_records):
    """
    Extract PAN + State ONLY for requested GST numbers.
    Robust against JSONPath returning nested lists.
    """

    # ---- Normalize requested GST numbers ----
    if gst_numbers and isinstance(gst_numbers[0], list):
        gst_numbers = gst_numbers[0]

    requested = set(
        g for g in gst_numbers
        if isinstance(g, str)
    )

    # ---- Normalize GST records ----
    if all_records and isinstance(all_records[0], list):
        records = all_records[0]
    else:
        records = all_records

    output = []

    for record in records:
        if not isinstance(record, dict):
            continue

        gst = record.get("gst_number")
        if not isinstance(gst, str):
            continue

        if gst not in requested:
            continue

        state_code = gst[:2]          # string ✔
        pan = gst[2:12]               # string ✔
        state = GST_STATE_CODE_MAP.get(
            state_code,
            GST_STATE_CODE_MAP.get(int(state_code), "")
        )


        output.append({
            "gst_number": gst,
            "pan_number": pan,
            "state_name": state
        })

    return output

def CONCATENATE(a: str, b: str) -> str:
    return f"{a} {b}"


def CAPITALIZE(a: str) -> str:
    return a.capitalize()


def JOIN(*args: str) -> str:
    return "".join(args)


def SUBSTR(value: str, start: int, length: int) -> str:
    try:
        return value[start:start + length]
    except Exception:
        return ""


def GST_STATE_NAME(gstin: str) -> str:
    if not gstin or len(gstin) < 2:
        return ""
    state_code = gstin[:2]
    return GST_STATE_CODE_MAP.get(state_code, "")
