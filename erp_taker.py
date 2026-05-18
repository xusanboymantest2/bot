import re

passports = []

with open("message (3).txt", "r", encoding="utf-8") as f:
    for line in f:
        # find passport series + number
        match = re.search(r'([A-Z-]+)\s+(\d+)', line)

        if match:
            series = match.group(1)
            number = match.group(2)

            # first value in line = date
            raw_date = line.strip().split()[0]

            # convert M/D/YYYY -> DD.MM.YYYY
            if "/" in raw_date:
                m, d, y = raw_date.split("/")
                birthdate = f"{d.zfill(2)}.{m.zfill(2)}.{y}"
            else:
                birthdate = raw_date

            passports.append((birthdate, series, number))

print(passports)