import json

with open("gstin_state_codes_india.json", "r") as f:
    raw = json.load(f)

GST_STATE_CODE_MAP = {}

def add(code, name):
    if code and name:
        GST_STATE_CODE_MAP[str(code).zfill(2)] = str(name)

# Case 1: Dict mapping
if isinstance(raw, dict):
    for k, v in raw.items():
        # "29": "Karnataka"
        if isinstance(v, str):
            add(k, v)
        # "states": [...]
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    add(
                        item.get("state_code") or item.get("code"),
                        item.get("state_name") or item.get("state")
                    )

# Case 2: List
elif isinstance(raw, list):
    for item in raw:
        if isinstance(item, dict):
            add(
                item.get("state_code") or item.get("code"),
                item.get("state_name") or item.get("state")
            )
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            add(item[0], item[1])

# Debug (keep for now)
print("GST_STATE_CODE_MAP sample keys:", list(GST_STATE_CODE_MAP.items())[:5])
print("GST_STATE_CODE_MAP type:", type(GST_STATE_CODE_MAP))
