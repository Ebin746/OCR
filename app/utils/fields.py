import re

def split_label_value(text):
    for sep in [":", "-", "=", "–"]:
        if sep in text:
            left, right = text.split(sep, 1)
            return left.strip(), right.strip()
    return None, text.strip()

def map_label(l):
    if not l: return None
    s = l.lower()

    if "first" in s: return "first_name"
    if "middle" in s: return "middle_name"
    if "last" in s: return "last_name"
    if "gender" in s: return "gender"
    if "birth" in s or "dob" in s: return "date_of_birth"
    if "address" in s and "1" in s: return "address_line_1"
    if "address" in s and "2" in s: return "address_line_2"
    if "city" in s: return "city"
    if "state" in s: return "state"
    if "pin" in s: return "postal_code"
    if "phone" in s or "mobile" in s: return "phone_number"
    if "email" in s: return "email"

    return None

def extract_fields(lines):
    fields = {}

    for line in lines:
        label, value = split_label_value(line)

        if not value:
            continue

        key = map_label(label)

        if key is None:
            if not label:
                key = f"field_{len(fields)+1}"
            else:
                key = label.lower().replace(" ", "_")

        fields[key] = value

    return fields
