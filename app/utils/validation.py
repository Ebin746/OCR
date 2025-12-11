import re

def validate(fields):
    verified = {}

    for k, v in fields.items():
        val = v.strip()

        if "name" in k:
            verified[k] = re.sub(r"[^A-Za-z ]", "", val)

        elif "gender" in k:
            if "male" in val.lower(): verified[k] = "Male"
            elif "female" in val.lower(): verified[k] = "Female"
            else: verified[k] = val

        elif "birth" in k:
            verified[k] = val

        elif "phone" in k:
            digits = re.sub(r"\D", "", val)
            verified[k] = digits[-10:]

        elif "pin" in k:
            digits = re.sub(r"\D", "", val)
            verified[k] = digits[:6]

        else:
            verified[k] = val

    return verified
